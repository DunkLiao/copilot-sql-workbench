# SQL SPA Tools 配色規範與引用說明

本文件定義 SQL SPA Tools 全站共用的水墨黑白主題。所有工具頁面應使用根目錄的 [`theme.css`](../theme.css)，避免各頁重新建立不同的背景、文字、按鈕與狀態色。

## 適用頁面

目前以下頁面共用同一份主題：

- `index.html`
- `sql-spa-tools-catalog.html`
- `sql-spa-tools-column-lineage.html`
- `sql-spa-tools-sqlscriptmanage.html`
- `sql-spa-tools-excel-csv-sql.html`
- `sql-spa-tools-excel-csv-sql-cte.html`
- `sql-spa-tools-sql-lab.html`
- `sql-spa-tools-oracle-formatter.html`
- `sql-spa-tools-pii-cleaner.html`
- `sql-spa-tools-sql-compare.html`
- `sql-spa-tools-data-quality-audit-center.html`
- `sql-spa-tools-data-relationship-explorer.html`
- `sql-spa-tools-schema-studio.html`

頁面與 `theme.css` 必須位於同一個資料夾，才能支援直接以瀏覽器開啟 HTML 的離線使用方式。

## 設計原則

1. 以黑、白、灰階建立頁面基底、文字與介面層次。
2. 背景、面板、表單、按鈕與邊框應使用共用 token，不直接寫死新的色碼。
3. 成功、警告、錯誤與資訊均使用黑、白、灰階，不以色相區分狀態。
4. 狀態差異透過明暗、文字與圖示表達，並維持明暗主題下的可讀性。
5. 匯出報表、列印頁與 SVG 等離開主頁面的輸出，必須使用相同的主題色。
6. 顏色變更不應影響既有版面、互動流程或資料處理行為。

## 共用字型

全站字型 token 定義於 `theme.css`，各頁面不得自行建立不同的全域字型設定：

| Token | 字型堆疊 | 用途 |
| --- | --- | --- |
| `--theme-font-sans` | `"Microsoft JhengHei", "PingFang TC", "Noto Sans TC", "Noto Sans CJK TC", system-ui, sans-serif` | 一般介面、標題、表單、按鈕與表格 |
| `--theme-font-mono` | `"Cascadia Mono", Consolas, "SFMono-Regular", monospace` | SQL、程式碼、路徑與日誌 |

`body` 與表單控制項使用一般介面字型；程式碼相關元件可明確使用等寬字型。字型只從使用者裝置上的本機字型載入，不新增外部字型或網路依賴。標題沿用一般介面字型，不另用襯線字型建立不同風格。

獨立開啟的報表、列印頁與匯出內容不一定會載入根目錄的 `theme.css`，因此其模板必須內嵌相同的字型候選順序。具 SVG 文字的輸出也應指定相同的一般或等寬字型堆疊。

詳細維護規則見 [`FONTS.md`](FONTS.md)。

## 深／淺色模式

- 預設模式為淺色，頁面未設定 `data-theme` 時即使用淺色 token。
- 每個頁面都有 `#themeToggle` 按鈕，可在深色與淺色之間切換。
- 使用者選擇會寫入 `localStorage` 的 `sql_spa_tools_theme`。
- 只有儲存值為 `dark` 時使用深色；其他值與首次開啟均回到淺色。
- 切換行為由共用 [`theme.js`](../theme.js) 管理，不得在個別頁面重複實作。

深色模式的核心 token 定義在 `theme.css` 的 `:root[data-theme='dark']`；淺色模式則使用未設定深色主題時的基準配色。

## 核心色彩 token

以下 token 定義於 `theme.css`。新元件應優先使用這些 `--theme-*` token；表格中的色碼是淺色模式基準值，深色模式會由同一 token 自動覆寫。

| Token | 色碼 | 用途 |
| --- | --- | --- |
| `--theme-page` | `#f6f6f6` | 全頁背景 |
| `--theme-surface` | `#ffffff` | 卡片、面板、輸入框 |
| `--theme-surface-alt` | `#ececec` | 表頭、工具列、次級區塊 |
| `--theme-surface-soft` | `#f2f2f2` | hover、程式碼區、柔和底色 |
| `--theme-text` | `#303030` | 主要文字 |
| `--theme-muted` | `#707070` | 輔助文字、說明文字 |
| `--theme-border` | `#d4d4d4` | 主要邊框與分隔線 |
| `--theme-border-soft` | `#e4e4e4` | 表格細線、次要分隔線 |
| `--theme-primary` | `#444444` | 主要操作、頁首、選取重點 |
| `--theme-primary-hover` | `#2e2e2e` | 主要操作 hover、強調邊框 |
| `--theme-secondary` | `#777777` | 輔助操作、focus、灰階重點 |
| `--theme-secondary-soft` | `#e9e9e9` | 灰階背景、選取狀態 |
| `--theme-purple` | `#777777` | 血緣／分類等次要識別 |
| `--theme-purple-soft` | `#e9e9e9` | 灰階背景 |
| `--theme-shadow` | `0 8px 24px rgb(48 48 48 / 12%)` | 浮動面板陰影 |

主題使用黑、白與灰階呈現水墨層次。成功、警告、錯誤與資訊狀態透過不同深淺的灰階及狀態文字區分，並確保明暗主題下均清楚可讀。

