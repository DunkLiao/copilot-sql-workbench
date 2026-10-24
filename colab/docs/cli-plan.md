# Colab CLI 自動測試版本規劃

日期：2026-10-24。狀態：CLI 與操作文件已實作；尚未在真實 Colab runtime 完成端到端驗證。

## 目標與既有基礎

從本機一個命令完成「打包專案 → 上傳 Colab → 安裝環境 → 執行測試 → 下載成果 → 驗證 → 釋放本次資源」。首次登入或憑證失效仍需使用者完成授權，不承諾完全免登入。

本規劃依據 `colab/docs/testing-guide.md`、`colab/docs/setup.md`、`colab/sql_tools_test_framework.ipynb`、`colab/testing/runner.py`、`colab/testing/framework.py` 與 `colab/close_colab_sessions.py`。

- 現有 runner 已提供 `--mode`、`--seed`、`--project-dir`、`--output-dir`、`--skip-browser`、`--skip-performance`，直接重用測試及報表邏輯。
- 預設 full：1,000 組合成案例、種子 `20261023`；quick：50 組。`prepared` 只能代表案例已產生，不能算成通過。
- Notebook 負責互動上傳、環境安裝、呼叫 runner 和下載；CLI 需取代 `files.upload()`／`files.download()`，不能直接照跑互動 Notebook。
- 保留 Excel、CSV、JSON、PNG、SVG、fixtures 與完整 ZIP。報表配色仍遵循根目錄 `theme.md`。
- 現有關閉腳本會關閉帳號所有 sessions，不適合直接用於本流程的自動清理。

## 技術路線

| 方案 | 優點 | 取捨 |
| --- | --- | --- |
| 官方 CLI 分階段 `new / upload / exec / download / stop`（建議） | 沿用已設定工具，可獨立重試下載與保存失敗成果 | 需自行管理狀態、逾時和清理 |
| 官方 `colab run` | 單次腳本執行較簡單 | 須先驗證目前版本的輸出收集及失敗釋放順序，否則可能來不及取回成果 |
| Colab Enterprise | 適合組織正式批次作業 | 需另外設定可計費 GCP 專案、權限與儲存桶，不作本次預設 |

建議採第一項；此為規劃建議，並非使用者已選定。無須以瀏覽器自動點選來代替現有 CLI，也不把自行串接白名單 REST API 當作前置條件。

平台基準：本機查得 `google-colab-cli 0.7.5`，但官方目前僅支援 Linux/macOS。Windows 原生登入成功不等於 upload、exec、download 可用。先驗證命令與小檔案往返；Windows 若不相容，改用 WSL Linux 的獨立 Python/CLI 環境與授權，不複製 Windows token。WSL 是建議執行環境，仍須實測，不能宣稱已驗證。

## 使用介面（以下為待實作命令）

```powershell
# 檢查平台、CLI 版本、必要子命令與專案結構；不建立 runtime
python colab/run_colab_tests.py doctor

# 完整測試：預設 CPU、固定種子，首次執行可能需互動登入
python colab/run_colab_tests.py run --mode full

# 快速測試仍包含瀏覽器與小規模效能測試
python colab/run_colab_tests.py run --mode quick

# 明確略過項目，報告仍應標示 skipped
python colab/run_colab_tests.py run --mode quick --skip-browser --skip-performance

# 遠端已執行完成，但下載中斷時，只重試取回成果
python colab/run_colab_tests.py download --run-id <識別碼>
```

共通選項：`--cli-path` 指定執行檔、`--project-dir` 預設儲存庫根目錄、`--output-dir` 預設 `colab/outputs/cli/<run-id>/`。run 選項：`--seed 20261023`、`--timeout 3600`（秒，涵蓋建立至遠端完成）、`--keep-session`。不自動啟用 GPU、高記憶體或 Enterprise。第一版只建立專屬 session，不附掛既有 session，避免誤用其他作業。

## 執行與成果契約

