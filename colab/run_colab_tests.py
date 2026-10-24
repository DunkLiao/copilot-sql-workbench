from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path

from automation.cli_adapter import ColabCLI, ColabCommandError, find_cli
from automation.package import create_source_archive, sha256_file, validate_result_archive
from automation.state import atomic_json, read_json, utc_now


ROOT = Path(__file__).resolve().parents[1]
REMOTE_ROOT = "/content/sqlspa-runs"
EXIT_TEST_FAILED = 1
EXIT_PRECHECK = 2
EXIT_REMOTE = 3
EXIT_DOWNLOAD = 4
EXIT_TIMEOUT = 5
EXIT_CLEANUP = 6
EXIT_INTERRUPTED = 130


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="將 SQL SPA 測試上傳至 Google Colab 並下載完整成果")
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor = subparsers.add_parser("doctor", help="檢查本機專案、Python 與 Colab CLI，不建立雲端工作階段")
    _common(doctor)
    run = subparsers.add_parser("run", help="打包、上傳、執行、下載並驗證測試成果")
    _common(run)
    run.add_argument("--mode", choices=("quick", "full"), default="full")
    run.add_argument("--seed", type=int, default=20261023)
    run.add_argument("--timeout", type=int, default=3600, help="runner 最長執行秒數，預設 3600")
    run.add_argument("--skip-browser", action="store_true")
    run.add_argument("--skip-performance", action="store_true")
    run.add_argument("--keep-session", action="store_true", help="成果下載成功後仍保留本次 Colab 工作階段")
    download = subparsers.add_parser("download", help="從尚存的工作階段補下載已完成的成果，不會重跑測試")
    _common(download)
    download.add_argument("--run-id", required=True)
    return parser


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cli-path", help="Colab CLI 完整路徑；預設從 PATH 或 Windows Python Scripts 尋找")
    parser.add_argument("--project-dir", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, help="預設 colab/outputs/cli/<run-id>/")


def _cli_help(executable: str) -> str:
    result = subprocess.run([executable, "--help"], capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=30, check=False)
    if result.returncode:
        raise ColabCommandError("讀取 Colab CLI 說明失敗", returncode=result.returncode,
                                stdout=result.stdout, stderr=result.stderr)
    return result.stdout + result.stderr


def _validate_project(project: Path) -> None:
    if not (project / "sql-spa-tools-main").is_dir() or not (project / "colab").is_dir():
        raise FileNotFoundError("專案根目錄必須同時包含 sql-spa-tools-main/ 與 colab/")
    for relative in ("theme.md", "colab/requirements.txt", "colab/testing/runner.py"):
        if not (project / relative).is_file():
            raise FileNotFoundError(f"找不到必要檔案：{relative}")


def doctor(args: argparse.Namespace) -> int:
    project = args.project_dir.resolve()
    _validate_project(project)
    executable = find_cli(args.cli_path)
    help_text = _cli_help(executable)
    commands = ("new", "upload", "exec", "download", "stop")
    missing = [command for command in commands if command not in help_text]
    if missing:
        raise RuntimeError("目前 Colab CLI 缺少必要命令：" + ", ".join(missing))
    print(f"專案：{project}")
    print(f"Python：{sys.version.split()[0]}")
    print(f"平台：{platform.platform()}")
    print(f"Colab CLI：{executable}")
    print("必要命令：" + ", ".join(commands))
    if platform.system() == "Windows":
        print("注意：官方尚未支援 Windows；本機 help 可用不代表遠端操作已驗證。可直接嘗試 run，或改用 WSL。")
    print("預檢完成；尚未建立 Colab 工作階段。")
    return 0


def _output_dir(project: Path, supplied: Path | None, run_id: str) -> Path:
    path = supplied or (project / "colab" / "outputs" / "cli" / run_id)
    path = path.resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _script_with_run_id(destination: Path, run_id: str) -> Path:
    source = Path(__file__).parent / "automation" / "remote_bootstrap.py"
    content = source.read_text(encoding="utf-8")
    content = content.replace('RUN_ID_PLACEHOLDER = "__SQLSPA_RUN_ID__"',
                              f'RUN_ID_PLACEHOLDER = {json.dumps(run_id)}')
    # google-colab-cli 0.7.5 opens --file using the Windows system encoding (CP950).
    # Keep the transmitted script ASCII; Python decodes \u escapes inside literals.
    destination.write_bytes(content.encode("ascii", errors="backslashreplace"))
    return destination