## 語意色規範

語意色只用來表達狀態，不用作一般裝飾或頁面主色。

| 狀態 | 文字／邊框 | 背景 | 使用情境 |
| --- | --- | --- | --- |
| 成功 | `--theme-success` `#505050` | `--theme-success-soft` `#e6e6e6` | 完成、通過、已寫回、增加 |
| 警告 | `--theme-warning` `#5c5c5c` | `--theme-warning-soft` `#dddddd` | 注意、待確認、修改 |
| 錯誤 | `--theme-danger` `#333333` | `--theme-danger-soft` `#cecece` | 失敗、刪除、錯誤、危險操作 |
| 資訊 | `--theme-info` `#595959` | `--theme-info-soft` `#eeeeee` | 提示、說明、資訊摘要 |

範例：

```css
.message-success {
  color: var(--theme-success);
  background: var(--theme-success-soft);
}

.message-error {
  color: var(--theme-danger);
  background: var(--theme-danger-soft);
}
```

## HTML 引用方式

每個頁面應在 `<head>` 中引用共用樣式：

```html
<link rel="stylesheet" href="theme.css">
<script src="theme.js"></script>
```

引用規則：

- `theme.css` 與 HTML 必須位於同一層目錄。
- `theme.js` 與 HTML 必須位於同一層目錄。
- 新頁面不可複製另一頁的完整 `:root` 色彩設定。
- 新增元件時，先使用 `--theme-*` token；只有既有元件相容需求才使用舊別名。
- 頁面專屬 CSS 可以保留布局與元件細節，但不得重新定義全站基礎色彩。
- 新增頁面時必須提供 `id="themeToggle"` 的按鈕，並引用 `theme.js`。
- 工具頁面必須提供回首頁連結，使用 `class="home-link"` 並指向 `index.html`：

  ```html
  <a class="home-link" href="index.html">⌂ 工具入口</a>
  ```

- `index.html` 本身是入口頁，不需要連結回自己。

## 既有相容別名

為了讓現有頁面逐步共用主題，`theme.css` 也提供 `--bg`、`--panel`、`--text`、`--muted`、`--pri`、`--ok`、`--warn`、`--err`、`--info` 等相容別名。

新程式碼不應再增加相容別名；請直接使用 `--theme-*` token。若修改既有元件，建議同步將舊別名替換為核心 token。

## 元件使用規範

### 按鈕

- 一般按鈕：`--theme-surface` 背景、`--theme-border` 邊框。
- 主要按鈕：`--theme-primary` 背景、淺色文字。
- 輔助按鈕：`--theme-secondary-soft` 背景。
- 危險按鈕：`--theme-danger-soft` 背景、`--theme-danger` 系列文字。
- disabled 狀態應降低透明度，但仍需保留文字辨識度。

### 表單與表格

- 表單控制項使用 `--theme-surface` 背景與 `--theme-border` 邊框。
- focus 使用 `--theme-primary` 邊框或 `--theme-secondary-soft` 外框。
- 表頭使用 `--theme-surface-alt`。
- hover 使用 `--theme-surface-soft`。
- 表格分隔線使用 `--theme-border-soft`。

### Header、Toolbar 與 Footer

- Header 使用 `--theme-primary`，文字使用淺色。
- Toolbar、Footer、次級導覽使用 `--theme-surface` 或 `--theme-surface-alt`。
- 不應在不同頁面重新引入彩色主題或高飽和裝飾色。

## CSP 與離線引用

`sql-spa-tools-catalog.html` 與 `sql-spa-tools-pii-cleaner.html` 有 Content Security Policy。因為頁面要載入同目錄的 `theme.css`，CSP 必須包含：

```text
style-src 'self' 'unsafe-inline'
script-src 'self' 'unsafe-inline'
```

若新增具有 CSP 的頁面，也要確認瀏覽器 Network／Console 沒有封鎖 `theme.css` 的錯誤。

## 動態報表與匯出

動態產生的 HTML 報表可能被下載到不同位置，不能假設使用者仍能取得根目錄的 `theme.css`。因此：

- 報表內嵌 CSS 應使用與主題相同的固定色碼。
- SVG 節點、連線與標記應使用主題對應色。
- 匯出樣式應維持黑、白、灰階，不得使用與共用主題不一致的色盤。
- 修改主題色時，應同步搜尋各 HTML 內的報表模板與 SVG 色彩設定。

## 驗證方式

在專案根目錄執行：

```powershell
node '.\tests\test-theme.js'
& '.\tests\validate-theme.ps1'
```

驗證內容包括：

- `theme.css` 是否存在且包含核心 token。
- `theme.js` 是否存在且使用 `sql_spa_tools_theme` 儲存模式。
- 所有 HTML 是否引用 `theme.css`。
- 所有 HTML 是否都包含 `themeToggle` 與 `theme.js`。
- 所有工具頁面是否都包含 `home-link` 並指向 `index.html`。
- 未設定主題時是否以淺色 token 為預設。
- 具有 CSP 的頁面是否允許同目錄樣式檔。
- Formatter、Catalog、SQL Compare 的動態報表是否包含共用主題色。

完成樣式調整後，應在瀏覽器實際開啟入口頁與各工具頁面，確認一般狀態、hover、focus、disabled、成功、警告、錯誤與匯出畫面均維持一致。
