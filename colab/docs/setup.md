# Google Colab CLI 設定步驟

## 環境資訊

- 作業系統：Windows
- Python：3.13
- 套件：`google-colab-cli`
- CLI 執行檔：`$env:APPDATA\Python\Python313\Scripts\colab.exe`

> Google Colab CLI 官方目前支援 Linux 與 macOS，尚未支援 Windows。本機 Windows 環境已可完成登入與查詢工作階段；其他功能可能受平台限制。

## 安裝

以 PowerShell 執行：

```powershell
python -m pip install --user google-colab-cli
```

檢查執行檔是否存在並查看指令：

```powershell
$colab = Join-Path $env:APPDATA 'Python\Python313\Scripts\colab.exe'
Test-Path $colab
& $colab --help
```

如果 `colab` 指令已在 PATH，可直接使用 `colab`；否則使用上面的 `$colab` 完整路徑執行。

## 登入

第一次呼叫需要 Google OAuth 授權。執行：

```powershell
& (Join-Path $env:APPDATA 'Python\Python313\Scripts\colab.exe') sessions
```

CLI 會顯示 Google 授權網址：

1. 在瀏覽器開啟 CLI 顯示的網址。
2. 登入 Google 帳戶並核准 Colab CLI 要求的存取權限。
3. 複製 Google 顯示的一次性授權碼。
4. 將授權碼貼到終端機的 `Enter the authorization code:` 提示並按 Enter。

授權成功後，CLI 會列出可用的 Colab 工作階段。之後再次執行 `sessions`，確認不需重新授權即可列出工作階段。

## 關閉並確認所有工作階段

在檔案總管雙擊 `colab/close_colab_sessions.bat`。批次檔會呼叫 `close_colab_sessions.py`，先列出工作階段並要求確認；解除指派後會輪詢伺服器最多 30 秒，確認工作階段清單為空才回報成功。按 `Ctrl+C` 或輸入非 `y` 回應可取消。

## 常用確認指令

```powershell
$colab = Join-Path $env:APPDATA 'Python\Python313\Scripts\colab.exe'
& $colab sessions
& $colab version
```

## 憑證位置與安全

OAuth 憑證由 CLI 保存在使用者設定目錄（通常為 `~/.config/colab-cli/token.json`）。請勿將此檔案提交到 Git、貼到聊天或分享給他人。授權碼是一次性敏感資料，也不要留存在文件或日誌中。

本設定已透過重複執行 `sessions` 驗證登入成功；目前帳戶列出三個工作階段。
