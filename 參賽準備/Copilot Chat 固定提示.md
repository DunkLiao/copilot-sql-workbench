# M365 Copilot Chat 固定提示

提示版本 1.1，用於合成案例 `copilot-impact-demo-001`。每次試次都使用相同提示與同一版 JSON；不要在試次間增加臨時指示。輸入可使用附件或在訊息中貼上完整 JSON，並在紀錄中註明方式。

## 固定提示文字

```text
請使用繁體中文，根據我提供的 SQL SPA Tools 欄位血緣摘要 JSON（附件或以下貼上的內容）整理變更影響評估。若 JSON 的 changes 有項目，將它們列為操作者輸入的變更背景，並遵守其來源與驗證標記。

請遵守以下規則：
1. 先確認 schemaVersion 是否為 1.0；若 JSON 缺漏、無法讀取或版本不支援，先說明問題並要求重新提供，不要猜測內容。
2. 影響物件、欄位、關係與證據只能逐項取自 JSON 的 impacts。changes 非空時，impacts 已按輸入來源欄位篩選；保留原始名稱與 evidence，不要新增、改名、合併或推測相依關係。
3. changes 若含有 origin=operator_entered 或 verification=not_verified_by_tool，必須標示為操作者輸入、工具未驗證的背景；不要稱為工具比對結果。若 changes 為空，說明 JSON 沒有提供變更欄位背景，不要自行推測。
4. 檢查 analysisMessages。若 warn 或 error 數量大於 0，清楚列出等級與數量，說明摘要不包含訊息全文，要求工程師回到 SQL SPA Tools 本機檢視詳細解析訊息；此時不得把影響清單描述為完整。
5. 若 impacts 為空，請說「目前摘要中沒有找到影響關係」，並說明結果只涵蓋目前載入且可靜態解析的 SQL。不得說「沒有影響」或暗示全行程式與報表均已排除。
6. 逐字保留 limitations 的限制。把測試或審查事項標為建議檢核，不要說成已執行、已確認或已核准。
7. 不得要求或推導客戶資料、帳號、身分證字號、連線資訊或其他機敏資料；不要執行 SQL、批准變更或提出部署已完成的結論。

請依序輸出：
A. 變更背景（有 changes 時依來源標示為操作者輸入且未由工具驗證；沒有時說明缺少背景）
B. JSON 分析摘要：列出物件、欄位、直接／間接關係及逐項 evidence
C. 警告、錯誤、涵蓋範圍與 limitations
D. 工程師待確認事項
E. 上線前建議檢核清單（每項標為建議，不宣稱已完成）
F. 一句人工覆核聲明：此摘要不等於變更核准、測試完成或部署許可
```

## 演練資料

- 正常案例：[`copilot-impact-demo/expected.json`](../sql-spa-tools-main/uat-fixtures/copilot-impact-demo/expected.json)；摘要應包含兩個預期影響且沒有解析警告。
- 解析警告案例：[`parser-warning.sql`](../sql-spa-tools-main/uat-fixtures/copilot-impact-demo/parser-warning.sql)；分析摘要預期顯示 `warn: 1`。提示要求 Copilot 說明警告數量、限制與回到本機工具檢視詳細訊息，不把目前影響列視為完整。

提示只約束輸出方式，不能證明 Copilot 一定遵循。每次實際回覆都須按[成效驗證計畫與紀錄](成效驗證計畫與紀錄.md)逐項評分，保留失敗輸出。

Colab 自動化測試只驗證本機工具的契約、頁面載入、部分操作與個資處理；不會呼叫 Copilot Chat，也不驗證模型是否遵守本提示。固定提示的回答品質、附件讀取及銀行核准租用戶行為仍須另行演練。此次 Colab full 執行有 30 項檢查通過；另 1,000 筆是已產生、尚未逐筆執行的案例，不能當作提示測試次數。


