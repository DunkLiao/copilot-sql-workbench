from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


class ColabCommandError(RuntimeError):
    def __init__(self, message: str, *, returncode: int | None = None,
                 stdout: str = "", stderr: str = "", timed_out: bool = False) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out


def find_cli(explicit_path: str | None = None) -> str:
    if explicit_path:
        candidate = Path(explicit_path).expanduser()
        if candidate.is_file():
            return str(candidate.resolve())
        found = shutil.which(explicit_path)
        if found:
            return found
        raise FileNotFoundError(f"找不到指定的 Colab CLI：{explicit_path}")
    found = shutil.which("colab") or shutil.which("colab.exe")
    if found:
        return found
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates = sorted(Path(appdata).glob("Python/Python*/Scripts/colab.exe"), reverse=True)
        if candidates:
            return str(candidates[0])
    raise FileNotFoundError("找不到 Colab CLI；請安裝 google-colab-cli 或使用 --cli-path 指定執行檔")


class ColabCLI:
    def __init__(self, executable: str, session: str, log_dir: Path, timeout: int) -> None:
        self.executable = executable
        self.session = session
        self.log_dir = log_dir
        self.timeout = timeout
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_index = 0

    def call(self, *args: str, timeout: int | None = None, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
        command = [self.executable, *args]
        self.log_index += 1
        log_path = self.log_dir / f"colab-{self.log_index:02d}-{args[0] if args else 'command'}.log"
        try:
            result = subprocess.run(command, cwd=self.log_dir, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=timeout or self.timeout,
                                    check=False)
        except subprocess.TimeoutExpired as exc:
            stdout = _decode(exc.stdout)
            stderr = _decode(exc.stderr)
            log_path.write_text(f"COMMAND: {command!r}\nTIMEOUT\n{stdout}\n{stderr}\n", encoding="utf-8")
            raise ColabCommandError(f"Colab CLI 命令逾時：{' '.join(command)}", stdout=stdout, stderr=stderr,
                                    timed_out=True) from exc
        log_path.write_text(f"COMMAND: {command!r}\nEXIT: {result.returncode}\n"
                            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}\n",
                            encoding="utf-8")
        if result.returncode and not allow_failure:
            raise ColabCommandError(f"Colab CLI 命令失敗（exit={result.returncode}）：{' '.join(command)}",
                                    returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
        return result

    def new(self) -> None:
        self.call("new", "--session", self.session)

    def authenticate_interactively(self) -> None:
        """讓首次 OAuth 在終端機顯示授權網址並接受一次性驗證碼。"""
        command = [self.executable, "sessions"]
        result = subprocess.run(command, check=False)
        if result.returncode:
            raise ColabCommandError("Colab CLI 登入或列出工作階段失敗", returncode=result.returncode)

    def upload(self, local: Path, remote: str) -> None:
        self.call("upload", "--session", self.session, str(local.resolve()), remote,
                  timeout=max(self.timeout, 600))

    def execute(self, source_file: Path, timeout: int) -> subprocess.CompletedProcess[str]:
        return self.call("exec", "--session", self.session, "--file", str(source_file.resolve()),
                         "--timeout", str(timeout), timeout=timeout + 60, allow_failure=True)

    def download(self, remote: str, local: Path) -> Path:
        local.parent.mkdir(parents=True, exist_ok=True)
        partial = local.with_name(local.name + ".part")
        partial.unlink(missing_ok=True)
        self.call("download", "--session", self.session, remote, str(partial.resolve()),
                  timeout=max(self.timeout, 600))
        if not partial.is_file():
            raise ColabCommandError(f"Colab CLI 未建立下載檔案：{partial}")
        return partial

    def stop(self) -> None:
        self.call("stop", "--session", self.session, timeout=120)


def _decode(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value

