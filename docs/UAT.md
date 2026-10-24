# SQL SPA Tools 使用者驗收測試（UAT）

本文件說明如何開始並記錄 SQL SPA Tools 的使用者驗收測試。UAT 使用合成案例，不得上傳真實客戶資料、帳號資料或未經核准的銀行內部資料至測試頁面、Google Colab 或 M365 Copilot Chat。

## 驗收目標

- 確認工具可載入並完成主要使用流程。
- 核對匯入、分析與匯出結果符合預期。
- 確認 Copilot 摘要能忠實呈現靜態分析證據、警告與限制，不補造影響。
- 留存可重現的操作步驟、預期結果、實際結果與缺陷證據。

UAT 是人工驗收。Colab 自動測試可協助檢查既有契約與主要瀏覽器流程，但不會替你驗證 M365 Copilot Chat 的實際回覆，也不涵蓋工具的所有操作選項及錯誤路徑。

## 開始前

1. 從儲存庫根目錄開啟 `sql-spa-tools-main/index.html`，建議使用最新版 Chrome 或 Edge。
2. 確認可正常瀏覽工具入口並開啟待測工具頁。
3. 使用 `sql-spa-tools-main/uat-fixtures/` 中的合成資料；詳細案例說明見 [`sql-spa-tools-main/uat-fixtures/README.md`](../sql-spa-tools-main/uat-fixtures/README.md)。
4. 如果要測試 Copilot 摘要與實際 M365 Copilot Chat，確認已登入核准的 M365 帳號，並可使用 [`參賽準備/Copilot Chat 固定提示.md`](../參賽準備/Copilot%20Chat%20固定提示.md)。
5. 建立 UAT 紀錄，記下日期、測試人員、瀏覽器與版本、應用程式版本或 Git commit，以及每項案例的結果。

## 第一階段：自動化環境檢查（建議）

在儲存庫根目錄開啟 PowerShell：

```powershell
python colab/run_colab_tests.py doctor
python colab/run_colab_tests.py run --mode quick
```

`doctor` 檢查本機專案、Python 與 Colab CLI，不會建立遠端工作階段。`quick` 會建立 Colab 工作階段、執行 50 組合成案例及既有主要檢查，完成後下載並驗證成果。首次執行可能會在終端要求 Google OAuth 授權。

成果預設存放於 `colab/outputs/cli/<run-id>/`。先查看 `test-results.zip` 與 `run-state.json`；退出碼 `0` 表示自動測試通過且成果已驗證，退出碼 `1` 表示測試有失敗但報告已下載，請開啟報告檢視。完整的自動測試範圍與退出碼見 [`colab/docs/testing-guide.md`](../colab/docs/testing-guide.md)。

模式與案例數：

| 命令 | 模式 | 合成案例數 | 執行範圍 |
|---|---|---:|---|
| `python colab/run_colab_tests.py run` | 預設 `full` | 1,000 | 10 支 Node 契約測試、12 個工具頁載入檢查、主要瀏覽器功能檢查，以及 Formatter 完整效能測試 |
| `python colab/run_colab_tests.py run --mode full` | `full` | 1,000 | 與上列相同，明確指定完整模式 |
| `python colab/run_colab_tests.py run --mode quick` | `quick` | 50 | 相同類型的契約與瀏覽器檢查，效能測試縮小為 100 份 SQL、量測一次 |

以上案例數是產生並保存在報告中的合成案例數。報告裡 `prepared` 表示案例已產生，**不代表該筆案例已逐一送入工具執行或驗收通過**；請將自動化檢查結果與下一階段的人工 UAT 分開判讀。完整效能模式會以 Formatter 實際函式處理 100／1,000／10,000 份 SQL，各規模暖機一次並量測五次。

**Windows 限制：** 官方 `google-colab-cli` 目前尚未正式支援 Windows。若遠端操作失敗，請改用 WSL 中的 Python 與 CLI，並在 WSL 完成登入；不要複製 Windows 的 CLI token。CLI 尚未在真實 Colab runtime 完成端到端驗證時，也可直接使用下一節的 Notebook 手動流程。

## 第二階段：Notebook 手動測試流程

原有手動流程持續可用：

1. 開啟 `colab/sql_tools_test_framework.ipynb`，在 Google Colab 選擇「執行階段 → 全部執行」。
2. 上傳儲存庫根目錄打包的 ZIP。解壓後的專案根目錄必須同時包含 `sql-spa-tools-main/` 與 `colab/`，不要只壓縮 `sql-spa-tools-main/`。
3. 等待測試執行完成，再下載 `test-results.zip`。
4. 在 `test-report.xlsx` 檢視總覽、模組覆蓋、案例明細、效能結果、失敗與限制；逐筆結果見 `results/results.json` 和 `results/results.csv`。

Notebook 預設執行 full：固定種子 `20261023`、1,000 組合成案例。若要先快速檢查，可在 Notebook 設定區改為 `quick`，執行 50 組案例。更多說明見 [`colab/docs/testing-guide.md`](../colab/docs/testing-guide.md)。

## 第三階段：人工驗收案例

### A. SQL 變更影響與 Copilot 摘要

使用 `sql-spa-tools-main/uat-fixtures/copilot-impact-demo/` 中的合成 SQL 和預期結果。

