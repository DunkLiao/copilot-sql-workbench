#!/usr/bin/env python3
"""列出並關閉目前 Google Colab 帳號的所有運算工作階段。

使用方式：
    python close_colab_sessions.py           # 列出並詢問是否關閉
    python close_colab_sessions.py --yes     # 不詢問，直接關閉

需要安裝並完成登入的 Google Colab CLI（colab_cli）。
"""

import argparse
import sys
import time


def _endpoint(assignment):
    endpoint = getattr(assignment, "endpoint", None)
    if not endpoint and isinstance(assignment, dict):
        endpoint = assignment.get("endpoint")
    return str(endpoint) if endpoint else None


def main() -> int:
    parser = argparse.ArgumentParser(description="關閉 Google Colab 所有 active sessions")
    parser.add_argument("--yes", "-y", action="store_true", help="跳過確認，直接關閉")
    args = parser.parse_args()

    try:
        from colab_cli.common import state
    except ImportError:
        print("錯誤：找不到 colab_cli。請使用安裝 Colab CLI 的 Python 環境執行。")
        return 1

    try:
        assignments = list(state.client.list_assignments())
    except Exception as exc:
        print(f"讀取 Colab Sessions 失敗：{exc}")
        return 1

    if not assignments:
        print("沒有可關閉的 Colab Sessions。")
        return 0

    endpoints = []
    for assignment in assignments:
        endpoint = _endpoint(assignment)
        if endpoint is None:
            print(f"警告：無法取得工作階段的 endpoint：{assignment!r}")
            continue
        endpoints.append(endpoint)

    if not endpoints:
        print("沒有找到有效的 Session endpoint，未執行關閉操作。")
        return 1

    print(f"找到 {len(endpoints)} 個 Sessions：")
    for i, endpoint in enumerate(endpoints, 1):
        print(f"  {i}. {endpoint}")

    if not args.yes:
        response = input("\n確定要關閉上述所有 Sessions？未儲存資料可能遺失。[y/N] ").strip().lower()
        if response not in ("y", "yes"):
            print("已取消，沒有關閉任何 Session。")
            return 2

    failures = 0
    for endpoint in endpoints:
        try:
            print(f"正在關閉：{endpoint}")
            state.client.unassign(endpoint)
            print("  已送出解除指派請求。")
        except Exception as exc:
            failures += 1
            print(f"  失敗：{exc}")

    print(f"\n處理完畢：成功送出 {len(endpoints) - failures} 個，失敗 {failures} 個。")
    if failures:
        print("若出現 HTTP 404 Not Found，可能是伺服器狀態或 API 不一致；請改從 Colab 網頁的『管理工作階段』檢查。")

    # unassign() only acknowledges a request; poll the server until every assignment disappears.
    print("正在確認 Colab 伺服器上的工作階段狀態（最多等待 30 秒）……")
    deadline = time.monotonic() + 30
    while True:
        try:
            remaining = list(state.client.list_assignments())
        except Exception as exc:
            print(f"無法驗證工作階段是否全部關閉：{exc}")
            return 1
        if not remaining:
            print("確認完成：所有 Colab Sessions 均已關閉。")
            return 0
        if time.monotonic() >= deadline:
            print(f"驗證失敗：仍有 {len(remaining)} 個 Colab Sessions：")
            for assignment in remaining:
                print(f"  - {_endpoint(assignment) or 'endpoint unavailable'}")
            return 1
        time.sleep(2)


if __name__ == "__main__":
    sys.exit(main())
