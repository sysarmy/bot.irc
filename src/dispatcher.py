import logging
from dataclasses import dataclass

from src.commands.ctxbirras import birrasfunctx
from src.commands.ctxcaucho import cauchofunctx
from src.commands.ctxclima import climafunctx
from src.commands.ctxcripto import criptofunctx
from src.commands.ctxdolar import dolarfunctx
from src.commands.ctxeuro import eurofunctx
from src.commands.ctxferiadoar import feriadoarfunctx
from src.commands.ctxferiadocl import feriadoclfunctx
from src.commands.ctxferiadoes import feriadoesfunctx
from src.commands.ctxferiadomx import feriadomxfunctx
from src.commands.ctxferiadouy import feriadouyfunctx
from src.commands.ctxfulbo import fulbofunctx
from src.commands.ctxkarma import karmagiversfunctx, karmagiversuserfunctx, karmarankfunctx, karmawordfunctx
from src.commands.ctxpesos import pesosfunctx
from src.commands.ctxquote import qsearchfunctx, quoteaddfunctx, quotefunctx
from src.commands.ctxsubte import subtefunctx
from src.commands.ctxunderground import undergroundfunctx
from src.help import help_message, missing_argument_message


LOGGER = logging.getLogger(__name__)


@dataclass
class CommandContext:
    author: str
    target: str
    client: object

    async def send(self, message: str) -> None:
        await self.client.send_message(self.target, str(message))


COMMANDS = {
    "birras": (birrasfunctx, 0), "caucho": (cauchofunctx, 0),
    "clima": (climafunctx, 1), "cripto": (criptofunctx, 0),
    "dolar": (dolarfunctx, -1), "dolor": (dolarfunctx, -1), "euro": (eurofunctx, 0),
    "feriadoar": (feriadoarfunctx, 0), "feriadocl": (feriadoclfunctx, 0),
    "feriadoes": (feriadoesfunctx, 0), "feriadomx": (feriadomxfunctx, 0),
    "feriadouy": (feriadouyfunctx, 0), "fulbo": (fulbofunctx, 1),
    "rank": (karmarankfunctx, 0), "karma": (karmawordfunctx, 1),
    "kgivers": (karmagiversfunctx, 0), "kgiven": (karmagiversuserfunctx, 1),
    "pesos": (pesosfunctx, 1), "q": (quotefunctx, 0),
    "qadd": (quoteaddfunctx, 1), "qsearch": (qsearchfunctx, 1),
    "subte": (subtefunctx, 0), "underground": (undergroundfunctx, 0),
}


async def dispatch(ctx: CommandContext, content: str) -> None:
    if not content.startswith("!"):
        return
    command_line = content[1:].strip()
    if not command_line:
        return
    command, _, argument = command_line.partition(" ")
    command = command.lower()

    if command == "help":
        await ctx.send(help_message(argument))
        return
    if command == "ping":
        await ctx.send("Pong!")
        return
    if command == "flip":
        await ctx.send("`(╯°□°）╯︵ ┻━┻`")
        return
    if command == "shrug":
        await ctx.send("`¯\\_(\ツ)_/¯`")
        return

    definition = COMMANDS.get(command)
    if not definition:
        await ctx.send(f"Comando inexistente: {command}")
        return
    handler, required_args = definition
    if required_args == 1 and not argument:
        await ctx.send(missing_argument_message(command))
        return

    try:
        if command == "pesos":
            await handler(ctx, int(argument))
        elif required_args == 0:
            await handler(ctx)
        elif required_args == -1:
            await handler(ctx, argument or None)
        else:
            await handler(ctx, argument)
    except Exception:
        LOGGER.exception("Command failed: %s", command)
        await ctx.send(f"Error ejecutando !{command}")
