# BOFH IRC bot

IRC-only version of the Sysarmy BOFH bot. It listens to every `PRIVMSG`, runs commands only when the message starts with `!`, and retains text karma (`word++` and `word--`) using the existing `db/karma.db` schema.

Discord-only slash commands, reactions, member synchronization, embeds, job forum operations, and Discord RSS publishing are intentionally excluded.

## Run with Docker Compose

1. Copy `.env.example` to `.env` and configure the IRC connection.
2. Copy the existing `karma.db` and, optionally, `quotes.db` into `db/`.
3. Start the bot:

   ```sh
   docker compose up --build -d
   docker compose logs -f bot
   ```

The complete `db/` directory is mounted at `/app/db`; SQLite updates persist on the host. If a database is absent, the bot creates a compatible empty one.
`main.py` and `src/` are also mounted read-only, so after pulling code changes only restart the bot:

```sh
git pull
docker compose restart bot
```

Rebuild with `docker compose up --build -d` only when `requirements.txt` or the Dockerfile changes.
On Linux, set `PUID` and `PGID` in `.env` to the owner of the `db/` directory so SQLite remains writable.

To join multiple channels, list them comma-separated in `.env`:

```dotenv
IRC_CHANNELS="#sysarmy,#sysarmy-offtopic,#jobs"
```

The bot joins every listed channel and replies in the channel where each command was received.

## Libera.Chat operation

Use TLS and SASL, register a separate account for the bot, and set `IRC_REALNAME` so the
bot is clearly identified and an administrator can be contacted. Obtain permission from
the operators of every configured channel before adding it to `IRC_CHANNELS`.

The client answers server pings independently of slow command APIs, probes silent
connections, reconnects with exponential backoff and jitter, and rejoins the configured
channels after a connection loss. It deliberately does not immediately rejoin after a
channel operator kicks it. Outbound messages are serialized at one every 2.1 seconds to
stay within Libera.Chat's normal message rate.

## Identity and karma

When the server supports IRCv3 `account-tag`, the authenticated account name is recorded as the karma giver. Otherwise the bot falls back to the current nickname. SASL is therefore recommended.

Do not run this bot with the same nickname as a connected Matterbridge instance: IRC nicknames must be unique. Many networks allow the same NickServ/SASL account to have multiple concurrent connections with distinct nicknames, but this depends on network policy.

Matterbridge messages in the form `<username> !command` are supported when they come from a configured bridge nickname. `IRC_BRIDGE_NICKS` is a comma-separated list and defaults to `nbot`; the relayed username is used as the command and karma identity.

## Yelling channel

`IRC_YELLING_CHANNELS` is a comma-separated list that defaults to `#sysarmy-yelling`. Messages containing lowercase words receive a random all-caps reminder. URLs and `:emoji:` tokens are ignored. Matterbridge messages are checked after extracting their Discord or Slack username and content.

## Commands

Run `!help` for the current list. The migrated commands are `birras`, `caucho`, `clima`, `cripto`, `dolar`, `euro`, country holiday commands, `fulbo`, karma/ranking commands, peso conversion, quotes, `subte`, `underground`, and the small utility commands.