1. **預檢**：確認 CLI 可用、子命令參數、授權模式與平台；憑證失效時明確要求重新授權，不在背景永久等待。檢查原始碼、runner、requirements、theme 是否存在。
2. **打包**：以明確允許清單包含 `sql-spa-tools-main/` 的程式、靜態資源與測試、`colab/testing/`、`colab/requirements.txt`、遠端執行腳本、根目錄 `theme.md`。保持專案根結構。排除 `.git`、相依套件、outputs、快取、憑證、`.env` 與 `參賽準備/`。列出檔案 manifest、大小及 ZIP SHA-256；拒絕指向根目錄外的 symlink。
3. **建立 session**：使用唯一名稱 `sqlspa-<run-id>`、CPU，保存本次擁有權與遠端路徑。建立回應不明時先對帳，不盲目重建。
4. **上傳**：將專案 ZIP、工作參數 JSON 上傳至本次專屬路徑；遠端先驗證雜湊，安全解壓，拒絕絕對路徑及 `../` 越界檔案。
5. **執行**：`exec -f` 傳送無互動的 bootstrap。安裝 requirements、Node.js 22、中文字型、Playwright Chromium 與 Linux 相依套件；驗證中文字型可用，設定 `SQLSPA_NODE_BIN`。依既有 Notebook 行為執行 runner，明確指定輸出目錄。
6. **發布成果**：記錄 runner exit code，不能只看 CLI exec 成功。遠端在 `finally` 保留 stdout/stderr、工作狀態及可取得的成果。報告成功產生時發布 `test-results.zip` 的 SHA-256、大小、runner run_id 與 orchestration run_id；工作狀態 JSON 最後以原子更名發布。安裝失敗時只產生診斷包，不偽造測試報告。
7. **下載及驗證**：先讀工作狀態，再將成果下載為 `.part`；核對大小、SHA-256、ZIP CRC、預期檔案，通過後原子更名。預期包含 `test-report.xlsx`、`results/results.json`、`results/results.csv`、`results/performance-summary.json`、`charts/`、`fixtures/`；略過測試時依既有報表契約驗證，不把空效能資料視為傳輸損壞。
8. **清理**：完整成果或診斷資料已取回且驗證後，才停止本次建立的 session。`--keep-session` 或下載失敗時保留 session 與重試指令；提示 runtime 終止後無法補下載。停止失敗須標示 `cleanup_failed`，不可回報已釋放，也不可呼叫「關閉所有 sessions」腳本。

狀態依序為 `prepared → provisioned → uploaded → running → remote_finished → downloaded → verified → cleaned`。失敗保留最後成功階段與分類原因。CLI 失聯或逾時不代表遠端已停止；先重新查詢工作狀態，只允許下載重試，不自動重跑測試。使用者中斷同樣保留 session 識別與取回方法，不誤殺其他 session。

建議本機輸出：

```text
colab/outputs/cli/<run-id>/
  source-manifest.json
  run-state.json
  remote-status.json
  bootstrap.log
  runner.stdout.log
  runner.stderr.log
  test-results.zip       # 報告有產生且下載驗證成功時
  diagnostics.zip        # 環境或執行器提前失敗時
```

`run-state.json` 僅存識別碼、session 名稱、階段、時間、來源雜湊、參數及成果路徑，不存 token。以 UTF-8 寫入；日誌需遮蔽憑證。並行作業以 UUID 區分，禁止覆寫其他 run 的成果。

退出碼：`0` 測試通過且下載驗證成功；`1` 測試失敗但報告已取回；`2` 參數／平台／授權預檢失敗；`3` 遠端建立、環境或執行故障；`4` 下載或驗證失敗；`5` 逾時；`6` 資源清理失敗；`130` 使用者中斷。多重故障以傳輸／基礎設施故障優先於測試失敗，所有原因另存狀態檔；已存在更主要錯誤時，清理錯誤不覆蓋它。

## 預計新增與修改檔案

