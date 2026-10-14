# slak

Slack from the shell, as yourself. Zero dependencies (Python 3.8+ stdlib).

Auth comes from the Slack desktop app: `slak login` decrypts its session cookie
and mints a token from it, the way [slk](https://github.com/gammons/slk) does.
No Slack App, no OAuth, no admin approval, no tokens to paste. Linux and macOS;
needs `openssl` (and `secret-tool` on Linux).

```bash
ln -s "$PWD/slak" ~/.local/bin/slak
slak login
slak whoami
slak unread
slak read random
slak search '"飲料"'
slak send @alice "hi"
slak watch --once          # new messages mentioning 飲料/請客/nidin/Uber Eats links
```

Every command takes `--json`. See [SKILL.md](SKILL.md) for the full surface,
exit codes, and gotchas. Tests: `python3 test_parse.py`.
