from __future__ import annotations

import argparse
import json
from importlib.metadata import PackageNotFoundError, version
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    from .framework import MODULES, PAGE_FILES, generate_cases, source_fingerprint, write_report, pii_metrics
except ImportError:  # Support direct `python colab/testing/runner.py` execution.
    from framework import MODULES, PAGE_FILES, generate_cases, source_fingerprint, write_report, pii_metrics

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "sql-spa-tools-main"
NODE_TESTS = {
    "test-theme.js": "共用介面",
    "test-excel-csv-sql.js": "Excel／CSV 轉 SQL",
    "test-excel-csv-sql-cte.js": "Excel／CSV 轉 SQL CTE",
    "test-sqlscriptmanage.js": "SQLScriptManage",
    "test-schema-studio.js": "SQL 欄位映射",
    "test-copilot-export.js": "Copilot 摘要匯出",
    "test-copilot-impact-demo.js": "SQL 欄位血緣分析器",
    "test-data-quality-audit-center.js": "資料品質稽核中心",
    "test-pii-cleaner.js": "SQL 個資清除器",
    "test-sql-lab.js": "SQL Lab",
}
NODE_BIN = os.environ.get("SQLSPA_NODE_BIN") or shutil.which("node") or "node"


def run_node_contracts(timeout: int = 600) -> list[dict]:
    if not Path(NODE_BIN).exists() and not shutil.which(NODE_BIN):
        return [{"module": module, "level": "node-contract", "status": "error", "error": "找不到 Node.js"}
                for module in sorted(set(NODE_TESTS.values()))]
    rows = []
    for script, module in NODE_TESTS.items():
        started = time.perf_counter()
        try:
            proc = subprocess.run([NODE_BIN, str(APP / "tests" / script)], cwd=APP, text=True, encoding="utf-8", errors="replace",
                                  capture_output=True, timeout=timeout, check=False)
            status = "passed" if proc.returncode == 0 else "failed"
            rows.append({"case_id": script, "module": module, "level": "node-contract", "status": status,
                         "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                         "details": (proc.stdout + proc.stderr).strip()[-3000:],
                         "error": "" if status == "passed" else f"exit={proc.returncode}"})
        except subprocess.TimeoutExpired as exc:
            rows.append({"case_id": script, "module": module, "level": "node-contract", "status": "error",
                         "duration_ms": round((time.perf_counter() - started) * 1000, 2), "error": f"timeout: {exc}"})
    return rows