def _prepare_script(destination: Path, remote_run_dir: str) -> Path:
    destination.write_text(
        "from pathlib import Path\n"
        f"Path({remote_run_dir!r}).mkdir(parents=True, exist_ok=True)\n"
        f"Path({(remote_run_dir + '/upload')!r}).mkdir(parents=True, exist_ok=True)\n"
        f"Path({(remote_run_dir + '/output')!r}).mkdir(parents=True, exist_ok=True)\n"
        "print('Colab run directories prepared')\n", encoding="utf-8")
    return destination


def _start_download(project: Path, run_id: str, output_dir: Path, cli_path: str,
                    timeout: int) -> tuple[int, dict | None, str | None]:
    state_path = output_dir / "run-state.json"
    if not state_path.is_file():
        print(f"找不到本機作業狀態：{state_path}", file=sys.stderr)
        return EXIT_PRECHECK, None, None
    state = read_json(state_path)
    if state.get("run_id") != run_id:
        print("狀態檔的 run_id 與指定值不符。", file=sys.stderr)
        return EXIT_PRECHECK, None, None
    if state.get("stage") in ("verified", "cleaned") and state.get("artifact_local_path"):
        existing = Path(state["artifact_local_path"])
        if existing.is_file() and sha256_file(existing) == state.get("artifact_sha256"):
            print(f"成果已驗證：{existing}")
            return (EXIT_TEST_FAILED if state.get("outcome") == "failed" else
                    EXIT_REMOTE if state.get("outcome") == "infrastructure_error" else 0), state, None
        if state.get("stage") == "cleaned":
            print("本機成果遺失或 SHA-256 不符，且 Colab 工作階段已停止，無法補下載。", file=sys.stderr)
            return EXIT_DOWNLOAD, state, None
        # A retained verified session can serve another download if the local copy was removed.
    session = state.get("session")
    if not session:
        print("此作業沒有可用的 Colab session；可能需要重新執行。", file=sys.stderr)
        return EXIT_DOWNLOAD, state, None
    cli = ColabCLI(cli_path, session, output_dir, timeout)
    remote_state = state.get("remote_status_path") or f"{REMOTE_ROOT}/{run_id}/remote-status.json"
    local_status = output_dir / "remote-status.json"
    try:
        status_partial = cli.download(remote_state, local_status)
        remote = read_json(status_partial)
        if remote.get("run_id") != run_id or remote.get("stage") not in ("remote_finished", "remote_error"):
            raise ValueError("Colab 回傳的狀態檔尚未完成或 run_id 不符")
        status_partial.replace(local_status)
        artifact_path = remote.get("artifact_path", "")
        remote_base = f"{REMOTE_ROOT}/{run_id}/"
        if not artifact_path.startswith(remote_base):
            raise ValueError("遠端成果路徑超出本次作業目錄")
        if remote.get("artifact_kind") == "diagnostics":
            artifact_name = "diagnostics.zip"
        else:
            artifact_name = "test-results.zip"
        target = output_dir / artifact_name
        partial_target = cli.download(artifact_path, target)
        if partial_target.stat().st_size != remote.get("artifact_size"):
            raise ValueError("下載成果大小不符")
        if sha256_file(partial_target) != remote.get("artifact_sha256"):
            raise ValueError("下載成果 SHA-256 不符")
        with zipfile.ZipFile(partial_target) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise ValueError(f"下載 ZIP CRC 錯誤：{bad_member}")
        members: list[str] = []
        if artifact_name == "test-results.zip":
            members = validate_result_archive(partial_target, remote["artifact_size"], remote["artifact_sha256"])
        partial_target.replace(target)
        state.update({"stage": "verified", "outcome": remote.get("outcome"),
                      "runner_exit_code": remote.get("runner_exit_code"),
                      "runner_run_id": remote.get("runner_run_id"),
                      "artifact_local_path": str(target), "artifact_sha256": remote["artifact_sha256"],
                      "verified_members": members, "downloaded_at": utc_now()})
        atomic_json(state_path, state)
        print(f"成果已下載並驗證：{partial_target}")
        if remote.get("outcome") == "failed":
            print(f"測試失敗（runner exit={remote.get('runner_exit_code')}），完整報告已保存。", file=sys.stderr)
            return EXIT_TEST_FAILED, state, None
        if remote.get("outcome") == "infrastructure_error":
            print(f"遠端環境或執行器失敗，診斷包已保存：{partial_target}", file=sys.stderr)
            return EXIT_REMOTE, state, None
        return 0, state, None
    except Exception as exc:
        state.update({"stage": "download_failed", "download_error": str(exc), "updated_at": utc_now()})
        atomic_json(state_path, state)
        print(f"下載或驗證失敗；session {session} 仍保留，可重試 download --run-id {run_id}。\n{exc}",
              file=sys.stderr)
        return EXIT_DOWNLOAD, state, None


