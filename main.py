import asyncio
import base64
import logging
import os
import random
import ssl
import time

from dotenv import load_dotenv

from src.bridge import message_identity
from src.database import initialize_databases
from src.dispatcher import CommandContext, dispatch
from src.karma import process_karma
from src.text import ascii_message
from src.yelling import has_lowercase_word, random_response

load_dotenv()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
LOGGER = logging.getLogger("bofh-irc")


def env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


class IRCBot:
    def __init__(self) -> None:
        self.host = os.environ["IRC_HOST"]
        self.tls = env_bool("IRC_TLS", True)
        self.port = int(os.getenv("IRC_PORT", "6697" if self.tls else "6667"))
        self.nickname = os.environ["IRC_NICK"]
        self.username = os.getenv("IRC_USERNAME", self.nickname)
        self.realname = os.getenv("IRC_REALNAME", "Sysarmy BOFH IRC bot")
        self.channels = [item.strip() for item in os.environ["IRC_CHANNELS"].split(",") if item.strip()]
        self.bridge_nicks = {item.strip().lower() for item in os.getenv("IRC_BRIDGE_NICKS", "nbot").split(",") if item.strip()}
        self.yelling_channels = {item.strip().lower() for item in os.getenv("IRC_YELLING_CHANNELS", "#sysarmy-yelling").split(",") if item.strip()}
        self.server_password = os.getenv("IRC_SERVER_PASSWORD")
        self.sasl_username = os.getenv("IRC_SASL_USERNAME")
        self.sasl_password = os.getenv("IRC_SASL_PASSWORD")
        if bool(self.sasl_username) != bool(self.sasl_password):
            raise ValueError("IRC_SASL_USERNAME and IRC_SASL_PASSWORD must be set together")
        self.writer = None
        self.send_lock = asyncio.Lock()
        self.last_message_sent = 0.0
        self.registered = False
        self.connected_at = None
        self.message_tasks: set[asyncio.Task] = set()

    async def raw(self, line: str) -> None:
        if not self.writer:
            return
        LOGGER.debug(">> %s", line.split("AUTHENTICATE ", 1)[0] if line.startswith("AUTHENTICATE ") else line)
        self.writer.write((line + "\r\n").encode("utf-8"))
        await self.writer.drain()

    async def send_message(self, target: str, message: str, ascii_only: bool = True) -> None:
        # Keep ample room for IRC command/target overhead within the 512-byte limit.
        if ascii_only:
            message = ascii_message(message)
        chunks = []
        for logical_line in message.replace("\r", "").split("\n"):
            current = ""
            for word in logical_line.split(" "):
                candidate = word if not current else f"{current} {word}"
                if len(candidate.encode("utf-8")) <= 380:
                    current = candidate
                else:
                    if current:
                        chunks.append(current)
                    current = word
            if current:
                chunks.append(current)
        async with self.send_lock:
            for chunk in chunks:
                # Libera.Chat's normal message limit is one message every two seconds.
                wait = 2.1 - (time.monotonic() - self.last_message_sent)
                if wait > 0:
                    await asyncio.sleep(wait)
                await self.raw(f"PRIVMSG {target} :{chunk}")
                self.last_message_sent = time.monotonic()

    async def register(self) -> None:
        if self.server_password:
            await self.raw(f"PASS {self.server_password}")
        if self.sasl_username and self.sasl_password:
            await self.raw("CAP REQ :sasl")
        else:
            await self.raw("CAP REQ :account-tag")
        await self.raw(f"NICK {self.nickname}")
        await self.raw(f"USER {self.username} 0 * :{self.realname}")

    async def handle_line(self, line: str) -> None:
        tags = {}
        if line.startswith("@"):
            raw_tags, line = line[1:].split(" ", 1)
            tags = dict(tag.split("=", 1) if "=" in tag else (tag, "") for tag in raw_tags.split(";"))
        prefix = ""
        if line.startswith(":"):
            prefix, line = line[1:].split(" ", 1)
        command, _, rest = line.partition(" ")

        if command == "PING":
            await self.raw(f"PONG {rest}")
        elif command == "CAP" and " ACK " in f" {rest} ":
            if self.sasl_username and "sasl" in rest:
                await self.raw("AUTHENTICATE PLAIN")
            else:
                await self.raw("CAP END")
        elif command == "CAP" and " NAK " in f" {rest} ":
            if self.sasl_username and "sasl" in rest:
                raise RuntimeError(f"IRC server rejected required SASL capability: {rest}")
            await self.raw("CAP END")
        elif command == "AUTHENTICATE" and rest == "+":
            auth = f"{self.sasl_username}\0{self.sasl_username}\0{self.sasl_password}"
            await self.raw("AUTHENTICATE " + base64.b64encode(auth.encode()).decode())
        elif command == "903":
            # Authentication is complete; account-tag is optional but gives stable karma identities.
            await self.raw("CAP REQ :account-tag")
        elif command in {"904", "905", "906", "907"}:
            raise RuntimeError(f"SASL authentication failed: {rest}")
        elif command == "001":
            self.registered = True
            self.connected_at = time.monotonic()
            for channel in self.channels:
                await self.raw(f"JOIN {channel}")
            LOGGER.info("Connected to %s:%s as %s; joined %s", self.host, self.port, self.nickname, ", ".join(self.channels))
        elif command == "433":
            raise RuntimeError(f"IRC nickname {self.nickname!r} is already in use")
        elif command == "KICK":
            channel, _, kicked = rest.partition(" ")
            kicked = kicked.partition(" ")[0]
            if kicked.lower() == self.nickname.lower():
                # Do not fight an operator's decision by automatically rejoining.
                LOGGER.warning("Kicked from %s; not rejoining until the next IRC connection", channel)
        elif command == "PRIVMSG":
            task = asyncio.create_task(self.process_privmsg(tags, prefix, rest))
            self.message_tasks.add(task)
            task.add_done_callback(self.message_tasks.discard)

    async def process_privmsg(self, tags: dict[str, str], prefix: str, rest: str) -> None:
        """Process commands separately so slow HTTP APIs cannot delay IRC PONGs."""
        try:
            target, separator, content = rest.partition(" :")
            if not separator:
                return
            nick = prefix.split("!", 1)[0]
            if nick.lower() == self.nickname.lower():
                return
            account = tags.get("account")
            identity = account if account and account != "*" else nick
            identity, content = message_identity(nick, identity, content, self.bridge_nicks)
            response_target = nick if target.lower() == self.nickname.lower() else target
            ctx = CommandContext(author=identity, target=response_target, client=self)
            if target.lower() in self.yelling_channels and has_lowercase_word(content):
                await ctx.send(f"{identity}: {random_response()}")
            for reply in process_karma(content, identity):
                await ctx.send(reply)
            await dispatch(ctx, content)
        except Exception:
            LOGGER.exception("Unhandled error while processing PRIVMSG")

    async def connect_once(self) -> None:
        self.registered = False
        self.connected_at = None
        ssl_context = ssl.create_default_context() if self.tls else None
        reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=ssl_context)
        await self.register()
        probing = False
        while True:
            try:
                line_bytes = await asyncio.wait_for(reader.readline(), timeout=60 if probing else 240)
            except asyncio.TimeoutError:
                if probing:
                    raise ConnectionError("IRC connection did not answer a keepalive probe")
                await self.raw(f"PING :bofh-{int(time.time())}")
                probing = True
                continue
            if not line_bytes:
                break
            probing = False
            line = line_bytes.decode("utf-8", errors="replace").rstrip("\r\n")
            LOGGER.debug("<< %s", line)
            await self.handle_line(line)
        raise ConnectionError("IRC server closed the connection")

    async def run(self) -> None:
        delay = 2
        while True:
            try:
                await self.connect_once()
            except asyncio.CancelledError:
                raise
            except Exception:
                if self.connected_at and time.monotonic() - self.connected_at >= 300:
                    delay = 2
                retry_in = delay + random.uniform(0, min(delay * 0.25, 10))
                LOGGER.exception("IRC connection failed; retrying in %.1fs", retry_in)
                await asyncio.sleep(retry_in)
                delay = min(delay * 2, 300)
            finally:
                if self.writer:
                    self.writer.close()
                    try:
                        await self.writer.wait_closed()
                    except (ConnectionError, OSError):
                        pass
                    self.writer = None


async def async_main() -> None:
    initialize_databases()
    await IRCBot().run()


if __name__ == "__main__":
    asyncio.run(async_main())
