# SQL SPA Tools 開發規範

本專案的所有網頁設計、樣式調整與新頁面開發，都必須遵守以下文件：

- [命名規則](docs/NAMING.md)
- [配色規範與引用說明](docs/THEME.md)
- [全站字型規則](docs/FONTS.md)

## 強制規則

### 1. 頁面命名

- 頁面名稱使用 `SQL SPA Tools｜功能名稱`。
- `<title>` 與頁面主標題使用相同的主要名稱。
- 不在頁面名稱或主標題加入版本號。
- HTML 檔名使用小寫 kebab-case，並以 `sql-spa-tools-` 開頭。
- 檔名不得包含空白、底線、大寫字母、日期或版本號。
- `index.html` 為入口頁保留檔名例外，不需要 `sql-spa-tools-` 前綴。

新增頁面前，先確認功能名稱與檔名不會和既有頁面衝突；若頁面被索引、文件或其他 HTML 引用，必須同步更新引用路徑。

### 2. 共用主題

- 每個 HTML 頁面都必須引用根目錄的 `theme.css`：

  ```html
  <link rel="stylesheet" href="theme.css">
  ```

- 每個 HTML 頁面都必須引用根目錄的 `theme.js`：

  ```html
  <script src="theme.js"></script>
  ```

- 每個頁面都必須提供 `id="themeToggle"` 的深／淺色切換按鈕。
- 每個工具頁面都必須提供 `class="home-link"` 的回首頁連結，指向 `index.html`。
- `index.html` 是入口頁，不需要連結回自己。
- 預設主題必須是淺色；只有使用者明確選擇深色時才使用深色模式。
- 不得在個別頁面重新建立另一套全域色彩系統。
- 新增 CSS 優先使用 `--theme-*` token，不直接寫死背景、文字、邊框或狀態色。
- 全站一般介面字型統一使用 `var(--theme-font-sans)`；SQL、程式碼、路徑與日誌等內容使用 `var(--theme-font-mono)`。
- 不得在個別頁面重新指定一般介面字型或另建字型別名；標題沿用一般介面字型，不使用襯線字型作為另一套視覺風格。
- 獨立報表、列印頁與匯出內容須內嵌相同的中英文字型候選順序與等寬字型候選順序，確保離線單獨開啟時字型一致。
- 既有相容別名僅供維護舊元件使用，新程式碼不得再增加相容別名。
- 頁面專屬 CSS 只能處理布局與元件細節，不得覆蓋全站主題契約。

### 3. 顏色與狀態

- 主要操作使用 `--theme-primary`。
- 一般文字使用 `--theme-text`，輔助文字使用 `--theme-muted`。
- 面板使用 `--theme-surface`，次級區塊使用 `--theme-surface-alt`。
- hover 使用 `--theme-surface-soft`。
- 成功、警告、錯誤、資訊必須分別使用對應的語意 token。
- 不使用純黑作為一般文字，也不使用高飽和紅、黃、藍作為主要 UI 色。
- 深色模式下仍須維持文字、按鈕、focus 與 disabled 狀態的可讀性。

### 4. 離線與安全限制

- 所有頁面必須維持同資料夾直接開啟的離線使用方式。
- `theme.css`、`theme.js` 與 HTML 頁面必須放在同一層目錄。
- 具有 CSP 的頁面必須允許同目錄樣式與腳本：

  ```text
  style-src 'self' 'unsafe-inline'
  script-src 'self' 'unsafe-inline'
  ```

- 不任意新增外部 CDN、追蹤程式或網路依賴。

### 5. 動態輸出

若頁面會產生列印頁、HTML 報表、SVG 或其他可獨立開啟的輸出：

- 輸出樣式必須沿用 `THEME.md` 定義的色彩語意。
- 不可因離開主頁面而恢復舊有深紅、藏青、金色或高飽和色盤。
- 修改主題 token 後，必須同步檢查動態報表模板與 SVG 色彩。

## 新增或修改網頁檢查清單

- [ ] 已依 `docs/NAMING.md` 命名 HTML 檔案。
- [ ] `<title>` 與頁面主標題符合 `SQL SPA Tools｜功能名稱`。
- [ ] 已引用 `theme.css` 與 `theme.js`。
- [ ] 已加入 `themeToggle`。
- [ ] 工具頁已加入 `home-link` 回首頁連結。
- [ ] 預設開啟為淺色模式。
- [ ] 所有新增顏色均使用 `--theme-*` token。
- [ ] 一般介面與程式碼字型分別使用 `--theme-font-sans` 與 `--theme-font-mono`。
- [ ] 動態報表、列印與匯出內容沿用共用字型堆疊。
- [ ] 一般、hover、focus、disabled、成功、警告、錯誤狀態均可讀。
- [ ] CSP 沒有阻擋共用 CSS 或 JavaScript。
- [ ] 動態報表、列印與匯出樣式已同步檢查。
- [ ] 沒有改變既有功能或資料處理行為。

## 驗證命令

以下命令與 GitHub Actions「回歸測試」workflow 完全相同（設定檔：[.github/workflows/regression-test.yml](.github/workflows/regression-test.yml)）。在本機執行可先重現 CI 結果，再推送變更。

Node.js 測試（CI 使用 Node.js 22，於 `ubuntu-latest` 執行）：

```powershell
node '.\tests\test-theme.js'
node '.\tests\test-excel-csv-sql.js'
node '.\tests\test-excel-csv-sql-cte.js'
node '.\tests\test-sqlscriptmanage.js'
node '.\tests\test-schema-studio.js'
node '.\tests\test-copilot-export.js'
node '.\tests\test-copilot-impact-demo.js'
node '.\tests\test-data-quality-audit-center.js'
node '.\tests\test-pii-cleaner.js'
node '.\tests\test-sql-lab.js'
node --check '.\theme.js'
```

PowerShell 驗證（CI 於 `windows-latest` 以 `pwsh` 執行；本機 Windows PowerShell 亦可）：

```powershell
& '.\tests\validate-theme.ps1'
& '.\tests\validate-index.ps1'
& '.\tests\validate-home-links.ps1'
```

新增或調整測試腳本時，必須同步更新 CI workflow 與上述清單，確保規範文件、測試與 CI 保持一致。

完成後應再以瀏覽器開啟所有 HTML 頁面，確認主題切換、頁面布局、表單操作與動態輸出均正常。

## 文件維護

若命名或主題規範變更，必須先更新：

1. `docs/NAMING.md` 或 `docs/THEME.md`
2. 本 `AGENTS.md`
3. 相關測試與現有頁面

規範文件、測試與實際頁面行為必須保持一致。
