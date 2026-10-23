# Excel／CSV 轉 SQL UAT 測試檔案

## M365 Copilot 變更影響 Demo

`copilot-impact-demo/` 是欄位血緣分析與 Copilot 摘要的合成案例，不含任何資料列或真實銀行資料：

1. 在 SQL Compare 載入 `customer-before.sql` 與 `customer-after.sql`，確認 `DEMO_CUSTOMER.CUSTOMER_SEGMENT` 從 `VARCHAR2(20)` 改為 `VARCHAR2(40)`。
2. 在 SQL 欄位血緣分析器載入 `downstream.sql` 並分析。
3. 按「Copilot 摘要」，檢查物件／欄位名稱，再確認並下載 JSON。
4. 以 `copilot-impact-demo/expected.json` 對照摘要的兩個預期下游影響與證據。
5. 在 M365 Copilot Chat 上傳 JSON，貼上[固定提示](../../參賽準備/Copilot Chat 固定提示.md)，逐項核對 Copilot 回覆與 JSON 證據。

不確定性演練：在欄位血緣分析器載入 `copilot-impact-demo/parser-warning.sql`。這份合成 SQL 故意省略 PIVOT 的 `IN` 清單，摘要應顯示一筆 `warn`。下載並檢查摘要後，使用同一份固定提示上傳至 Copilot Chat；檢查它是否指出警告數量、解析訊息全文未隨摘要匯出、靜態分析限制及人工覆核要求。若 Copilot 過度確定或補造影響，保留原答並記為未通過。

`tests/test-copilot-impact-demo.js` 會直接執行頁面中的分析器，檢查兩個預期影響、解析錯誤與警告計數。此案例驗證靜態血緣辨識，不代表資料庫已執行 DDL，也不代表正式環境變更核准。Node 測試不會驗證 M365 Copilot Chat 的實際回覆。

預期結果：`DEMO_MONTHLY_REPORT.SEGMENT_LABEL` 為直接來源，`DEMO_RISK_SEGMENTATION.RISK_BUCKET` 為條件判斷的間接來源；其他欄位不列入 `CUSTOMER_SEGMENT` 的影響清單。

---

請在工具頁選擇檔案後，分別測試以下情境：

| 檔案 | 測試重點 | 建議設定 |
| --- | --- | --- |
| `uat-basic-utf8.csv` | 引號、逗號、多行儲存格、NULL、前導零、日期與布林值 | 編碼選「自動偵測 BOM」；Header 開啟 |
| `uat-big5-cp950.csv` | Big5／CP950 繁體中文檔案 | 編碼選「Big5／CP950」；Header 開啟 |
| `uat-utf16le.csv` | UTF-16 Little Endian | 編碼選「自動偵測 BOM」；Header 開啟 |
| `uat-utf16be.csv` | UTF-16 Big Endian | 編碼選「自動偵測 BOM」；Header 開啟 |
| `uat-no-header-utf8.tsv` | Tab 分隔且沒有欄位標題 | 編碼選「UTF-8」；欄位名稱模式選「自動產生欄位名稱」 |
| `uat-large-100k-utf8.csv` | 100,000 筆、8 欄的效能與分塊輸出；含 UTF-8 BOM、繁體中文、前導零、布林值、日期及含逗號的引號欄位 | 編碼選「自動偵測 BOM」；Header 開啟；先用 SQLite 或 PostgreSQL，另切換 SQL Server 確認每塊最多 1,000 筆 |

也請測試「啟用自訂欄位名稱」：勾選後輸入 `member_id, city, postal_code, score`，再按「套用自訂欄位名稱」載入無標題 TSV，確認欄位數量一致時可正常產生 SQL，數量不一致時會顯示錯誤。此選項預設不啟用。

建議將資料表名稱設為 `uat_import_test`，並依序切換 PostgreSQL、MySQL、SQL Server、Oracle、SQLite，確認 DDL、DML、複製與下載內容均正常。

大型檔案匯入後，確認資料列顯示 `100,000`、欄位數為 `8`，SQL 可完整預覽、複製及下載；SQL Server 的分塊數應為 `100`（每塊 1,000 列）。
