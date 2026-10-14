# slak

[English](#english) · [繁體中文](#繁體中文)

## English

Slack from the shell, as yourself. Read channels, DMs and threads, see what's
unread, search, post, and watch every channel for keywords, all without
opening the Slack window.

Zero dependencies. Python 3.8+. Single file. Linux and macOS.

> **Unofficial.** Not affiliated with or endorsed by Slack. slak reuses the
> session of the Slack desktop app you are already signed in to, the same way
> [slk](https://github.com/gammons/slk) does. It acts as **you**: messages it
> sends are indistinguishable from ones you type. Your workspace's policies may
> not allow automated clients. Check them first, and use it at human request rates.

### Features

- **No setup on Slack's side.** No Slack App, no OAuth, no admin approval, no
  tokens to copy. `slak login` takes the session from the desktop app.
- **Self-healing auth.** When the token expires, slak mints a new one from the
  desktop cookie and retries.
- **Read everything you're in.** Public and private channels, DMs, group DMs.
  Paste a message link to open its thread.
- **Unread overview.** Conversations with unread messages, mentions first.
- **Search** with full Slack syntax (`in:#channel`, `from:@user`, `after:`…).
- **Post** to a channel, a DM (`@user`), or a thread reply. Schedule it for
  later, then list or cancel it.
- **Follow up on messages:** edit, delete (optionally with their uploads), react.
- **Files:** upload to a channel, DM or thread; download a message's attachments.
- **Mentions** across all channels, and **mark read** when you're done.
- **Status and Do Not Disturb:** set a status with auto-expiry, snooze notifications.
- **Export** a channel (with threads) to Markdown or JSON, ready to hand to an LLM.
- **Keyword watch.** Scans every channel for keywords and reports only messages
  it hasn't shown before. Run it as a one-off from cron or as a foreground loop.
- **Agent-ready.** Every command takes `--json` with a stable envelope and exit
  codes. [SKILL.md](SKILL.md) is a drop-in skill for Claude Code and other agents.
- Mentions, channel links and URLs come back as plain text. CJK-aware tables.

### Install

```bash
git clone https://github.com/Unayung/slak-cli && cd slak-cli
ln -s "$PWD/slak" ~/.local/bin/slak
```

Needs `openssl` on PATH, plus `secret-tool` (libsecret) on Linux.

### Quick start

```bash
slak login                       # every workspace the desktop app is signed in to
slak whoami
slak unread
slak channels dev                # filter by name
slak read random -n 30           # #name, channel id, @user, or a message link
slak thread <message link>
slak search '"release notes" in:#dev after:2026-10-01'
slak users alice
slak send random "hello"
slak send @alice "got a sec?"
slak send random "on it" --thread <ts or message link>
echo "multi-line" | slak send random -

slak send random "standup in 5" --at 09:55     # also +30m, 'YYYY-MM-DD HH:MM'
slak scheduled                                 # list; --cancel <id>
slak edit <message link> "fixed typo"
slak delete <message link> --files
slak react <message link> eyes
slak upload random report.pdf -m "Q3 numbers"
slak download <message link> -o ~/Downloads
slak mentions
slak mark random
slak status :bento: lunch --for 1h             # --clear to remove
slak dnd 30m                                   # dnd off / dnd to check
slak export random --since 7 --threads > random.md
```

Commands that target one message take a message link, or `<channel> --ts <ts>`.

### Keyword watch

```bash
slak watch --once                          # default keywords, last day, new hits only
slak watch -k deploy -k outage --since 2 --once --json
slak watch --interval 300                  # keep polling, one line per new hit
```

Each keyword is one `search.messages` call, so it covers every channel without
walking channel history. Messages already reported are remembered in
`~/.config/slak/seen-<TEAM>.json`. Delete that file to replay the window. Your
own messages are skipped. Edit `worth_alerting()` in the script for more filtering.

Hits with a nidin group link also show the store and who opened the group,
read from nidin's public group summary. With
[nidin-cli](https://github.com/Unayung/nidin-cli) installed, the printed
`nidin group peek <link>` shows the menu and `nidin group join` orders from it.

### For scripts and agents

```json
{"ok": true, "data": ...}
{"ok": false, "error": {"message": "...", "code": 3, "detail": {...}}}
```

Exit codes: `0` ok · `1` error · `2` usage · `3` auth · `4` network.

### How auth works

The desktop app keeps its session in a `d` cookie, AES-encrypted in its
Chromium cookie store. The key lives in the OS keyring: GNOME Keyring /
libsecret on Linux, Keychain on macOS, which may show a one-time "allow"
prompt. `slak login` decrypts the cookie with `openssl` and loads the workspace
page with it to get an `xoxc` token. Both are saved to
`~/.config/slak/tokens/<TEAM>.json` with mode 0600.

On macOS, run `slak login` in a local Terminal. Keychain cannot show its
"allow" prompt over SSH. Saved tokens keep working over SSH, but re-minting
an expired token there fails until you log in locally again.

Not supported: Windows and KWallet. On those, tokens that
[slk](https://github.com/gammons/slk) saved in `~/.local/share/slk/tokens/`
are picked up instead. `SLACK_TOKEN` + `SLACK_COOKIE` env vars override
everything.

Tests: `python3 test_parse.py`

---

## 繁體中文

用自己的 Slack 帳號在終端機操作 Slack。讀頻道、私訊和 thread，看未讀，搜尋，發訊息，監看所有頻道的關鍵字，都不用打開 Slack 視窗。

不需要裝任何套件。Python 3.8 以上，單一檔案，支援 Linux 和 macOS。

> **非官方工具。** 與 Slack 無關，也未經 Slack 認可。slak 沿用你在 Slack 桌面版已經登入的狀態，做法和 [slk](https://github.com/gammons/slk) 相同。它就是**你本人**，透過它送出的訊息跟你親手打的看不出差別。你的 workspace 可能不允許自動化程式，使用前請先確認公司規範，請求頻率也請維持在一般人的程度。

### 功能

- **Slack 那邊不用做任何設定**：不用建 Slack App、不用 OAuth、不用找管理員核准，也不用自己複製 token。`slak login` 會直接從桌面版拿登入狀態。
- **token 過期會自動更新**：用桌面版的 cookie 重新換一個 token，再重試一次。
- **你加入的對話都讀得到**：公開與私人頻道、私訊、群組私訊。直接貼訊息連結就能打開整串 thread。
- **未讀總覽**：列出有未讀的對話，被 tag 的排在最前面。
- **搜尋**：支援完整的 Slack 搜尋語法（`in:#頻道`、`from:@人`、`after:` 等）。
- **發訊息**：可以發到頻道、私訊（`@人`）或回覆在 thread 裡。也能排程稍後送出，並列出或取消排程。
- **處理已送出的訊息**：編輯、刪除（可以連附件一起刪）、加表情回應。
- **檔案**：上傳到頻道、私訊或 thread，下載訊息裡的附件。
- **被 tag 的訊息**：跨所有頻道列出，看完可以把頻道標成已讀。
- **狀態與勿擾**：設定會自動到期的狀態，暫停通知一段時間。
- **匯出**：把頻道（含 thread）匯出成 Markdown 或 JSON，可以直接交給 LLM 摘要。
- **關鍵字監看**：掃描所有頻道，只回報還沒報過的新訊息。可以交給 cron 定時跑，也可以在前景持續輪詢。預設關鍵字是「飲料」「請客」和你訂、Uber Eats 的團購連結。
- **方便給 agent 用**：每個指令都能加 `--json`，輸出格式和 exit code 固定。[SKILL.md](SKILL.md) 可以直接裝成 Claude Code 等 agent 的 skill。
- 輸出裡的 tag、頻道連結和網址都轉成純文字，表格會照中文字寬對齊。

### 安裝

```bash
git clone https://github.com/Unayung/slak-cli && cd slak-cli
ln -s "$PWD/slak" ~/.local/bin/slak
```

需要 `openssl`；Linux 另外需要 `secret-tool`（libsecret）。

### 快速上手

```bash
slak login                       # 登入桌面版上所有已登入的 workspace
slak whoami
slak unread                      # 未讀總覽
slak channels dev                # 依名稱篩選
slak read random -n 30           # 頻道名、頻道 ID、@人，或訊息連結
slak thread <訊息連結>
slak search '"飲料" in:#random after:2026-10-01'
slak users alice
slak send random "大家好"
slak send @alice "有空嗎？"
slak send random "收到" --thread <ts 或訊息連結>
echo "多行內容" | slak send random -

slak send random "5 分鐘後站會" --at 09:55    # 也可以用 +30m 或 'YYYY-MM-DD HH:MM'
slak scheduled                                 # 列出排程；--cancel <id> 取消
slak edit <訊息連結> "修正錯字"
slak delete <訊息連結> --files
slak react <訊息連結> eyes
slak upload random report.pdf -m "Q3 數字"
slak download <訊息連結> -o ~/Downloads
slak mentions
slak mark random
slak status :bento: 午餐中 --for 1h            # --clear 清除
slak dnd 30m                                   # dnd off 關閉；dnd 查看
slak export random --since 7 --threads > random.md
```

針對單一訊息的指令可以用訊息連結，也可以用 `<頻道> --ts <ts>` 指定。

排程訊息走的是 Slack 的草稿 API（官方排程 API 不接受這種登入方式），所以排程的文字會原樣送出，`*粗體*` 和 `<@U…>` 不會被轉換。

搜尋中文時請把關鍵字加上引號，例如 `'"請客"'`。不加的話，Slack 會把中文拆成單字做模糊比對，結果裡會混進很多不相干的訊息。

### 關鍵字監看

```bash
slak watch --once                          # 預設關鍵字、最近一天、只列新的
slak watch -k 飲料 -k nidin.shop --since 2 --once --json
slak watch --interval 300                  # 每 5 分鐘查一次，有新訊息就印一行
```

每個關鍵字只打一次搜尋 API，所以頻道再多也不會一個個翻歷史訊息。已經回報過的訊息記在 `~/.config/slak/seen-<TEAM>.json`，刪掉這個檔就會重新回報觀察期間內的訊息。你自己發的訊息會被略過，其他過濾條件可以改程式裡的 `worth_alerting()`。

抓到你訂團購連結時，會另外顯示是哪家店、誰開的團，資料來自你訂公開的團購摘要，不用登入你訂。有裝 [nidin-cli](https://github.com/Unayung/nidin-cli) 的話，照著印出來的 `nidin group peek <連結>` 就能看菜單，用 `nidin group join` 可以直接跟團點餐。

Uber Eats 的團購連結有 `ubereats.com` 和 `eats.uber.com` 兩種網域，兩個都已經放進預設關鍵字。

### 給腳本與 agent 使用

```json
{"ok": true, "data": ...}
{"ok": false, "error": {"message": "...", "code": 3, "detail": {...}}}
```

Exit code：`0` 成功 · `1` 錯誤 · `2` 用法錯誤 · `3` 登入失效 · `4` 網路問題。

### 登入原理

桌面版把登入狀態存在名為 `d` 的 cookie 裡，這個 cookie 經過 AES 加密，放在 Chromium 的 cookie 資料庫。金鑰存在作業系統的 keyring：Linux 是 GNOME Keyring 或 libsecret，macOS 是鑰匙圈，第一次讀取時可能會跳出「允許」的確認視窗。`slak login` 用 `openssl` 解開 cookie，再帶著它打開 workspace 頁面拿到 `xoxc` token。兩者都存在 `~/.config/slak/tokens/<TEAM>.json`，權限 0600。

macOS 上請在本機的終端機執行 `slak login`，透過 SSH 執行時鑰匙圈無法跳出「允許」視窗。登入後，透過 SSH 照常可以使用存好的 token，但 token 過期時無法在 SSH 下自動更新，要回到本機重新登入一次。

Windows 和 KWallet 目前不支援。在這兩種環境下，如果裝過 [slk](https://github.com/gammons/slk)，slak 會改讀它存在 `~/.local/share/slk/tokens/` 的 token。設定 `SLACK_TOKEN` 和 `SLACK_COOKIE` 環境變數的話，會優先使用環境變數。

測試：`python3 test_parse.py`
