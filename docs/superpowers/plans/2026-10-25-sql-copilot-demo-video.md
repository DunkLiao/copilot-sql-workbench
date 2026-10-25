# SQL Copilot Demo 影片 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 在 `參賽準備/sql-spa-tools-demo-video/` 建立一支 4 分 30 秒、繁體中文、含合成語音旁白的 Remotion 提案 Demo，供 Studio 預覽。

**Architecture:** 獨立 Remotion 專案承載單一 1920×1080、30 fps、270 秒 composition。場景以 React 元件分段，使用共用品牌色 token、固定腳本資料、旁白音檔與字幕；不改動既有 SQL SPA Tools。

**Tech Stack:** Remotion、React、TypeScript、CSS、合成繁體中文語音、Remotion Studio。

**Spec:** `docs/superpowers/specs/2026-10-25-sql-copilot-demo-video-design.md`

## Global Constraints

- 專案放在 `參賽準備/sql-spa-tools-demo-video/`，不改動既有 SQL 工具。
- 畫幅 1920×1080、30 fps、總長精確 270 秒。
- 使用繁體中文；合成物件名稱與 SQL 型別維持原樣。
- 沿用 `theme.md` 色彩語意：石墨黑、冰川藍、雪霧白、暖磚橘、松針綠。
- 只用合成 SQL、合成物件名稱與固定案例，不呈現真實銀行資料。
- 明確呈現變更欄位由操作者依 SQL Compare 人工核對後輸入，工具未驗證 SQL 差異。
- 30 項通過與 1,000 筆 prepared 必須分開呈現；不得宣稱未量測效益或正式環境驗收。
- 可交付 Studio 預覽，不預設渲染 MP4。

## Review Focus

- 270 秒與各段落起訖時間必須一致；在 Studio 時間軸預覽首尾段及段落切點。
- 繁體中文字幕、SQL 識別字與 JSON 字段不可裁切或互相覆蓋；預覽每個場景。
- 旁白要完整覆蓋 8 段，字幕與畫面切換不得早於或晚於相應語句；在 Studio 預覽音訊同步。
- 示意 Copilot 對話不可冒充正式租用戶輸出；畫面需保留「示意」標記。
- 「原始 SQL 留在本機」只描述本機分析與人工確認交接流程；不得暗示已取得銀行上傳核准。

---

### Task 1: 建立獨立 Remotion 專案並啟動 Studio

**Files:**
- Create: `參賽準備/sql-spa-tools-demo-video/` Remotion scaffold
- Create: `參賽準備/sql-spa-tools-demo-video/package.json`
- Create: `參賽準備/sql-spa-tools-demo-video/src/Root.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/index.ts`

**Interfaces:**
- Produces: Remotion entry point and a starter composition named `SqlCopilotDemo` for later scene work.

- [x] 在 `參賽準備/sql-spa-tools-demo-video/` 建立 Remotion blank project，不使用 Tailwind。
- [x] 安裝專案依賴，保留現有根目錄與 SQL 工具檔案。
- [x] 建立初始 `SqlCopilotDemo` composition，尺寸 1920×1080、30 fps、270 秒。
- [x] 啟動 `npx remotion studio --no-open`，在 Codex in-app browser 開啟列出的本機 URL，確認 Studio 與 composition 預覽載入。

### Task 2: 建立共用品牌視覺與場景資料

**Files:**
- Create: `參賽準備/sql-spa-tools-demo-video/src/theme.ts`
- Create: `參賽準備/sql-spa-tools-demo-video/src/data/scenes.ts`
- Create: `參賽準備/sql-spa-tools-demo-video/src/components/SceneFrame.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/components/Subtitle.tsx`
- Modify: `參賽準備/sql-spa-tools-demo-video/src/Root.tsx`

**Interfaces:**
- `theme.ts` exports semantic color constants copied from root `theme.md`.
- `scenes.ts` exports the eight scene durations, headings, subtitle segments and narration text.
- `SceneFrame` accepts title, scene index and `children`; `Subtitle` accepts text and frame-based timing.

- [x] 建立 `scenes.ts` 八段資料，時長依序為 25、30、55、40、35、25、30、30 秒，合計 270 秒。
- [x] 建立 `theme.ts`，逐項採用 `#202A33`、`#70B7D5`、`#365A69`、`#D8E0E6`、`#F7FAFC`、`#25323C`、`#C65D3B`、`#3E7C68`，並沿用 theme.md 色彩語意。
- [x] 建立共用場景框架與字幕元件，所有動畫使用 Remotion frame hooks，確保可依時間軸定位預覽。

### Task 3: 製作八段視覺敘事

**Files:**
- Create: `參賽準備/sql-spa-tools-demo-video/src/scenes/ProblemScene.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/scenes/SecurityFlowScene.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/scenes/ImpactScene.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/scenes/CopilotScene.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/scenes/WarningScene.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/scenes/RegressionScene.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/scenes/MeasurementScene.tsx`
- Create: `參賽準備/sql-spa-tools-demo-video/src/scenes/NextStepsScene.tsx`
- Modify: `參賽準備/sql-spa-tools-demo-video/src/Root.tsx`

**Interfaces:**
- Each scene component accepts `durationInFrames` and uses a local frame timeline starting at frame 0.
- `Root.tsx` registers scenes in design order using `Sequence` and the exact durations from `scenes.ts`.

- [x] 製作人工追查痛點與提案主張的關係節點動畫。
- [x] 製作本機分析、摘要檢查、確認下載與人工交接的安全流程圖。
- [x] 製作正常案例欄位差異與兩個預期下游影響，將未變更 `CUSTOMER_ID` 關係淡化處理。
- [x] 製作操作者輸入與 JSON 證據畫面，標示 `operator_entered`、`not_verified_by_tool` 及「Copilot 回答示意」。
- [x] 製作 PIVOT `IN` 清單解析警告與人工補查提醒。
- [x] 製作 30 項通過、1,000 筆 prepared 的分開數據卡，並加上工具層測試限制。
- [x] 製作至少三組配對量測項目、下一步時程與結尾主張。

### Task 4: 合成繁體中文旁白與同步字幕

**Files:**
- Create: `參賽準備/sql-spa-tools-demo-video/src/data/narration.ts`
- Create: `參賽準備/sql-spa-tools-demo-video/public/audio/` narration assets
- Modify: `參賽準備/sql-spa-tools-demo-video/src/Root.tsx`

**Interfaces:**
- `narration.ts` exports eight narration scripts and matching frame ranges.
- Root composition plays narration audio and corresponding subtitle sequences on a shared 270-second timeline.

- [x] 依既有 Demo 講稿整理八段沉穩、清晰的繁體中文口語旁白，不刪除證據限制。
- [x] 使用可用的合成語音工具產生分段音訊，將音訊檔置於 `public/audio/`。
- [x] 依實際旁白節奏調整字幕與場景進出點，保持總長 270 秒；不加與旁白競爭的音樂。

### Task 5: Studio 全片預覽與事實核對

**Files:**
- Modify: `參賽準備/sql-spa-tools-demo-video/src/` as needed for preview corrections

- [x] 於持續運行的 Remotion Studio 預覽 8 段場景，檢查首尾畫面、段落切點、字幕可讀性與旁白同步。
- [x] 對照設計稿核對所有合成欄位名稱、測試數據標籤、警告限制與租用戶驗收狀態。
- [x] 確認預覽 composition 精確長 270 秒且無畫面溢出；提供 Studio 預覽連結，不輸出 MP4。

