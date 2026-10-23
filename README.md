# SQL 變更影響評估 Copilot｜鎖頭銀行 M365 Copilot 黑客松

本專案是鎖頭銀行 M365 Copilot 黑客松的參賽工作區，目標是展示如何以 SQL SPA Tools 協助資料與開發團隊整理 SQL 變更影響，再由 Microsoft 365 Copilot Chat 根據經人工檢查的摘要產出影響說明與檢核清單。

- **參賽期間：** 2026/10/22–2026/12/24
- **參賽人員：** 鎖頭銀行風險管理部 Dunk
- **提案方向：** 用 M365 Copilot 加速 SQL 變更影響評估，並保留銀行資料安全與人工覆核

## 專案內容

| 路徑 | 說明 |
| --- | --- |
| [`index.html`](index.html) | 專案入口，可由瀏覽器開啟 |
| [`sql-spa-tools-main/`](sql-spa-tools-main/) | SQL SPA Tools 原型、使用手冊、測試與 CI 設定 |
| [`參賽準備/`](參賽準備/) | 提案、Demo 講稿、設計、量測計畫與待辦 |
| [`參賽準備/參賽文件/`](參賽準備/參賽文件/) | 正式提案書、競賽簡報與成效量化報告 |
| [`theme.md`](theme.md) | 鎖頭銀行企業配色與視覺使用原則 |

SQL SPA Tools 的完整操作說明與功能清單請見 [`sql-spa-tools-main/README.md`](sql-spa-tools-main/README.md)。

## 快速展示

1. 以 Chrome 或 Edge 開啟根目錄的 [`index.html`](index.html)，進入工具入口。
2. 使用內建的合成 SQL 案例，在 SQL Compare 比對版本，並於欄位血緣分析器檢視下游影響。
3. 檢查 Copilot 摘要預覽，確認物件與欄位名稱適合展示，再依畫面確認程序匯出 JSON。
4. 在具備使用權限的 Microsoft 365 Copilot Chat 中，由參賽者手動上傳摘要 JSON，並使用 [`Copilot Chat 固定提示.md`](參賽準備/Copilot%20Chat%20固定提示.md) 中的提示。
5. 將 Copilot 回覆逐項對照摘要證據，檢查影響、警告、限制與人工檢核項目。

此原型使用「本機 SQL 分析、人工確認、手動交接摘要至 Copilot Chat」流程；不是已連接 M365 的自動化服務或正式銀行系統整合。個人帳戶探索結果、待驗證項目與限制請以提案文件和量測紀錄為準；尚未驗證的效益不應描述為實測成果。

## 資料安全與展示邊界

- 展示及測試使用合成 SQL、合成資料與示範名稱，不使用生產資料或真實客戶資料。
- SQL 分析在使用者瀏覽器中進行。只有使用者明確檢查並確認匯出後，摘要 JSON 才會交由使用者手動上傳。
- 摘要不含原始 SQL，但可能含有資料表或欄位名稱；匯出及上傳前仍須確認名稱已核准用於該租用戶與展示情境。
- Copilot 回覆需由工程師核對來源證據。靜態分析未發現關係不代表沒有影響；解析警告及分析限制應一併說明。
- formatter 寫回與個資清除器可能修改選取的本機檔案；操作前請先檢查目標並保留備份。

## 開發與驗證

一般使用者不需安裝套件：原型可直接以瀏覽器開啟。維護者測試需求、命令與 CI 工作流程請參閱 [`sql-spa-tools-main/AGENTS.md`](sql-spa-tools-main/AGENTS.md) 及 [`sql-spa-tools-main/README.md`](sql-spa-tools-main/README.md)。

## 文件導覽

- [黑客松提案報告](參賽準備/黑客松提案報告.md)
- [Copilot 原型設計](參賽準備/sql-spa-tools-copilot-hackathon-design.md)
- [3 至 5 分鐘 Demo 講稿](參賽準備/3至5分鐘Demo講稿.md)
- [成效驗證計畫與紀錄](參賽準備/成效驗證計畫與紀錄.md)
- [參賽待辦](參賽準備/TODO.md)
- [正式提案書](參賽準備/參賽文件/SQL_SPA_Tools_黑客松正式提案書.docx)
- [競賽簡報](參賽準備/參賽文件/SQL_SPA_Tools_競賽簡報.pptx)
- [成效量化報告](參賽準備/參賽文件/SQL_SPA_Tools_成效量化報告.xlsx)

Office 文件及展示素材應遵循 [`theme.md`](theme.md) 的企業配色規範；如需新增或改變色彩語意，先更新該文件。