def node_version() -> str:
    try:
        proc = subprocess.run([NODE_BIN, "--version"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=10, check=False)
        return proc.stdout.strip() or f"unavailable (exit={proc.returncode})"
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"unavailable ({exc})"


def run_browser_smoke(cases: list | None = None, timeout_ms: int = 30000) -> tuple[list[dict], dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return ([{"module": "共用介面", "level": "browser-smoke", "status": "error",
                  "error": "缺少 Playwright；請安裝 requirements.txt"}], pii_metrics(0, 0, 0))

    rows = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        pii_summary = pii_metrics(0, 0, 0)
        for module, filename in PAGE_FILES.items():
            page = context.new_page()
            page_errors: list[str] = []
            page.on("pageerror", lambda error, sink=page_errors: sink.append(str(error)))
            started = time.perf_counter()
            try:
                response = page.goto(f"file:///{(APP / filename).as_posix()}", wait_until="domcontentloaded", timeout=timeout_ms)
                page.wait_for_timeout(350)
                title = page.title()
                h1 = page.locator("h1").first.inner_text(timeout=3000)
                has_toggle = page.locator("#themeToggle").count() == 1
                has_home = page.locator("a.home-link[href='index.html']").count() == 1
                ok = bool(response and response.ok and title and h1 and has_toggle and has_home and not page_errors)
                rows.append({"case_id": filename, "module": module, "level": "browser-smoke", "status": "passed" if ok else "failed",
                             "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                             "details": f"title={title}; h1={h1}; themeToggle={has_toggle}; homeLink={has_home}; pageErrors={page_errors}"})
                if module == "Oracle SQL Formatter":
                    result = page.evaluate("() => { const r = formatText(\"select 'keep;semi' as label from synth_table where id = 1;\", opt()); return {ok:r.ok, out:r.out}; }")
                    passed = result["ok"] and "'keep;semi'" in result["out"] and "SELECT" in result["out"]
                    rows.append({"case_id": "formatter-preserves-literal", "module": module, "level": "browser-functional",
                                 "status": "passed" if passed else "failed", "details": json.dumps(result, ensure_ascii=False)})
                elif module == "Oracle SQL Compare":
                    page.locator("#txtA").fill("CREATE TABLE SYNTH_T (ID NUMBER, LABEL VARCHAR2(20));")
                    page.locator("#txtB").fill("CREATE TABLE SYNTH_T (ID NUMBER, LABEL VARCHAR2(40));")
                    page.locator("#btnCompare").click()
                    page.wait_for_function("document.querySelector('#stats')?.innerText !== '尚未比對'", timeout=timeout_ms)
                    diff_text = page.locator("#resultBody").inner_text()
                    passed = "VARCHAR2(20)" in diff_text and "VARCHAR2(40)" in diff_text
                    rows.append({"case_id": "compare-column-type-change", "module": module, "level": "browser-functional",
                                 "status": "passed" if passed else "failed", "details": diff_text[:1200]})
                elif module == "SQL Catalog":
                    found = page.evaluate("() => parseSql('WITH Q AS (SELECT * FROM APP.CUSTOMERS) SELECT * FROM Q JOIN APP.ACCOUNTS A ON A.ID=Q.ID').tables")
                    passed = found == ["APP.ACCOUNTS", "APP.CUSTOMERS"]
                    rows.append({"case_id": "catalog-cte-table-discovery", "module": module, "level": "browser-functional",
                                 "status": "passed" if passed else "failed", "details": json.dumps(found)})
                elif module == "資料關聯探索器":
                    csv_data = b"CUSTOMER_ID,SEGMENT\nC001,RETAIL\nC002,BUSINESS\n"
                    page.locator("#fileInput").set_input_files({"name": "SYNTH_CUSTOMERS.csv", "mimeType": "text/csv", "buffer": csv_data})
                    page.locator("#impOk").wait_for(timeout=timeout_ms)
                    page.wait_for_function("document.querySelector('#impBody')?.innerText.includes('CUSTOMER_ID')", timeout=timeout_ms)
                    page.locator("#impOk").click()
                    page.wait_for_function("S.tables.some(t => t.name === 'SYNTH_CUSTOMERS' && t.rowCount === 2)", timeout=timeout_ms)
                    rows.append({"case_id": "relationship-explorer-csv-import", "module": module, "level": "browser-functional",
                                 "status": "passed", "details": "匯入合成 CSV 後建立 2 筆資料的 SYNTH_CUSTOMERS 表格"})
                if module == "SQL 個資清除器" and cases:
                    pii_cases = [case for case in cases if case.category == "pii"]
                    content = "\n".join(case.sql for case in pii_cases)
                    expected_ranges = []
                    expected_masks = []
                    cursor = 0
                    for case in pii_cases:
                        for hit in case.expected["pii"]:
                            start = cursor + case.sql.index(hit["value"])
                            expected_ranges.append((hit["type"], start, start + len(hit["value"])))
                            value = hit["value"]
                            masked = (value[:3] + "****" + value[-3:] if hit["type"] == "id" else
                                      value[:2] + "****" + value[-2:] if hit["type"] == "ban" else
                                      value[:4] + "*" * (len(value) - 8) + value[-4:])
                            expected_masks.append((hit["type"], masked))
                        cursor += len(case.sql) + 1
                    with tempfile.TemporaryDirectory(prefix="sqlspa-pii-") as folder:
                        (Path(folder) / "synthetic.sql").write_bytes(content.encode("utf-8"))
                        page.locator("#dirInput").set_input_files(folder)
                        page.locator("#tbl tbody tr").first.wait_for(timeout=timeout_ms)
                        page.wait_for_function("document.querySelector('#status')?.innerText.includes('掃描完成')", timeout=timeout_ms)
                        page.wait_for_timeout(150)
                        checked_rejected = page.evaluate("state.files.length===1 && state.files[0].res.nId===0")
                        page.locator("#optChk").uncheck()
                        page.locator("#btnRescan").click()
                        expected_id_count = sum(1 for case in pii_cases for hit in case.expected["pii"] if hit["type"] == "id")
                        page.wait_for_function("([expected]) => !state.busy && state.files.length===1 && state.files[0].res.nId===expected",
                                               arg=[expected_id_count], timeout=timeout_ms)
                    actual_ranges = page.evaluate("state.files.flatMap(f => (f.res?.hits || []).map(h => [h.type, h.bs, h.be]))")
                    actual_set = {tuple(item) for item in actual_ranges}
                    expected_set = set(expected_ranges)
                    actual_masks = page.evaluate("state.files.flatMap(f => (f.res?.hits || []).map(h => [h.type, h.masked]))")
                    mask_ok = set(map(tuple, actual_masks)) == set(expected_masks)
                    expected_clean = content
                    for _, start, end in sorted(expected_ranges, key=lambda item: item[1], reverse=True):
                        expected_clean = expected_clean[:start] + expected_clean[end:]
                    strip_check = page.evaluate("expected => { const f=state.files[0]; const cleaned=new TextDecoder('utf-8').decode(stripRanges(f.bytes, f.res.hits)); return cleaned===expected; }",
                                                 expected_clean)
                    tp = len(actual_set & expected_set)
                    fp = len(actual_set - expected_set)
                    fn = len(expected_set - actual_set)
                    pii_summary = pii_metrics(tp, fp, fn)
                    pii_ok = fp == 0 and fn == 0
                    rows.append({"case_id": "synthetic-pii-batch", "module": module, "level": "browser-pii-counts",
                                 "status": "passed" if pii_ok else "failed",
                                 "details": f"expected_range_count={len(expected_set)}; actual_range_count={len(actual_set)}; metrics={pii_summary}"})
                    rows.append({"case_id": "synthetic-pii-mask-patterns", "module": module, "level": "browser-pii-mask",
                                 "status": "passed" if mask_ok else "failed", "details": f"expected_masks={len(expected_masks)}; matched={len(set(map(tuple, actual_masks)) & set(expected_masks))}"})
                    rows.append({"case_id": "synthetic-pii-checksum-filter", "module": module, "level": "browser-pii-checksum",
                                 "status": "passed" if checked_rejected else "failed", "details": "預設啟用檢查碼時，拒絕格式相符但檢查碼無效的合成身分證"})
                    rows.append({"case_id": "synthetic-pii-byte-removal", "module": module, "level": "browser-pii-redaction",
                                 "status": "passed" if strip_check else "failed", "details": "清除命中區間後與獨立計算的預期內容逐位元組相同" if strip_check else "清除後內容不符預期"})
            except Exception as exc:
                rows.append({"case_id": filename, "module": module, "level": "browser-smoke", "status": "error",
                             "duration_ms": round((time.perf_counter() - started) * 1000, 2), "error": str(exc)})
            finally:
                page.close()
        browser.close()
    return rows, pii_summary


def run_performance(cases: list, repetitions: int = 5, sizes: tuple[int, ...] = (100, 1000, 10000), timeout_s: int = 120) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return [{"module": "Oracle SQL Formatter", "size": size, "duration_ms": 0,
                 "throughput_per_second": 0, "status": "error", "note": "缺少 Playwright"} for size in sizes]
    sql_bank = [case.sql or "SELECT 1 FROM DUAL;" for case in cases]
    source = "\n".join(sql_bank)
    rows = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{(APP / PAGE_FILES['Oracle SQL Formatter']).as_posix()}", wait_until="domcontentloaded")
        for size in sizes:
            batch = [sql_bank[i % len(sql_bank)] for i in range(size)]
            page.evaluate("sqls => formatText(sqls[0],opt()).ok", batch[:1])  # 每個規模先暖機一次
            for run in range(repetitions):
                started = time.perf_counter()
                try:
                    data = page.evaluate("([sqls, limitMs]) => { const start=performance.now(); let failures=0, chars=0; for (const sql of sqls) { const result=formatText(sql,opt()); chars+=sql.length; if (!result.ok) failures++; } const elapsed=performance.now()-start; return {elapsed, failures, chars, timedOut:elapsed>limitMs}; }",
                                         [batch, timeout_s * 1000])
                    elapsed = float(data["elapsed"]) / 1000
                    rows.append({"module": "Oracle SQL Formatter", "size": size, "run": run + 1,
                                 "duration_ms": round(elapsed * 1000, 3),
                                 "throughput_per_second": round((size - data["failures"]) / elapsed, 2) if elapsed else 0,
                                 "status": "passed" if data["failures"] == 0 and not data["timedOut"] else "failed",
                                 "note": f"逐份呼叫實際 formatter formatText；{data['chars']} 字元；失敗 {data['failures']} 份"})
                except Exception as exc:
                    rows.append({"module": "Oracle SQL Formatter", "size": size, "run": run + 1,
                                 "duration_ms": round((time.perf_counter() - started) * 1000, 3),
                                 "throughput_per_second": 0, "status": "timeout-or-error", "note": str(exc)})
        browser.close()
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="SQL SPA Tools Colab test framework")
    parser.add_argument("--mode", choices=("quick", "full"), default="full")
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--project-dir", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--skip-browser", action="store_true")
    parser.add_argument("--skip-performance", action="store_true")
    args = parser.parse_args()
    project = args.project_dir.resolve()
    app = project / "sql-spa-tools-main"
    if not app.is_dir():
        parser.error(f"project directory must contain sql-spa-tools-main/: {project}")
    globals()["APP"] = app
    cases = generate_cases(args.seed)
    if args.mode == "quick":
        selected = []
        categories = list(dict.fromkeys(case.category for case in cases))
        for index, category in enumerate(categories):
            selected.extend([case for case in cases if case.category == category][:(8 if index == len(categories) - 1 else 7)])
        cases = selected
    output_dir = args.output_dir or project / "colab" / "outputs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()
    results = run_node_contracts()
    if not args.skip_browser:
        browser_results, pii = run_browser_smoke(cases)
        results.extend(browser_results)
    else:
        pii = pii_metrics(0, 0, 0)
        results.append({"module": "共用介面", "level": "browser-smoke", "status": "skipped", "details": "使用 --skip-browser"})
    # Each synthetic case is indexed and retained. Execution applicability is explicit;
    # full functional assertions use module contracts and browser smoke, not self-oracles.
    for case in cases:
        results.append({"case_id": case.case_id, "module": "、".join(case.modules), "level": "fixture-generation",
                        "status": "prepared", "details": f"category={case.category}; expected={json.dumps(case.expected, ensure_ascii=False)}"})
    perf = [] if args.skip_performance else run_performance(cases, repetitions=1 if args.mode == "quick" else 5,
                                                            sizes=(100,) if args.mode == "quick" else (100, 1000, 10000))
    metadata = {"run_id": run_id, "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
                "seed": args.seed, "mode": args.mode, "source": str(project), "source_sha256": source_fingerprint(app),
                "python": sys.version, "node": node_version(),
                "platform": platform.platform(), "processor": platform.processor(),
                "cpu_count": os.cpu_count(), "browser": "Playwright Chromium" if not args.skip_browser else "skipped",
                "packages": {name: version(name) if _installed(name) else "not-installed"
                             for name in ("matplotlib", "xlsxwriter", "playwright")},
                "limitations": [
                    "瀏覽器檢查驗證全部工具頁載入與共用導覽，並覆蓋主要功能流程；尚未逐項測試所有操作選項及錯誤路徑。",
                    "個資指標以 UTF-8 合成檔案的命中類型與位元組區間逐筆比對；Big5／UTF-16 準確度仍待加入掃描器整合案例。",
                    "效能測試目前量測 Oracle SQL Formatter 實際 formatText 函式，不代表其他模組端到端效能。",
                    "未設定 Oracle 連線；SQL Lab 亦未視為 Oracle 執行器。",
                ]}
    write_report(output_dir, cases, results, metadata, pii, perf)
    print(json.dumps({"run_id": run_id, "output_dir": str(output_dir), "cases": len(cases),
                      "results": len(results), "failed": sum(r.get("status") in ("failed", "error") for r in results)}, ensure_ascii=False))
    return 1 if any(row.get("status") in ("failed", "error", "timeout-or-error") for row in results) or any(
        row.get("status") != "passed" for row in perf
    ) else 0


def _installed(name: str) -> bool:
    try:
        version(name)
        return True
    except PackageNotFoundError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
