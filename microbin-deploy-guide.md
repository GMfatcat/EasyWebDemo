# MicroBin 本地部署完整指南

## 目錄

1. [什麼是 MicroBin](#什麼是-microbin)
2. [模式說明](#模式說明)
3. [下載 Binary](#下載-binary)
4. [部署方式 A：直接執行](#部署方式-a直接執行)
5. [部署方式 B：Systemd 常駐服務](#部署方式-b-systemd-常駐服務)
6. [部署方式 C：Docker](#部署方式-c-docker)
7. [完整參數對照表](#完整參數對照表)

---

## 什麼是 MicroBin

MicroBin 是一個輕量的自架 Pastebin 服務，以 Rust 撰寫，單一執行檔即可運作，無需資料庫，適合在內部區域網路快速部署。

**主要特色：**
- 單一 binary，零依賴
- 語法高亮
- 閱後即焚 / 過期時間
- 密碼保護
- 內建短網址功能
- 檔案上傳支援

---

## 模式說明

### 一般模式（預設）

預設狀態，任何人可以新增、瀏覽貼文。適合小型內部團隊，信任所有使用者的環境。

```bash
./microbin --port 3009 --bind 0.0.0.0
```

---

### `--readonly` 唯讀模式

**開啟後：只能瀏覽，不能新增或刪除貼文。**

適合情境：想把 MicroBin 當作一個唯讀的公告板，由管理員事先建立內容，其他人只能查看。

```bash
./microbin --readonly
```

> ⚠️ 如果同時設定了 `--admin-username` 和 `--admin-password`，管理員登入後仍可以新增和管理貼文。

---

### `--private` 私密模式

**開啟後：貼文列表不公開，只有知道連結的人才能查看內容。**

適合情境：不想讓所有人看到所有貼文的列表，每則貼文只有持有連結的人能存取。

```bash
./microbin --private
```

> 與 `--readonly` 的差異：`--private` 不影響新增功能，只是隱藏列表頁面。

---

### `--editable` 可編輯模式

**開啟後：貼文建立後可以再次修改內容。**

預設貼文建立後無法修改，開啟此選項後，建立者可以回到貼文頁面編輯內容。

```bash
./microbin --editable
```

---

### `--encryption-client-side` 客戶端加密模式

**開啟後：內容在瀏覽器端加密，伺服器只儲存密文。**

加密金鑰會附在網址的 `#fragment` 部分，伺服器本身無法解讀內容。

```bash
./microbin --encryption-client-side
```

> ⚠️ 注意事項：
> - 開啟後**語法高亮失效**（伺服器看不到原始內容）
> - **搜尋功能失效**
> - **Raw 連結 / curl 取用失效**
> - 網址會變得較長
>
> 區域網路內部使用建議**不開啟**，除非有存放機敏資料（API Key、密碼等）的需求。

---

### `--highlightsyntax` 語法高亮模式

**開啟後：根據檔案類型或語言自動套用語法顏色。**

```bash
./microbin --highlightsyntax
```

> 與 `--encryption-client-side` 不相容，二選一。

---

### 管理員模式

設定管理員帳號後，登入管理員可以查看所有貼文、刪除任意內容。

```bash
./microbin --admin-username admin --admin-password yourpassword
```

管理員登入網址：`http://你的IP:PORT/admin`

---

## 下載 Binary

> 在有網路的機器上下載，再將檔案傳入內網機器。

前往 GitHub Releases 頁面下載對應平台的版本：

```
https://github.com/szabodanika/microbin/releases/latest
```

### Linux x86_64（最常見）

```bash
wget https://github.com/szabodanika/microbin/releases/latest/download/microbin-x86_64-unknown-linux-musl.tar.gz
tar -xzf microbin-*.tar.gz
chmod +x microbin
```

### 建立工作目錄

```bash
sudo mkdir -p /opt/microbin
sudo mv microbin /opt/microbin/
```

完成後目錄結構：

```
/opt/microbin/
├── microbin          ← 執行檔
├── start.sh          ← 啟動腳本（下方建立）
└── pasta_data/       ← 自動建立，儲存所有貼文資料
```

---

## 部署方式 A：直接執行

適合測試或臨時使用。

```bash
cd /opt/microbin
./microbin --port 3009 --bind 0.0.0.0 --highlightsyntax --editable
```

開啟瀏覽器前往：`http://localhost:3009`

---

## 部署方式 B：Systemd 常駐服務

適合正式部署，開機自動啟動，crash 後自動重啟。

### 步驟 1：建立啟動腳本

```bash
sudo nano /opt/microbin/start.sh
```

內容：

```bash
#!/bin/bash

/opt/microbin/microbin \
  --port 3009 \
  --bind 0.0.0.0 \
  --highlightsyntax \
  --editable
```

給予執行權限：

```bash
sudo chmod +x /opt/microbin/start.sh
```

### 步驟 2：建立 Systemd Service 檔案

```bash
sudo nano /etc/systemd/system/microbin.service
```

內容：

```ini
[Unit]
Description=MicroBin Pastebin Service
After=network.target

[Service]
ExecStart=/opt/microbin/start.sh
WorkingDirectory=/opt/microbin
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 步驟 3：啟動服務

```bash
sudo systemctl daemon-reload
sudo systemctl enable microbin   # 設定開機自啟
sudo systemctl start microbin    # 立即啟動
sudo systemctl status microbin   # 確認狀態
```

### 常用管理指令

```bash
# 查看即時 log
sudo journalctl -u microbin -f

# 修改 start.sh 後重新載入
sudo systemctl restart microbin

# 停止服務
sudo systemctl stop microbin

# 取消開機自啟
sudo systemctl disable microbin
```

---

## 部署方式 C：Docker

適合已有 Docker 環境，隔離性更好，升級方便。

### docker-compose.yml

```yaml
services:
  microbin:
    image: danielszabo99/microbin:latest
    restart: unless-stopped
    ports:
      - "3009:3009"
    volumes:
      - ./microbin-data:/app/pasta_data
    environment:
      - MICROBIN_PORT=3009
      - MICROBIN_BIND=0.0.0.0
      - MICROBIN_HIGHLIGHTSYNTAX=true
      - MICROBIN_EDITABLE=true
```

> ⚠️ 注意：`ports` 的 container 端口要與 `MICROBIN_PORT` 一致，否則連不上。
> 例如 `MICROBIN_PORT=3009` 時，ports 要設 `"3009:3009"`。

### 啟動

```bash
mkdir microbin && cd microbin
# 將上方 docker-compose.yml 存入此目錄
docker compose up -d

# 查看 log
docker compose logs -f
```

### 升級版本

```bash
docker compose pull
docker compose up -d
```

---

## 完整參數對照表

| 功能 | Binary 參數 | Docker 環境變數 | 說明 |
|------|------------|----------------|------|
| 監聽 Port | `--port 3009` | `MICROBIN_PORT=3009` | 服務埠號 |
| 綁定 IP | `--bind 0.0.0.0` | `MICROBIN_BIND=0.0.0.0` | 0.0.0.0 允許外部連線 |
| 語法高亮 | `--highlightsyntax` | `MICROBIN_HIGHLIGHTSYNTAX=true` | 程式碼著色 |
| 可編輯 | `--editable` | `MICROBIN_EDITABLE=true` | 允許修改貼文 |
| 唯讀 | `--readonly` | `MICROBIN_READONLY=true` | 禁止新增貼文 |
| 私密模式 | `--private` | `MICROBIN_PRIVATE=true` | 隱藏貼文列表 |
| 客戶端加密 | `--encryption-client-side` | `MICROBIN_ENCRYPTION_CLIENT_SIDE=true` | 瀏覽器端加密 |
| 寬螢幕版面 | `--wide` | `MICROBIN_WIDE=true` | 寬版 UI |
| 管理員帳號 | `--admin-username xxx` | `MICROBIN_ADMIN_USERNAME=xxx` | 管理員登入帳號 |
| 管理員密碼 | `--admin-password xxx` | `MICROBIN_ADMIN_PASSWORD=xxx` | 管理員登入密碼 |
| 隱藏 Logo | `--hide-logo` | `MICROBIN_HIDE_LOGO=true` | 隱藏頁面 Logo |

---

## 常見問題

**Q：資料存在哪裡？**
Binary 版本存在執行目錄下的 `pasta_data/`。Docker 版本存在 volume 掛載的目錄。備份時只需要備份這個資料夾。

**Q：如何備份資料？**
```bash
cp -r /opt/microbin/pasta_data /backup/microbin-$(date +%Y%m%d)
```

**Q：如何升級 Binary 版本？**
下載新版本，替換 `/opt/microbin/microbin` 執行檔，再 `sudo systemctl restart microbin` 即可。資料不受影響。

**Q：區域網路其他人連不進來？**
確認 `--bind` 設為 `0.0.0.0`，並確認防火牆沒有擋住對應 port：
```bash
sudo ufw allow 3009
```
