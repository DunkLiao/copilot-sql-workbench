import sys
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from testing.framework import generate_cases, pii_metrics, write_report
from testing.runner import MODULES, PAGE_FILES, NODE_TESTS


class FrameworkContractTests(unittest.TestCase):
    def test_generator_returns_exact_reproducible_distribution(self):
        cases = generate_cases(seed=20261023)
        self.assertEqual(len(cases), 1000)
        self.assertEqual(cases, generate_cases(seed=20261023))
        self.assertEqual(
            {key: sum(case.category == key for case in cases) for key in {case.category for case in cases}},
            {"basic": 150, "joins": 150, "cte_lineage": 150, "oracle_specific": 150,
             "ddl_dml": 150, "pii": 150, "edge_cases": 100},
        )

    def test_synthetic_national_ids_fail_the_real_checksum(self):
        values = [item["value"] for case in generate_cases() if case.category == "pii"
                  for item in case.expected["pii"] if item["type"] == "id"]
        weights = [8, 7, 6, 5, 4, 3, 2, 1]
        letters = "ABCDEFGHJKLMNPQRSTUVXYWZIO"
        for value in values:
            letter_value = letters.index(value[0]) + 10
            checksum = letter_value // 10 + (letter_value % 10) * 9
            checksum += sum(int(value[i]) * weight for i, weight in enumerate(weights, start=1))
            checksum += int(value[9])
            self.assertNotEqual(checksum % 10, 0)

    def test_pii_metrics_handle_confusion_matrix_and_zero_denominators(self):
        self.assertEqual(pii_metrics(tp=8, fp=2, fn=2), {
            "tp": 8, "fp": 2, "fn": 2, "precision": 0.8, "recall": 0.8, "f1": 0.8,
        })
        self.assertIsNone(pii_metrics(tp=0, fp=0, fn=0)["precision"])

    def test_report_writes_workbook_charts_and_machine_readable_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = write_report(
                output_dir=Path(tmp),
                cases=generate_cases(seed=7)[:10],
                results=[{"case_id": "C001", "module": "Oracle SQL Formatter", "status": "passed",
                          "duration_ms": 4.5, "details": "ok"}],
                metadata={"seed": 7, "source": "unit-test"},
                pii_summary=pii_metrics(tp=1, fp=0, fn=0),
                performance=[{"module": "Formatter", "size": 10, "duration_ms": 4.5,
                               "throughput_per_second": 2222.2}],
            )
            self.assertTrue((out / "test-report.xlsx").is_file())
            self.assertTrue((out / "results" / "results.json").is_file())
            self.assertEqual(json.loads((out / "results" / "performance-summary.json").read_text(encoding="utf-8"))[0]["p95_ms"], 4.5)
            self.assertTrue((out / "charts" / "case-distribution.png").is_file())
            self.assertTrue((out / "test-results.zip").is_file())

    def test_runner_declares_all_tool_pages_and_existing_contracts(self):
        self.assertEqual(len(PAGE_FILES), 12)
        self.assertEqual(set(PAGE_FILES), set(MODULES) - {"Copilot 摘要匯出", "共用介面"})
        self.assertEqual(len(NODE_TESTS), 10)


if __name__ == "__main__":
    unittest.main()
