# Google Colab 自動化測試操作指南

## 快速開始

1. 將 `colab/sql_tools_test_framework.ipynb` 上傳或開啟於 Google Colab。
2. 選擇「執行階段 → 全部執行」。
3. 在檔案選擇器上傳完整專案 ZIP；解壓後的根目錄必須同時包含 `sql-spa-tools-main/` 與 `colab/`（測試執行器位於 `colab/testing/runner.py`）。請上傳此儲存庫根目錄打包的 ZIP，不要只壓縮 `sql-spa-tools-main/`。也可先在 Notebook 設定 `SOURCE_URL` 指向可讀取的 Git URL。
4. 完成後下載輸出的 `test-results.zip`。成果也會保留在目前 Colab 執行階段的 `colab/outputs/<執行識別碼>/`。

預設完整模式以固定種子 `20261023` 產生 1,000 組案例。可在 Notebook 設定區選 `quick` 進行 50 案例快速檢查。完整模式會安裝 Node.js 22、Chromium 與中文字型，執行 10 支既有 Node 契約測試、12 個工具頁載入檢查，並對 Formatter 字串保留、Compare 欄位型別差異、Catalog CTE 解析、關聯探索器 CSV 匯入及 PII 掃描位元組區間進行瀏覽器驗證；另以 Formatter 實際函式逐份處理 100／1,000／10,000 份 SQL，暖機一次並量測五次。

## CLI 自動執行

原有 Notebook 手動流程繼續保留。若要從本機自動執行，可使用新增的 `colab/run_colab_tests.py`：它會打包應用程式與測試框架、上傳至 Google Colab、執行相同 runner，下載並驗證報告 ZIP，最後只停止本次建立的工作階段。

官方 `google-colab-cli` 目前支援 Linux 與 macOS，尚未正式支援 Windows。本機 Windows 若能使用 `colab sessions`，不代表上傳、執行及下載均相容；建議先用 `doctor` 檢查，再以 quick 模式驗證。Windows 操作失敗時，請改在 WSL 安裝與登入 CLI。Colab CLI 首次登入會在終端顯示授權網址並要求輸入一次性授權碼。

在儲存庫根目錄執行：

```powershell
# 檢查專案、Python 與 CLI 子命令，不會建立遠端工作階段
python colab/run_colab_tests.py doctor

# 完整測試，預設 1,000 案例與種子 20261023
python colab/run_colab_tests.py run --mode full

# 快速測試，50 案例，仍執行瀏覽器與小規模效能檢查
python colab/run_colab_tests.py run --mode quick

# 快速除錯時略過瀏覽器及效能測試
python colab/run_colab_tests.py run --mode quick --skip-browser --skip-performance
```

預設成果存放在 `colab/outputs/cli/<run-id>/`。其中 `test-results.zip` 是完整報告；`source-manifest.json` 記錄本次上傳來源，`run-state.json` 記錄階段與結果，CLI 命令及遠端 runner 輸出保存在日誌。封裝會保留根目錄 `theme.md`、工具頁、測試及 `uat-fixtures/`，排除 Git 資料、環境憑證與舊輸出。請勿手動上傳該目錄中的 `source.zip` 以外內容到公開位置，尤其不要把狀態檔與日誌分享給未授權的人。

如果下載中斷，狀態檔會列出 run-id。Colab 工作階段仍存在時，可以重試下載，不會重跑測試：

```powershell
python colab/run_colab_tests.py download --run-id <run-id>
```

若執行時使用自訂輸出目錄，補下載時須帶相同路徑：

```powershell
python colab/run_colab_tests.py download --run-id <run-id> --output-dir D:\test-output
```

預設在報告下載並驗證後停止本次建立的 session。使用 `--keep-session` 可保留 session，供檢查 Colab 遠端環境；完成後請自行使用 `colab stop --session <session-name>` 停止。若下載或驗證失敗，工具會保留 session 讓你補下載。Colab runtime 若已被平台終止，暫存成果可能無法取回。

退出碼 `0` 表示測試成功且成果已驗證；`1` 表示測試有失敗但報告已下載；`2` 表示參數、平台或登入預檢問題；`3` 表示遠端環境或執行錯誤；`4` 表示下載或成果驗證失敗；`5` 表示逾時；`6` 表示停止工作階段失敗；`130` 表示使用者中斷。測試失敗報告仍會保存在本機，請依 Excel「失敗與限制」及 `results/results.json` 判讀。

## 成果解讀

- `test-report.xlsx` 提供總覽、模組覆蓋、案例明細、個資指標、效能結果、失敗與限制、執行資訊。
- `results/results.json` 與 `results/results.csv` 保存逐項測試紀錄；狀態中的 `prepared` 表示合成案例已產生並保留，尚未代表已對應工具執行。
- `results/performance-summary.json` 與 Excel 效能工作表列出各規模的 P50、P95 和吞吐量。
- `charts/` 產生簡報可用 PNG 與 SVG 圖表；配色依根目錄 `theme.md`。
- `fixtures/` 保存案例與預期答案，`test-results.zip` 包含完整輸出。
- 個資指標以合成 SQL 中預期類型及字元區間比對；現階段資料內容使用 UTF-8，編碼差異測試仍待擴充。效能數據只代表 Formatter 的 `formatText` 處理批次 SQL 的結果。
- 瀏覽器檢查驗證頁面載入、標題、主題切換元件、回首頁連結、未處理 JavaScript 例外，以及上述主要功能流程；它不涵蓋每個工具的所有選項與錯誤路徑。
- Colab 的執行環境與資源會變動；效能數值應連同執行資訊解讀，不宜跨環境直接比較。

## 本機維護

```bash
python -m pip install -r colab/requirements.txt
python -m playwright install chromium
python -m unittest discover -s colab/tests -v
python colab/testing/runner.py --mode quick --skip-browser --skip-performance
```

完整瀏覽器測試建議於 Colab Linux 執行。`--skip-browser` 與 `--skip-performance` 適用於快速除錯；被略過的項目會標示為 skipped。
