from __future__ import annotations

import csv
import hashlib
import json
import random
import shutil
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ft2font import FT2Font
import xlsxwriter

PALETTE = {
    "graphite": "#202A33", "ice": "#70B7D5", "ice_text": "#365A69",
    "silver": "#D8E0E6", "snow": "#F7FAFC", "slate": "#25323C",
    "warning": "#C65D3B", "success": "#3E7C68",
}
CATEGORY_COUNTS = {
    "basic": 150, "joins": 150, "cte_lineage": 150, "oracle_specific": 150,
    "ddl_dml": 150, "pii": 150, "edge_cases": 100,
}
CATEGORY_LABELS = {
    "basic": "基礎查詢", "joins": "JOIN／子查詢", "cte_lineage": "CTE／血緣",
    "oracle_specific": "Oracle 語法", "ddl_dml": "DDL／DML", "pii": "個資案例", "edge_cases": "邊界案例",
}
MODULES = [
    "Oracle SQL Formatter", "Oracle SQL Compare", "SQL 個資清除器", "SQL Catalog",
    "SQL 欄位血緣分析器", "SQLScriptManage", "Excel／CSV 轉 SQL",
    "Excel／CSV 轉 SQL CTE", "SQL 欄位映射", "SQL Lab", "資料品質稽核中心",
    "資料關聯探索器", "Copilot 摘要匯出", "共用介面",
]

# 選取字型時同時驗證報表會用到的中文字形，避免 findfont 靜默回退至缺字字型。
_FONT_PROBE = "".join(CATEGORY_LABELS.values()) + "".join(MODULES) + "合成案例分布案例數測試狀態個資辨識準確性個資誤判與漏判資料規模與耗時吞吐量筆秒"
_CJK_FONT = None
_font_records = sorted(
    font_manager.fontManager.ttflist,
    key=lambda entry: ("noto" not in entry.name.lower(), entry.name.lower(), entry.fname.lower()),
)
_best_font = None
_best_coverage = -1
_probe_chars = set(_FONT_PROBE)
for _record in _font_records:
    try:
        _font_charmap = FT2Font(_record.fname).get_charmap()
    except (OSError, RuntimeError):
        continue
    _coverage = sum(ord(char) in _font_charmap for char in _probe_chars)
    if _coverage > _best_coverage:
        _best_font, _best_coverage = _record, _coverage
    if _coverage == len(_probe_chars):
        _best_font = _record
        break
if _best_font is not None:
    font_manager.fontManager.addfont(_best_font.fname)
    _CJK_FONT = FT2Font(_best_font.fname).family_name
    plt.rcParams["font.family"] = _CJK_FONT
    if _best_coverage < len(_probe_chars):
        _missing_chars = "".join(sorted(char for char in _probe_chars if ord(char) not in FT2Font(_best_font.fname).get_charmap()))
        print(f"警告：字型 {_CJK_FONT} 未涵蓋部分圖表字元：{_missing_chars}；請確認 Colab 已安裝 fonts-noto-cjk。")
else:
    print("警告：找不到中文字型，圖表將使用 Matplotlib 預設字型；請確認 Colab 已安裝 fonts-noto-cjk。")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "path"
PAGE_FILES = {
    "Oracle SQL Formatter": "sql-spa-tools-oracle-formatter.html",
    "Oracle SQL Compare": "sql-spa-tools-sql-compare.html",
    "SQL 個資清除器": "sql-spa-tools-pii-cleaner.html",
    "SQL Catalog": "sql-spa-tools-catalog.html",
    "SQL 欄位血緣分析器": "sql-spa-tools-column-lineage.html",
    "SQLScriptManage": "sql-spa-tools-sqlscriptmanage.html",
    "Excel／CSV 轉 SQL": "sql-spa-tools-excel-csv-sql.html",
    "Excel／CSV 轉 SQL CTE": "sql-spa-tools-excel-csv-sql-cte.html",
    "SQL 欄位映射": "sql-spa-tools-schema-studio.html",
    "SQL Lab": "sql-spa-tools-sql-lab.html",
    "資料品質稽核中心": "sql-spa-tools-data-quality-audit-center.html",
    "資料關聯探索器": "sql-spa-tools-data-relationship-explorer.html",
}


@dataclass(frozen=True)
class SyntheticCase:
    case_id: str
    category: str
    sql: str
    modules: tuple[str, ...]
    expected: dict[str, Any]
    source: str = "deterministic-template"


