---
name: slak
description: Read and write Slack from the command line as the user's own account - unread overview, read channels/DMs/threads (paste a permalink), search, mentions, send / schedule / edit / delete / react, upload and download files, mark read, set status and do-not-disturb, export a channel to Markdown, and watch every channel for keywords (飲料, 請客, nidin / Uber Eats group-order links). Use whenever the user wants to check, search, monitor, or act in Slack from a shell.
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
slak mentions -n 20                # messages that @-mention the user
slak users erica                   # cached; --refresh after new hires
slak download <permalink> -o DIR   # files attached to a message (never overwrites)
slak export random --since 7 --threads   # Markdown transcript; --json for records
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
the user before sending.** Keep the returned permalink: it is how you edit,
react to or delete that message afterwards.

```bash
slak send random "text" --at 09:00          # schedule: +30m, 09:00 (next), 'YYYY-MM-DD HH:MM'
slak scheduled [channel]                    # pending scheduled messages, with ids
slak scheduled --cancel <id>
slak edit <permalink> "new text"            # your own messages only
slak delete <permalink> [--files]           # --files also removes attached uploads
slak react <permalink> plus1 [--remove]
slak upload random a.png b.pdf -m "caption" [--thread <ts|permalink>]
slak mark random                            # mark read up to the latest message
slak status :bento: 午餐中 --for 1h          # or: slak status / slak status --clear
slak dnd 30m                                # snooze notifications; `slak dnd off`; `slak dnd`
```

Any message-targeting command also takes `<channel> --ts <ts>` instead of a permalink.

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

A hit with a nidin group link (`order.nidin.shop/gb/menu/...`) gets a `nidin`
field: brand, store, opener, `store_id`, `group_buying_status` (20 = closed).
The data comes from nidin's public brief endpoint, so no nidin login is needed.
To see the menu or join, hand the link to the `nidin` CLI:
`nidin group peek <link>`, `nidin group join <link> <product_id>`, and, after
the user confirms, `nidin group send <order_id> --yes`.

## Gotchas

- Scheduling goes through Slack's draft API (`chat.scheduleMessage` rejects
  session tokens), so scheduled text is sent literally: `*bold*` and `<@U…>`
  are not rendered.
- `chat.delete` leaves uploaded files behind; use `delete --files` when cleaning up.

- Slack search segments CJK and fuzzily matches single characters. `watch`
  quotes each keyword and then re-checks the literal text. Quote CJK terms in
  `slak search` yourself.
- 請客 also matches 請客戶 ("please ask the customer"), which is very common in
  work channels.
- Uber Eats group orders appear as both `ubereats.com` and `eats.uber.com`.
- Search results lag real time by a few seconds to a minute.