| 路徑 | 責任 |
| --- | --- |
| `colab/run_colab_tests.py` | argparse 入口、doctor/run/download、退出碼與狀態流程 |
| `colab/automation/cli_adapter.py` | 以 subprocess 參數陣列呼叫官方 CLI、逾時與錯誤分類；不依賴其私有 Python API |
| `colab/automation/package.py` | 專案允許清單打包、manifest、雜湊與下載驗證 |
| `colab/automation/state.py` | 狀態序列化、原子寫入、作業擁有權 |
| `colab/automation/remote_bootstrap.py` | 無互動安裝、runner 呼叫、診斷及成果發布 |
| `colab/automation/__init__.py` | 套件入口 |
| `colab/tests/test_cli_automation.py` | 不需真實 Colab 的流程及故障測試 |
| `colab/docs/testing-guide.md` | 新增 CLI 操作、輸出、退出碼與補下載說明 |
| `colab/docs/setup.md` | 記錄實際驗證的版本、平台及授權步驟；區分既有歷史紀錄與新驗證 |

預設不修改 runner 的測試判定和 framework 的報表內容，不必重構既有 Notebook 才能交付第一版。若發現成果契約不足，再單獨修改 runner 並驗證原本 Notebook 相容性。

## 分階段工作與驗收

- [ ] **P0：相容性驗證**。讀取本機 `--help` 確認版本的命令參數與授權模式，再於實作驗證階段建立專屬 CPU session，完成一個小檔上傳、Python 執行、下載比對及單一 session 停止。原生 Windows 不通則改 WSL；此關未通過，不宣稱方案已可執行。鎖定驗證成功版本，不逕用上游 main 的新功能。
- [ ] **P1：本機打包與狀態**。測試包含必要三部分（應用程式、測試框架、theme），排除憑證與舊成果；中文／空白路徑、symlink 越界與並行 run 不互相覆寫。執行 `python -m unittest discover -s colab/tests -v`。
- [ ] **P2：遠端工作腳本**。以假 runner 驗證正常、exit=1、安裝失敗、無報告、狀態寫入中斷；失敗時仍保存診斷。整合既有環境安裝步驟，確保全程無檔案選擇器或下載彈窗。
- [ ] **P3：CLI 編排**。以 fake adapter 驗證命令順序、建立逾時對帳、下載重試不重跑、錯誤退出碼、校驗失敗不釋放、停止只作用於本次 session。對 CLI 回應無法解析時明確失敗，不用第一個 active session 猜測。
- [ ] **P4：真實 quick 端到端**。執行 50 案例，取回 ZIP 並檢查 Excel／圖表／機器可讀成果，確認兩端雜湊一致、來源版本一致、`prepared` 未算通過。測試失敗情境亦需驗證報告可下載。
- [ ] **P5：完整測試與文件交付**。執行 full，核對 1,000 合成案例、10 支 Node 契約測試、12 工具頁檢查，以及 Formatter 100／1,000／10,000 份、每規模五次效能紀錄。驗證 `--keep-session`、補下載與正常清理；更新指南後檢查 `git diff --check`。

完整測試的「案例數」並非全部工具功能斷言數；個資編碼與工具覆蓋限制沿用 testing-guide，不在 CLI 改版中擴大宣稱。效能測試只代表當次 Colab 環境的 Formatter，無法保證跨 runtime 可直接比較。

## 查證來源與未驗證事項

- [官方 CLI 原始碼與命令索引](https://github.com/googlecolab/google-colab-cli)：確認分階段命令與 Linux/macOS 平台限制。
- [Google 官方 CLI 發布文章](https://developers.googleblog.com/introducing-the-google-colab-cli/)：確認官方遠端執行與成果回收用途。
- [Colab API 說明](https://developers.google.com/colab/api/reference/rest)：自行串接 REST API 有白名單限制，不能推論官方 CLI 也無法使用。
- [Enterprise Notebook 執行](https://docs.cloud.google.com/colab/docs/schedule-notebook-run)：作為替代方案背景。

本次只讀取文件與本機套件資訊，未建立 Colab session、上傳專案、執行測試或下載雲端報告。官方 main 文件可能與已裝 0.7.5 不同；實作前須以該版本 help／原始碼驗證。Windows 原生端到端支援、授權有效性與目前可用配額均未確認。
