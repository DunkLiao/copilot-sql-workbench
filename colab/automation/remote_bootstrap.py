from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

RUN_ID_PLACEHOLDER = "__SQLSPA_RUN_ID__"


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_extract(archive_path: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for item in archive.infolist():
            name = PurePosixPath(item.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError(f"封裝檔含有不安全路徑：{item.filename}")
            mode = item.external_attr >> 16
            if mode and (mode & 0o170000) == 0o120000:
                raise ValueError(f"封裝檔含有符號連結：{item.filename}")
            target = (destination / Path(*name.parts)).resolve()
            if not target.is_relative_to(destination_resolved):
                raise ValueError(f"封裝檔路徑超出目的資料夾：{item.filename}")
        archive.extractall(destination)


def run(command: list[str], log, *, timeout: int = 1800, env: dict | None = None) -> None:
    log.write(f"$ {' '.join(command)}\n")
    log.flush()
    subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=timeout, env=env)


def write_diagnostic(run_dir: Path, output_dir: Path, error: str) -> Path:
    diagnostic_dir = run_dir / "diagnostics"
    diagnostic_dir.mkdir(parents=True, exist_ok=True)
    (diagnostic_dir / "failure.txt").write_text(error, encoding="utf-8")
    for name in ("bootstrap.log", "runner.stdout.log", "runner.stderr.log"):
        source = output_dir / name
        if source.is_file():
            shutil.copy2(source, diagnostic_dir / name)
    archive = run_dir / "diagnostics.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as result:
        for path in sorted(diagnostic_dir.rglob("*")):
            if path.is_file():
                result.write(path, path.relative_to(diagnostic_dir).as_posix())
    return archive


def main() -> int:
    run_id = RUN_ID_PLACEHOLDER
    if not run_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in run_id):
        print("SQLSPA_RUN_ID 無效", file=sys.stderr)
        return 2
    root = Path("/content/sqlspa-runs") / run_id
    project = root / "project"
    output_dir = root / "output"
    upload_dir = root / "upload"
    state_path = root / "remote-status.json"
    root.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    state = {"run_id": run_id, "stage": "running", "started_at": datetime.now(timezone.utc).isoformat()}
    bootstrap_log = output_dir / "bootstrap.log"
    test_archive = output_dir / "test-results.zip"
    diagnostic_archive = root / "diagnostics.zip"
    failure = ""
    runner_returncode = None
    try:
        upload_archive = upload_dir / "source.zip"
        config_path = upload_dir / "run-config.json"
        manifest_path = upload_dir / "source-manifest.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if sha256_file(upload_archive) != manifest.get("archive_sha256"):
            raise ValueError("上傳的專案 ZIP SHA-256 不符")
        if upload_archive.stat().st_size != manifest.get("archive_size"):
            raise ValueError("上傳的專案 ZIP 大小不符")
        safe_extract(upload_archive, project)
        runner = project / "colab" / "testing" / "runner.py"
        requirements = project / "colab" / "requirements.txt"
        app = project / "sql-spa-tools-main"
        if not runner.is_file() or not requirements.is_file() or not app.is_dir():
            raise FileNotFoundError("解壓後找不到測試 runner、requirements 或應用程式")
        with bootstrap_log.open("w", encoding="utf-8") as log:
            run([sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements)], log)
            run(["apt-get", "update", "-qq"], log, timeout=1200)
            run(["apt-get", "install", "-y", "-qq", "fonts-noto-cjk"], log, timeout=1200)
            run(["fc-cache", "-f"], log)
            font_probe = subprocess.run(["fc-list", ":lang=zh", "family"], capture_output=True,
                                        text=True, check=True, timeout=30)
            if not font_probe.stdout.strip():
                raise RuntimeError("找不到中文字型，無法產生完整中文報告")
            run(["npm", "install", "--prefix", "/content/sqlspa-node", "--no-save", "node@22"], log,
                timeout=1200)
            node_bin = "/content/sqlspa-node/node_modules/node/bin/node"
            if not Path(node_bin).is_file():
                raise FileNotFoundError("Node.js 22 安裝後找不到 node 執行檔")
            environment = os.environ.copy()
            environment["SQLSPA_NODE_BIN"] = node_bin
            run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], log,
                timeout=2400, env=environment)
            if "skip_browser" not in config:
                config["skip_browser"] = False
            command = [sys.executable, str(runner), "--mode", config["mode"], "--seed", str(config["seed"]),
                       "--project-dir", str(project), "--output-dir", str(output_dir)]
            if config["skip_browser"]:
                command.append("--skip-browser")
            if config["skip_performance"]:
                command.append("--skip-performance")
            try:
                run_state = subprocess.run(command, cwd=project, capture_output=True, text=True, encoding="utf-8",
                                           errors="replace", timeout=config["timeout_seconds"], env=environment)
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                (output_dir / "runner.stdout.log").write_text(stdout, encoding="utf-8")
                (output_dir / "runner.stderr.log").write_text(stderr, encoding="utf-8")
                raise TimeoutError(f"測試 runner 執行超過 {config['timeout_seconds']} 秒") from exc
            runner_returncode = run_state.returncode
            (output_dir / "runner.stdout.log").write_text(run_state.stdout, encoding="utf-8")
            (output_dir / "runner.stderr.log").write_text(run_state.stderr, encoding="utf-8")
            summary = None
            for line in reversed(run_state.stdout.splitlines()):
                try:
                    candidate = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(candidate, dict) and "run_id" in candidate and "output_dir" in candidate:
                    summary = candidate
                    break
            if not test_archive.is_file() or summary is None:
                raise RuntimeError(f"runner 未發布完整成果 ZIP（exit={runner_returncode}）")
            metadata = {"orchestration_run_id": run_id, "runner_run_id": summary["run_id"],
                        "runner_exit_code": runner_returncode, "source_archive_sha256": manifest["archive_sha256"],
                        "finished_at": datetime.now(timezone.utc).isoformat()}
            metadata_path = output_dir / "cli-run.json"
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            enriched_archive = output_dir / "test-results.enriched.zip"
            with zipfile.ZipFile(enriched_archive, "w", zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(output_dir.rglob("*")):
                    if path.is_file() and path not in {test_archive, enriched_archive}:
                        archive.write(path, path.relative_to(output_dir).as_posix())
            enriched_archive.replace(test_archive)
            state.update({"stage": "remote_finished", "outcome": "passed" if runner_returncode == 0 else "failed",
                          "runner_exit_code": runner_returncode, "runner_run_id": summary["run_id"],
                          "artifact_path": str(test_archive), "artifact_size": test_archive.stat().st_size,
                          "artifact_sha256": sha256_file(test_archive), "bootstrap_log": str(bootstrap_log)})
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
        state.update({"stage": "remote_error", "outcome": "infrastructure_error", "error": str(exc),
                      "bootstrap_log": str(bootstrap_log)})
        diagnostic_archive = write_diagnostic(root, output_dir, failure)
        state.update({"artifact_path": str(diagnostic_archive), "artifact_size": diagnostic_archive.stat().st_size,
                      "artifact_sha256": sha256_file(diagnostic_archive), "artifact_kind": "diagnostics"})
    state["finished_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json(state_path, state)
    print(json.dumps({"remote_status": str(state_path), "stage": state["stage"],
                      "outcome": state["outcome"], "runner_exit_code": runner_returncode}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    # Colab CLI executes this file inside an IPython kernel; raising SystemExit
    # makes IPython print a misleading traceback even when the run succeeded.
    main()