def _cleanup(cli: ColabCLI, state: dict, state_path: Path, keep: bool) -> int:
    if keep:
        print(f"依 --keep-session 保留工作階段：{state['session']}")
        return 0
    try:
        cli.stop()
        state.update({"stage": "cleaned", "cleaned_at": utc_now()})
        atomic_json(state_path, state)
        print(f"已釋放本次 Colab 工作階段：{state['session']}")
        return 0
    except Exception as exc:
        state.update({"cleanup_failed": str(exc), "cleanup_failed_at": utc_now()})
        atomic_json(state_path, state)
        print(f"工作階段停止失敗，請手動檢查 {state['session']}：{exc}", file=sys.stderr)
        return EXIT_CLEANUP


def run_job(args: argparse.Namespace) -> int:
    project = args.project_dir.resolve()
    _validate_project(project)
    if args.timeout <= 0:
        raise ValueError("--timeout 必須大於 0")
    executable = find_cli(args.cli_path)
    help_text = _cli_help(executable)
    for command in ("new", "upload", "exec", "download", "stop"):
        if command not in help_text:
            raise RuntimeError(f"Colab CLI 缺少必要命令：{command}")
    run_id = uuid.uuid4().hex
    output_dir = _output_dir(project, args.output_dir, run_id)
    session = f"sqlspa-{run_id[:20]}"
    remote_run = f"{REMOTE_ROOT}/{run_id}"
    remote_status = f"{remote_run}/remote-status.json"
    state_path = output_dir / "run-state.json"
    state = {"run_id": run_id, "session": session, "stage": "prepared", "created_at": utc_now(),
             "project_dir": str(project), "mode": args.mode, "seed": args.seed,
             "skip_browser": args.skip_browser, "skip_performance": args.skip_performance,
             "timeout_seconds": args.timeout, "remote_status_path": remote_status,
             "output_dir": str(output_dir)}
    atomic_json(state_path, state)
    print(f"作業識別碼：{run_id}\nColab session：{session}\n成果目錄：{output_dir}")
    if platform.system() == "Windows":
        print("注意：官方尚未支援 Windows；正在以目前 CLI 版本嘗試本次作業。")

    source_archive = output_dir / "source.zip"
    manifest_path = output_dir / "source-manifest.json"
    try:
        manifest = create_source_archive(project, source_archive, manifest_path)
        state["source_archive_sha256"] = manifest["archive_sha256"]
        state["stage"] = "packaged"
        atomic_json(state_path, state)
    except Exception as exc:
        state.update({"stage": "precheck_failed", "error": str(exc)})
        atomic_json(state_path, state)
        raise

    cli = ColabCLI(executable, session, output_dir, max(args.timeout, 600))
    local_directory = Path(tempfile.mkdtemp(prefix=f"sqlspa-{run_id[:8]}-"))
    try:
        state.update({"stage": "authenticating", "updated_at": utc_now()})
        atomic_json(state_path, state)
        cli.authenticate_interactively()
        state.update({"stage": "provisioning", "updated_at": utc_now()})
        atomic_json(state_path, state)
        cli.new()
        state.update({"stage": "provisioned", "provisioned_at": utc_now()})
        atomic_json(state_path, state)
        prepare = _prepare_script(local_directory / "prepare.py", remote_run)
        prep_result = cli.execute(prepare, 120)
        if prep_result.returncode:
            raise ColabCommandError("無法在 Colab 建立本次執行目錄", returncode=prep_result.returncode,
                                    stdout=prep_result.stdout, stderr=prep_result.stderr)
        manifest_remote = remote_run + "/upload/source-manifest.json"
        config_local = output_dir / "run-config.json"
        config = {"mode": args.mode, "seed": args.seed, "skip_browser": args.skip_browser,
                  "skip_performance": args.skip_performance, "timeout_seconds": args.timeout}
        config_local.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        cli.upload(source_archive, remote_run + "/upload/source.zip")
        cli.upload(manifest_path, manifest_remote)
        cli.upload(config_local, remote_run + "/upload/run-config.json")
        state.update({"stage": "uploaded", "uploaded_at": utc_now()})
        atomic_json(state_path, state)

        bootstrap = _script_with_run_id(local_directory / "remote_bootstrap.py", run_id)
        state.update({"stage": "running", "started_at": utc_now()})
        atomic_json(state_path, state)
        execution_result = cli.execute(bootstrap, args.timeout + 3600)
        state["remote_exec_returncode"] = execution_result.returncode
        state["remote_exec_stdout"] = execution_result.stdout[-12000:]
        state["remote_exec_stderr"] = execution_result.stderr[-12000:]
        atomic_json(state_path, state)
        if execution_result.returncode:
            print("遠端 bootstrap 回傳錯誤，仍會嘗試下載遠端狀態與診斷資料。", file=sys.stderr)
        result_code, final_state, _ = _start_download(project, run_id, output_dir, executable, args.timeout)
        if final_state is not None:
            state = final_state
        if result_code == EXIT_DOWNLOAD:
            return result_code
        cleanup_code = _cleanup(cli, state, state_path, args.keep_session)
        if cleanup_code:
            return cleanup_code
        return result_code
    except KeyboardInterrupt:
        state.update({"stage": "interrupted", "interrupted_at": utc_now()})
        atomic_json(state_path, state)
        print(f"已中斷；保留工作階段 {session}。若遠端已完成，可使用 download --run-id {run_id}。",
              file=sys.stderr)
        return EXIT_INTERRUPTED
    except subprocess.TimeoutExpired as exc:
        state.update({"stage": "timeout", "error": str(exc), "updated_at": utc_now()})
        atomic_json(state_path, state)
        print(f"執行逾時；工作階段 {session} 保留，作業識別碼為 {run_id}。", file=sys.stderr)
        return EXIT_TIMEOUT
    except ColabCommandError as exc:
        failed_stage = state.get("stage")
        state.update({"stage": "timeout" if exc.timed_out else "remote_error", "failed_stage": failed_stage,
                      "error": str(exc), "updated_at": utc_now()})
        if failed_stage in ("packaged", "provisioning", "provisioned"):
            # No remote result exists to recover yet; stop only the uniquely named session created here.
            try:
                cli.stop()
                state["stage"] = "cleaned"
                state["cleaned_at"] = utc_now()
            except Exception as cleanup_exc:
                state["cleanup_failed"] = str(cleanup_exc)
        atomic_json(state_path, state)
        # 建立後的遠端故障保留 session，方便查詢及補救。
        print(f"Colab CLI 執行失敗；作業狀態保存在 {state_path}\n{exc}", file=sys.stderr)
        if exc.timed_out:
            return EXIT_TIMEOUT
        if failed_stage == "authenticating":
            return EXIT_PRECHECK
        return EXIT_REMOTE
    finally:
        shutil.rmtree(local_directory, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            return doctor(args)
        if args.command == "download":
            project = args.project_dir.resolve()
            run_id = args.run_id
            if not run_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in run_id):
                raise ValueError("--run-id 格式無效")
            output_dir = _output_dir(project, args.output_dir, run_id)
            return _start_download(project, run_id, output_dir, find_cli(args.cli_path), 600)[0]
        return run_job(args)
    except (FileNotFoundError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return EXIT_PRECHECK


if __name__ == "__main__":
    raise SystemExit(main())