def _taiwan_id(rng: random.Random) -> str:
    # Build a check-digit-valid synthetic identifier; never sourced from people.
    letters = "ABCDEFGHJKLMNPQRSTUVXYWZIO"
    letter = rng.choice(letters)
    gender = rng.choice("12")
    digits = [int(x) for x in f"{rng.randrange(10000000):07d}"]
    value = letters.index(letter) + 10
    checksum = (value // 10 + (value % 10) * 9 + int(gender) * 8
                + sum(d * w for d, w in zip(digits, [7, 6, 5, 4, 3, 2, 1]))) % 10
    check = ((10 - checksum) % 10 + 1) % 10  # invalid check digit by design; never a real national ID
    return f"{letter}{gender}{''.join(map(str, digits))}{check}"


def _business_id(rng: random.Random) -> str:
    weights = [1, 2, 1, 2, 1, 2, 4]
    for _ in range(100):
        digits = [rng.randrange(10) for _ in range(7)]
        total = sum((d * w) // 10 + (d * w) % 10 for d, w in zip(digits, weights))
        for check in range(10):
            if (total + check) % 5 == 0 or (digits[6] == 7 and (total + check + 1) % 5 == 0):
                return "".join(map(str, digits + [check]))
    raise RuntimeError("could not generate synthetic business identifier")


def _build_sql(category: str, i: int, rng: random.Random) -> tuple[str, dict[str, Any]]:
    table = f"SYNTH_T{i:04d}"
    if category == "basic":
        sql = f"SELECT ID, AMOUNT FROM {table} WHERE STATUS = 'ACTIVE' AND AMOUNT >= {i};"
        expected = {"contains": ["SELECT", table], "statement_count": 1}
    elif category == "joins":
        sql = f"SELECT a.ID, b.LABEL FROM {table} a JOIN SYNTH_LOOKUP b ON b.ID=a.LOOKUP_ID WHERE a.ID={i};"
        expected = {"contains": ["JOIN", "SYNTH_LOOKUP"], "statement_count": 1}
    elif category == "cte_lineage":
        sql = f"WITH SRC AS (SELECT ID, VALUE FROM {table}), AGG AS (SELECT ID, VALUE FROM SRC) SELECT VALUE FROM AGG;"
        expected = {"contains": ["SRC", "AGG"], "source_table": table, "statement_count": 1}
    elif category == "oracle_specific":
        sql = f"SELECT ID, ROW_NUMBER() OVER (PARTITION BY GROUP_ID ORDER BY CREATED_AT) RN FROM {table} CONNECT BY PRIOR ID = PARENT_ID START WITH PARENT_ID IS NULL;"
        expected = {"contains": ["ROW_NUMBER", "CONNECT BY"], "statement_count": 1}
    elif category == "ddl_dml":
        sql = f"CREATE TABLE {table} (ID NUMBER, LABEL VARCHAR2(40));\nALTER TABLE {table} ADD CREATED_AT DATE;"
        expected = {"contains": ["CREATE TABLE", "ALTER TABLE"], "statement_count": 2}
    elif category == "pii":
        national_id = _taiwan_id(rng)
        business_id = _business_id(rng)
        account = f"{rng.randrange(10**11, 10**12):012d}"
        date = f"2026{rng.randrange(1, 13):02d}{rng.randrange(1, 28):02d}"
        bad_id = "A3" + national_id[2:]  # fails the supported second-character pattern
        timestamp = date + "153045"
        sql = (f"INSERT INTO {table} (NATIONAL_ID, BUSINESS_ID, ACCOUNT_NO, BIZ_DATE, BAD_ID, CREATED_TS) "
               f"VALUES ('{national_id}', '{business_id}', '{account}', '{date}', '{bad_id}', '{timestamp}');")
        expected = {"statement_count": 1, "pii": [
            {"type": "id", "value": national_id}, {"type": "ban", "value": business_id},
            {"type": "acct", "value": account},
        ], "negative_examples": [date, timestamp, bad_id]}
    else:
        options = ["", f"-- synthetic case {i}\nSELECT 'a;''b' FROM {table};",
                   f"SELECT /* nested edge */ NULL FROM {table}",
                   f"SELECT 'unterminated FROM {table};", "WITH AS SELECT FROM"]
        sql = options[rng.randrange(len(options))]
        expected = {"non_empty": bool(sql.strip())}
    return sql, expected


def generate_cases(seed: int = 20261023) -> list[SyntheticCase]:
    rng = random.Random(seed)
    cases: list[SyntheticCase] = []
    idx = 0
    for category, count in CATEGORY_COUNTS.items():
        for _ in range(count):
            idx += 1
            sql, expected = _build_sql(category, idx, rng)
            modules = {
                "basic": ("Oracle SQL Formatter", "Oracle SQL Compare"),
                "joins": ("SQL 欄位血緣分析器", "Oracle SQL Formatter"),
                "cte_lineage": ("SQL 欄位血緣分析器", "Copilot 摘要匯出"),
                "oracle_specific": ("Oracle SQL Formatter", "SQL 欄位血緣分析器"),
                "ddl_dml": ("Oracle SQL Compare", "SQL Catalog"),
                "pii": ("SQL 個資清除器",),
                "edge_cases": ("Oracle SQL Formatter", "Oracle SQL Compare"),
            }[category]
            cases.append(SyntheticCase(f"SYN-{idx:04d}", category, sql, modules, expected))
    return cases


def pii_metrics(tp: int, fp: int, fn: int) -> dict[str, Any]:
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = round(2 * precision * recall / (precision + recall), 12) if precision is not None and recall is not None and precision + recall else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def _write_chart(path: Path, title: str, labels: list[str], values: list[float], ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")
    fig.patch.set_facecolor(PALETTE["snow"])
    ax.set_facecolor(PALETTE["snow"])
    bars = ax.bar(range(len(labels)), values, color=PALETTE["ice"], edgecolor=PALETTE["graphite"])
    ax.set_title(title, color=PALETTE["graphite"], fontweight="bold")
    ax.set_ylabel(ylabel, color=PALETTE["slate"])
    ax.set_xticks(range(len(labels)), labels, rotation=25, ha="right", color=PALETTE["slate"])
    ax.tick_params(axis="y", colors=PALETTE["slate"])
    ax.grid(axis="y", color=PALETTE["silver"], linewidth=.8)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.annotate(f"{value:g}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8, color=PALETTE["slate"])
    fig.savefig(path, dpi=160, facecolor=PALETTE["snow"])
    fig.savefig(path.with_suffix(".svg"), facecolor=PALETTE["snow"])
    plt.close(fig)


def write_report(output_dir: Path, cases: list[SyntheticCase], results: list[dict[str, Any]],
                 metadata: dict[str, Any], pii_summary: dict[str, Any],
                 performance: list[dict[str, Any]]) -> Path:
    output_dir = Path(output_dir)
    charts = output_dir / "charts"
    result_dir = output_dir / "results"
    fixture_dir = output_dir / "fixtures"
    for folder in (charts, result_dir, fixture_dir):
        folder.mkdir(parents=True, exist_ok=True)
    payload_cases = [asdict(case) for case in cases]
    (fixture_dir / "synthetic-cases.json").write_text(json.dumps(payload_cases, ensure_ascii=False, indent=2), encoding="utf-8")
    (result_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    if results:
        with (result_dir / "results.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for row in results for k in row)))
            writer.writeheader()
            writer.writerows(results)
    (result_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (result_dir / "pii-metrics.json").write_text(json.dumps(pii_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (result_dir / "performance.json").write_text(json.dumps(performance, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = {CATEGORY_LABELS[key]: sum(case.category == key for case in cases) for key in CATEGORY_COUNTS}
    _write_chart(charts / "case-distribution.png", "合成案例分布", list(counts), list(counts.values()), "案例數")
    status_labels = {"passed": "通過", "failed": "失敗", "error": "錯誤", "skipped": "略過", "manual": "人工驗收"}
    status_counts = {status_labels[s]: sum(r.get("status") == s for r in results) for s in status_labels}
    _write_chart(charts / "module-status.png", "測試狀態分布", list(status_counts), list(status_counts.values()), "測試數")
    _write_chart(charts / "pii-precision-recall.png", "個資辨識準確性", ["精確率", "召回率", "F1"],
                 [100 * (pii_summary.get(k) or 0) for k in ("precision", "recall", "f1")], "百分比")
    _write_chart(charts / "pii-false-results.png", "個資誤判與漏判", ["FP 誤判", "FN 漏判"],
                 [pii_summary.get("fp", 0), pii_summary.get("fn", 0)], "筆數")
    perf_groups: dict[int, list[float]] = {}
    throughput_groups: dict[int, list[float]] = {}
    for row in performance:
        perf_groups.setdefault(int(row["size"]), []).append(float(row["duration_ms"]))
        throughput_groups.setdefault(int(row["size"]), []).append(float(row.get("throughput_per_second", 0)))
    def percentile(values: list[float], fraction: float) -> float:
        ordered = sorted(values)
        return ordered[max(0, min(len(ordered) - 1, int(__import__("math").ceil(fraction * len(ordered)) - 1)))]
    perf_summary = [{"module": "Oracle SQL Formatter", "size": size, "runs": len(perf_groups[size]),
                     "p50_ms": round(percentile(perf_groups[size], .50), 3),
                     "p95_ms": round(percentile(perf_groups[size], .95), 3),
                     "mean_throughput_per_second": round(sum(throughput_groups[size]) / len(throughput_groups[size]), 2)}
                    for size in sorted(perf_groups) if perf_groups[size]]
    (result_dir / "performance-summary.json").write_text(json.dumps(perf_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    sizes = sorted(perf_groups)
    _write_chart(charts / "performance-duration.png", "資料規模與耗時", [str(s) for s in sizes],
                 [sum(perf_groups[s]) / len(perf_groups[s]) for s in sizes], "平均耗時（毫秒）")
    throughput = [sum(float(r.get("throughput_per_second", 0)) for r in performance if int(r["size"]) == size) /
                  max(1, sum(int(r["size"]) == size for r in performance)) for size in sizes]
    _write_chart(charts / "performance-throughput.png", "資料規模與吞吐量", [str(s) for s in sizes], throughput, "筆／秒")

    book = output_dir / "test-report.xlsx"
    wb = xlsxwriter.Workbook(str(book))
    title_fmt = wb.add_format({"bold": True, "font_size": 16, "font_color": "#FFFFFF", "bg_color": PALETTE["graphite"]})
    head_fmt = wb.add_format({"bold": True, "font_color": PALETTE["graphite"], "bg_color": PALETTE["ice"], "border": 1})
    cell_fmt = wb.add_format({"font_color": PALETTE["slate"], "text_wrap": True, "valign": "top"})
    sheets = {
        "總覽": [("項目", "數值"), *[(k, v) for k, v in {"執行時間 UTC": metadata.get("started_at", ""),
            "亂數種子": metadata.get("seed", ""), "來源": metadata.get("source", ""),
            "案例數": len(cases), "結果數": len(results),
            **{f"測試狀態：{status}": sum(row.get("status") == status for row in results)
               for status in ("passed", "failed", "error", "skipped", "manual", "prepared")},
            "個資指標": json.dumps(pii_summary, ensure_ascii=False)}.items()]],
        "模組覆蓋": [("模組", "狀態", "層級", "細節"), *[(r.get("module", ""), r.get("status", ""), r.get("level", ""), r.get("details", "")) for r in results]],
        "案例明細": [("案例 ID", "類別", "模組", "SQL", "預期"), *[(c.case_id, c.category, "、".join(c.modules), c.sql, json.dumps(c.expected, ensure_ascii=False)) for c in cases]],
        "個資指標": [("指標", "數值"), *[(k, v if v is not None else "N/A") for k, v in pii_summary.items()]],
        "效能結果": [("模組", "規模", "次數", "單次耗時 ms", "P50 ms", "P95 ms", "吞吐量／秒"),
            *[(r.get("module"), r.get("size"), r.get("run"), r.get("duration_ms"),
               next((s["p50_ms"] for s in perf_summary if s["size"] == r.get("size")), "N/A"),
               next((s["p95_ms"] for s in perf_summary if s["size"] == r.get("size")), "N/A"),
               r.get("throughput_per_second")) for r in performance]],
        "失敗與限制": [("案例／模組", "狀態", "錯誤或限制"), *[(r.get("case_id", r.get("module", "")), r.get("status", ""), r.get("error", r.get("details", ""))) for r in results if r.get("status") in ("failed", "error", "manual", "skipped", "timeout", "timeout-or-error")]],
        "執行資訊": [("欄位", "值"), *[(k, json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in metadata.items()]],
    }
    for name, rows in sheets.items():
        ws = wb.add_worksheet(name)
        ws.freeze_panes(1, 0)
        ws.set_column(0, 0, 24)
        ws.set_column(1, max(1, len(rows[0]) - 1), 36)
        ws.merge_range(0, 0, 0, max(1, len(rows[0]) - 1), name, title_fmt)
        # Header follows title row; autofilter starts at row 1.
        for col, value in enumerate(rows[0]):
            ws.write(1, col, value, head_fmt)
        for ridx, row in enumerate(rows[1:], start=2):
            for col, value in enumerate(row):
                ws.write(ridx, col, value, cell_fmt)
        ws.autofilter(1, 0, max(1, len(rows)), len(rows[0]) - 1)
        ws.freeze_panes(2, 0)
    wb.close()

    zip_path = output_dir / "test-results.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in output_dir.rglob("*"):
            if file.is_file() and file != zip_path:
                archive.write(file, file.relative_to(output_dir))
    return output_dir


def source_fingerprint(project_dir: Path) -> str:
    digest = hashlib.sha256()
    root = Path(project_dir)
    files = sorted({file for pattern in ("*.html", "*.js", "*.css") for file in root.rglob(pattern)})
    for file in files:
        digest.update(file.relative_to(root).as_posix().encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()