1. 開啟 SQL Compare，載入 `customer-before.sql` 和 `customer-after.sql`。
2. 確認 `DEMO_CUSTOMER.CUSTOMER_SEGMENT` 型別由 `VARCHAR2(20)` 變更為 `VARCHAR2(40)`。
3. 開啟 SQL 欄位血緣分析器，載入 `downstream.sql` 並執行分析。
4. 按「Copilot 摘要」，檢查物件與欄位名稱，確認後匯出 JSON。
5. 對照同資料夾的 `expected.json`，驗證影響清單：
   - `DEMO_MONTHLY_REPORT.SEGMENT_LABEL` 是直接影響欄位。
   - `DEMO_RISK_SEGMENTATION.RISK_BUCKET` 是條件判斷形成的間接影響欄位。
   - 不應把其他欄位列入 `CUSTOMER_SEGMENT` 的影響清單。
6. 在 M365 Copilot Chat 上傳剛匯出的 JSON，貼上 [`參賽準備/Copilot Chat 固定提示.md`](../參賽準備/Copilot%20Chat%20固定提示.md) 的固定提示。
7. 逐項比對 Copilot 回覆與 JSON 證據；記錄是否漏掉影響、加入 JSON 未支持的結論，或未遵守限制。

### B. 解析警告與不確定性

1. 在 SQL 欄位血緣分析器載入 `copilot-impact-demo/parser-warning.sql`。
2. 執行分析並匯出 Copilot 摘要 JSON。
3. 確認摘要顯示一筆 `warn`，且沒有把不完整解析描述成確定結果。
4. 在 Copilot Chat 上傳摘要 JSON，使用相同固定提示。
5. 核對 Copilot 是否說明警告數量、靜態分析限制及人工覆核要求；若過度確定或補造影響，保留原始回覆並判定未通過。

此案例測試的是 SQL 靜態分析，不代表資料庫已執行 DDL，也不代表正式環境變更已獲核准。Node 契約測試不會驗證 M365 Copilot Chat 的實際回覆。

### C. Excel／CSV 轉 SQL 匯入與輸出

在 Excel／CSV 轉 SQL 工具依序載入下列合成檔案，檢查預覽、欄位型別推斷與輸出內容：

| Fixture | 驗收重點 | 建議設定 |
|---|---|---|
| `uat-basic-utf8.csv` | 引號、逗號、多行儲存格、NULL、前導零、日期與布林值 | 編碼選「自動偵測 BOM」；開啟 Header |
| `uat-big5-cp950.csv` | Big5／CP950 繁體中文 | 編碼選「Big5／CP950」；開啟 Header |
| `uat-utf16le.csv` | UTF-16 Little Endian | 編碼選「自動偵測 BOM」；開啟 Header |
| `uat-utf16be.csv` | UTF-16 Big Endian | 編碼選「自動偵測 BOM」；開啟 Header |
| `uat-no-header-utf8.tsv` | Tab 分隔、沒有欄位標題 | 編碼選「UTF-8」；欄位名稱選「自動產生欄位名稱」 |
| `uat-large-100k-utf8.csv` | 100,000 筆、8 欄、中文、前導零、布林值、日期與含逗號欄位 | 編碼選「自動偵測 BOM」；開啟 Header |

另外驗收自訂欄位名稱：勾選「啟用自訂欄位名稱」，輸入 `member_id, city, postal_code, score`，再載入無標題 TSV。欄位數一致時應可產生 SQL；欄位數不一致時應顯示錯誤。

將資料表命名為 `uat_import_test`，依序切換 PostgreSQL、MySQL、SQL Server、Oracle 與 SQLite，檢查 DDL、DML、複製及下載結果。對 100,000 筆案例確認顯示列數為 `100,000`、欄位數為 `8`，可完整預覽、複製及下載。SQL Server 分塊輸出應為 100 塊，每塊最多 1,000 列。

### D. 其他工具主要流程

先使用前述自動化報告作為回歸檢查，再依本次 UAT 範圍操作指定工具頁。每項流程至少驗收：

- 頁面能載入，標題與工具用途相符。
- 使用合成輸入可完成主要操作。
- 結果內容、錯誤提示、複製或下載符合預期。
- 深／淺色切換與回首頁導覽可用。
- 不輸入真實個資或連線至正式資料庫。

如 UAT 涵蓋工具的例外情境，記錄明確輸入、操作步驟與預期錯誤訊息，不以「看起來正常」代替驗收條件。

## 結果判定與紀錄

每一案例的狀態使用 `通過`、`失敗`、`阻塞` 或 `未執行`。失敗時保留去識別化的輸入、預期／實際差異、錯誤訊息和截圖或匯出檔位置；不得把含機密資料的畫面或檔案放入一般 UAT 紀錄。

| ID | 案例 | 預期結果 | 實際結果／證據 | 狀態 | 缺陷編號／備註 |
|---|---|---|---|---|---|
| UAT-001 | 欄位型別變更比對 | `CUSTOMER_SEGMENT` 型別差異正確顯示 |  | 未執行 |  |
| UAT-002 | 欄位血緣與摘要 JSON | 直接、間接影響與 `expected.json` 相符 |  | 未執行 |  |
| UAT-003 | M365 Copilot 摘要解讀 | 回覆符合 JSON 證據，不補造影響 |  | 未執行 |  |
| UAT-004 | Parser warning 不確定性 | 警告、限制與人工覆核要求未遺漏 |  | 未執行 |  |
| UAT-005 | CSV／TSV 編碼與邊界資料 | 各 fixture 的欄位與資料內容可正確匯入 |  | 未執行 |  |
| UAT-006 | SQL 方言與大型輸出 | 五種方言可產生正確輸出；SQL Server 分塊符合預期 |  | 未執行 |  |

## 相關文件

- [Colab 自動化測試與手動 Notebook 操作指南](../colab/docs/testing-guide.md)
- [合成 UAT fixture 詳細說明](../sql-spa-tools-main/uat-fixtures/README.md)
- [Copilot Chat 固定提示](../參賽準備/Copilot%20Chat%20固定提示.md)
