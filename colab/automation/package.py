from __future__ import annotations

import hashlib
import json
import os
import stat
import zipfile
from pathlib import Path, PurePosixPath


APP_DIRS = ("tests", "uat-fixtures")
ROOT_FILES = ("theme.md",)
COLAB_DIRS = ("testing",)
COLAB_FILES = ("requirements.txt",)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_files(root: Path, app: Path, colab: Path) -> list[tuple[Path, str]]:
    selected: list[tuple[Path, str]] = []

    def add(path: Path, archive_name: str) -> None:
        if path.is_symlink():
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(root):
                raise ValueError(f"拒絕指向專案外部的符號連結：{path}")
            raise ValueError(f"封裝來源不得包含符號連結：{path}")
        if not path.is_file():
            return
        mode = path.stat().st_mode
        if not stat.S_ISREG(mode):
            raise ValueError(f"封裝來源不是一般檔案：{path}")
        selected.append((path, PurePosixPath(archive_name).as_posix()))

    for name in ROOT_FILES:
        add(root / name, name)
    for path in sorted(app.iterdir()):
        if path.is_file() and path.suffix.lower() in {".html", ".js", ".css"}:
            add(path, f"sql-spa-tools-main/{path.name}")
    for folder in APP_DIRS:
        base = app / folder
        if base.is_dir():
            for path in sorted(base.rglob("*")):
                if any(part in {"node_modules", ".git", "coverage", "__pycache__"} for part in path.parts):
                    continue
                if path.is_symlink():
                    add(path, "")
                elif path.is_file():
                    add(path, f"sql-spa-tools-main/{path.relative_to(app).as_posix()}")
    for name in COLAB_FILES:
        add(colab / name, f"colab/{name}")
    for folder in COLAB_DIRS:
        base = colab / folder
        if base.is_dir():
            for path in sorted(base.rglob("*")):
                if path.is_symlink():
                    add(path, "")
                elif path.is_file() and "__pycache__" not in path.parts:
                    add(path, f"colab/{path.relative_to(colab).as_posix()}")

    names = [name for _, name in selected]
    if len(names) != len(set(names)):
        raise ValueError("封裝清單包含重複路徑")
    required = {"theme.md", "sql-spa-tools-main/index.html", "sql-spa-tools-main/theme.css",
                "sql-spa-tools-main/theme.js", "colab/requirements.txt", "colab/testing/runner.py"}
    missing = required - set(names)
    if missing:
        raise FileNotFoundError("專案缺少必要檔案：" + ", ".join(sorted(missing)))
    return sorted(selected, key=lambda entry: entry[1])


def create_source_archive(project: Path, archive_path: Path, manifest_path: Path) -> dict:
    root = project.resolve()
    app = root / "sql-spa-tools-main"
    colab = root / "colab"
    if not app.is_dir() or not colab.is_dir():
        raise FileNotFoundError("專案根目錄必須同時包含 sql-spa-tools-main/ 與 colab/")
    files = _safe_files(root, app, colab)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_files = []
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, name in files:
            archive.write(path, name)
            manifest_files.append({"path": name, "size": path.stat().st_size, "sha256": sha256_file(path)})
    manifest = {"project_root_name": root.name, "archive": archive_path.name,
                "archive_size": archive_path.stat().st_size, "archive_sha256": sha256_file(archive_path),
                "files": manifest_files}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def validate_result_archive(archive_path: Path, expected_size: int, expected_sha256: str) -> list[str]:
    if not archive_path.is_file():
        raise FileNotFoundError(f"找不到下載的成果：{archive_path}")
    if archive_path.stat().st_size != expected_size:
        raise ValueError(f"成果大小不符：預期 {expected_size}，實際 {archive_path.stat().st_size}")
    digest = sha256_file(archive_path)
    if digest != expected_sha256:
        raise ValueError("成果 SHA-256 不符")
    with zipfile.ZipFile(archive_path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise ValueError(f"成果 ZIP CRC 錯誤：{bad_member}")
        names = set(archive.namelist())
    required = {"test-report.xlsx", "results/results.json", "results/results.csv",
                "results/performance-summary.json"}
    missing = required - names
    if missing:
        raise ValueError("成果 ZIP 缺少必要檔案：" + ", ".join(sorted(missing)))
    if not any(name.startswith("charts/") for name in names):
        raise ValueError("成果 ZIP 缺少 charts/ 圖表")
    if not any(name.startswith("fixtures/") for name in names):
        raise ValueError("成果 ZIP 缺少 fixtures/ 案例")
    return sorted(names)

