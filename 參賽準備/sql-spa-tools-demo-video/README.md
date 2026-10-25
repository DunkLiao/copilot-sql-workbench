# SQL SPA Tools × M365 Copilot Chat｜4 分 30 秒 Demo 影片

這是黑客松提案的 Remotion 影片專案。影片以固定合成 SQL 案例說明本機欄位血緣分析、人工確認後的 JSON 交接、Copilot 整理示意、解析警告、技術回歸與後續量測計畫。影片中的示意卡片並非銀行正式環境畫面。

## 完成影片

[SQL SPA Tools 提案 Demo（4 分 30 秒）](../參賽文件/SQL_SPA_Tools_提案Demo_4分30秒.mp4) 已輸出為 1920×1080、30 fps 的 H.264／AAC MP4。可直接播放或作為參賽影片素材。

## 開啟預覽

```powershell
cd 'D:\VIbeCoding\copilot-sql-workbench\參賽準備\sql-spa-tools-demo-video'
npm install
npx remotion studio --no-open
```

在 Studio 開啟 `SqlCopilotDemo`。Composition 為 1920×1080、30 fps、8100 frames，長度正好 4 分 30 秒，包含八段合成繁體中文旁白與同步字幕。`public/audio/` 已含播放所需音檔，預覽不需要重製語音。

## 修改旁白與字幕

在 `src/data/narration.json` 修改八段講稿。重新合成語音並依語音服務回傳的句子時間標記產生字幕：

```powershell
python -m pip install -r scripts/requirements.txt
python scripts/generate_narration.py
```

此步驟會將講稿文字送至線上合成語音服務；只應使用核准的合成展示文字。長句中的字幕時間再依字數細分，修改講稿後應在 Studio 人工檢視同步。

## 事實來源與展示界線

- 提案主軸：`../黑客松提案報告.md`
- 逐段時間與案例：`../3至5分鐘Demo講稿.md`
- 合成 SQL：`../../sql-spa-tools-main/uat-fixtures/copilot-impact-demo/`
- 配色：`../../theme.md`

正常案例的兩個預期影響欄位是 `DEMO_MONTHLY_REPORT.SEGMENT_LABEL` 與 `DEMO_RISK_SEGMENTATION.RISK_BUCKET`。變更欄位由操作者依 SQL Compare 人工核對後輸入，工具未自行驗證差異。影片中的 30 項通過為工具層檢查；1,000 筆案例仍為 `prepared`。銀行核准租用戶、JSON 附件流程與效益數據仍待驗證。
