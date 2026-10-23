# SQL SPA Tools 字型規則

本文件定義全站一般介面與程式碼內容的字型規則。所有 HTML 頁面共用根目錄的 [`theme.css`](../theme.css)，字型家族集中由以下 token 管理：

| Token | 字型堆疊 | 使用範圍 |
| --- | --- | --- |
| `--theme-font-sans` | `"Microsoft JhengHei", "PingFang TC", "Noto Sans TC", "Noto Sans CJK TC", system-ui, sans-serif` | 一般文字、標題、按鈕、表單與表格 |
| `--theme-font-mono` | `"Cascadia Mono", Consolas, "SFMono-Regular", monospace` | SQL、程式碼、檔案路徑、日誌與差異比對內容 |

## 使用規則

- 頁面一般介面以 `var(--theme-font-sans)` 為準，按鈕與表單控制項沿用一般介面字型。
- SQL、程式碼、檔案路徑與日誌使用 `var(--theme-font-mono)`，維持字元對齊。
- 標題沿用一般介面字型，不使用襯線字型建立另一套頁面風格。
- 不在個別頁面重新指定一般介面字型，也不建立頁面專屬的字型別名。
- 字型候選以逗號分隔，瀏覽器依序使用裝置已安裝的字型與系統後備字型。
- 不新增外部字型 CDN、追蹤程式或網路依賴，確保頁面可離線使用。
- 頁面專屬樣式只在需要時指定字型用途，不得改變共用字型堆疊。

## 獨立輸出

報表、列印頁、匯出 HTML 與 SVG 可能脫離主頁面獨立開啟。輸出模板應內嵌上述兩組相同的字型候選順序，再按內容指定一般或等寬字型，不能依賴根目錄 `theme.css` 存在。

修改字型 token 或堆疊時，應同步檢查所有獨立輸出模板與 SVG 文字樣式。
