---
name: slak
description: Read and write Slack from the command line as the user's own account - list channels, see what's unread, read channels/DMs/threads (paste a permalink), search messages, send messages and thread replies, find people, and watch every channel for keywords (飲料, 請客, nidin / Uber Eats group-order links). Use whenever the user wants to check, search, monitor, or post in Slack from a shell.
---

# slak

Zero-dependency Python CLI over the Slack Web API, acting as the user via the
Slack desktop app's session. Run `slak --help` for the full surface.

**Always pass `--json`** when parsing output. Envelope:

```json
{"ok": true, "data": ...}
{"ok": false, "error": {"message": "...", "code": 3, "detail": {...}}}
```

Exit codes: `0` ok · `1` error · `2` usage (unknown channel/user) · `3` auth · `4` network.
On exit `3` the desktop session itself is gone: ask the user to sign in to the
Slack desktop app, then run `slak login`. Do not retry.

## Auth

```bash
slak login                 # every workspace the desktop app is signed in to
slak login acme            # just one, by subdomain
```

`slak login` reads the desktop app's encrypted `d` cookie (key from GNOME
Keyring / libsecret on Linux, Keychain on macOS - macOS may show a one-time
"allow" prompt), mints an xoxc token from it, and saves both to
`~/.config/slak/tokens/<TEAM>.json` (0600). Expired tokens are re-minted from
the cookie automatically. On macOS `slak login` must run in a local Terminal:
Keychain can't prompt over SSH, so there it exits `3` and so does re-minting.
Needs `openssl` on PATH; `secret-tool` on Linux.
Windows and KWallet are not supported - tokens saved by
[slk](https://github.com/gammons/slk) in `~/.local/share/slk/tokens/` are read
as a fallback there.

With several workspaces, pick one with `--workspace <team id, name or domain>`.
`SLACK_TOKEN` + `SLACK_COOKIE` env vars override everything.

Never print the token or cookie. Never ask the user to paste them into chat.

## Reading

```bash
slak whoami
slak unread --json                 # conversations with unreads, mention counts first
slak channels [filter]             # everything you're in: public/private/mpim/im
slak read random -n 30             # channel by name, '#name', id, or '@user' for a DM
slak read <permalink>              # a message link opens its thread
slak thread <permalink>            # or: slak thread <channel> <ts>
slak search '"關鍵字" in:#random after:2026-10-01' -n 20
slak users erica                   # cached; --refresh after new hires
```

Messages come back oldest-first as `{ts, time, user, text, replies?, thread_ts?, files?}`.
Mentions, channel links and URLs are already resolved to plain text.

## Writing — real people read these

```bash
slak send random "text"
slak send @alice "text"                    # opens/uses the DM
slak send random "text" --thread <ts|permalink>
echo "multi-line" | slak send random -
```

Returns `{channel, ts, permalink}`. **Confirm the recipient and the text with
the user before sending.** There is no unsend from this CLI.

## Keyword watch

```bash
slak watch --once --json                   # default keywords, last 1 day, new hits only
slak watch -k 飲料 -k nidin.shop --since 2 --once
slak watch --interval 300                  # foreground loop, one line per new hit
```

One `search.messages` per keyword, so it covers every channel without walking
history. Hits already reported are remembered in `~/.config/slak/seen-<TEAM>.json`,
so `--once` from a systemd timer or cron only ever prints new ones. Delete that
file to replay the window. Your own messages are dropped; the rest of the filter
lives in `worth_alerting()` in the script.

## Gotchas

- Slack search segments CJK and fuzzily matches single characters. `watch`
  quotes each keyword and then re-checks the literal text. Quote CJK terms in
  `slak search` yourself.
- 請客 also matches 請客戶 ("please ask the customer"), which is very common in
  work channels.
- Uber Eats group orders appear as both `ubereats.com` and `eats.uber.com`.
- Search results lag real time by a few seconds to a minute.
