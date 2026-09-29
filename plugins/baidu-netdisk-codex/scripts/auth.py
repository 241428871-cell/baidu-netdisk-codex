"""Authorize locally without sending a Baidu access token to Codex chat."""

from __future__ import annotations

import argparse
from getpass import getpass
import os
import re
import sys
from urllib.parse import parse_qs, urlencode, urlsplit
import webbrowser

import keyring


SERVICE = "codex-baidu-netdisk-mcp"
ACCOUNT = "access_token"
GUIDE_URL = "https://github.com/baidu-netdisk/mcp"
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9._~-]{16,}")


def extract_token(value: str, *, official_url_only: bool = False) -> str:
    value = value.strip()
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        if (
            parsed.scheme != "https"
            or parsed.netloc != "openapi.baidu.com"
            or parsed.path != "/oauth/2.0/login_success"
        ):
            return ""
        fields = parse_qs(parsed.fragment or parsed.query)
        candidate = fields.get("access_token", [""])[0].strip()
        return candidate if TOKEN_PATTERN.fullmatch(candidate) else ""
    if official_url_only:
        return ""
    return value if TOKEN_PATTERN.fullmatch(value) else ""


def authorization_url(client_id: str) -> str:
    return "https://openapi.baidu.com/oauth/2.0/authorize?" + urlencode(
        {
            "client_id": client_id,
            "redirect_uri": "oob",
            "response_type": "token",
            "scope": "basic,netdisk",
        }
    )


def save_credential(value: str) -> bool:
    token = extract_token(value)
    if not token:
        return False
    keyring.set_password(SERVICE, ACCOUNT, token)
    return True


def console_authorize(client_id: str, open_browser: bool) -> int:
    if client_id and open_browser:
        webbrowser.open(authorization_url(client_id))
    elif not client_id:
        print(f"Get an authorization URL from your Baidu app or {GUIDE_URL}")
    if not sys.stdin.isatty():
        print("A local interactive terminal is required for authorization.", file=sys.stderr)
        return 2
    value = getpass("Paste the full Baidu success URL or access token here: ")
    if not save_credential(value):
        print("The pasted value is not a valid Baidu token or success URL.", file=sys.stderr)
        return 1
    print("Authorization saved to the local credential store.")
    return 0


def gui_authorize(client_id: str, open_browser: bool) -> int:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("Codex 连接百度网盘")
    root.geometry("720x290")
    root.resizable(False, False)
    state = {"watching": False, "last": None, "saved": False}

    def save(value: str, copied: bool = False) -> None:
        try:
            accepted = save_credential(value)
        except Exception as exc:
            messagebox.showerror("保存失败", type(exc).__name__)
            return
        if not accepted:
            messagebox.showerror("无法保存", "未找到有效的百度授权令牌。")
            return
        if copied:
            try:
                root.clipboard_clear()
            except tk.TclError:
                pass
        entry.delete(0, tk.END)
        state["saved"] = True
        messagebox.showinfo("授权已保存", "令牌已保存在本机凭据管理器。")
        root.destroy()

    def open_authorization() -> None:
        webbrowser.open(authorization_url(client_id) if client_id else GUIDE_URL)

    def poll_clipboard() -> None:
        if not state["watching"]:
            return
        try:
            value = root.clipboard_get()
        except tk.TclError:
            value = None
        if value and value != state["last"]:
            state["last"] = value
            if extract_token(value, official_url_only=True):
                save(value, copied=True)
                return
        root.after(500, poll_clipboard)

    def start_watch() -> None:
        if state["watching"]:
            return
        state["watching"] = True
        try:
            state["last"] = root.clipboard_get()
        except tk.TclError:
            state["last"] = None
        status.config(text="正在等待：授权成功后在浏览器按 Ctrl+L、Ctrl+C。")
        root.after(500, poll_clipboard)

    tk.Label(
        root,
        text="百度授权页不会自动跳回 Codex。令牌留在本机，请勿发到聊天中。",
        anchor="w",
    ).pack(fill="x", padx=18, pady=(16, 4))
    tk.Label(
        root,
        text=(
            "点击下方按钮打开授权页。若尚无应用 ID，"
            "按钮会打开百度官方 MCP 指南。"
        ),
        anchor="w",
    ).pack(fill="x", padx=18)
    tk.Button(root, text="打开百度授权页面", command=open_authorization).pack(pady=(12, 5))
    tk.Button(root, text="开始等待复制地址", command=start_watch).pack(pady=4)
    status = tk.Label(
        root,
        text="在授权成功页复制完整地址，本窗口会自动提取并保存令牌。",
        anchor="w",
    )
    status.pack(fill="x", padx=18, pady=(8, 8))
    tk.Label(
        root,
        text="也可把完整成功地址或令牌粘贴到此处，点击手动保存：",
        anchor="w",
    ).pack(fill="x", padx=18)
    entry = tk.Entry(root, show="*", width=80)
    entry.pack(padx=18, pady=(4, 6), fill="x")
    tk.Button(root, text="手动保存", command=lambda: save(entry.get())).pack()
    if client_id and open_browser:
        root.after(200, lambda: webbrowser.open(authorization_url(client_id)))
    root.mainloop()
    return 0 if state["saved"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Store Baidu authorization locally.")
    parser.add_argument(
        "--client-id",
        default=os.environ.get("BAIDU_NETDISK_CLIENT_ID", ""),
        help="Your Baidu developer app ID; its consent name is set in Baidu's console.",
    )
    parser.add_argument("--status", action="store_true", help="Report whether a token is saved.")
    parser.add_argument("--console", action="store_true", help="Use a local hidden prompt.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser.")
    args = parser.parse_args()
    if args.status:
        present = bool(keyring.get_password(SERVICE, ACCOUNT))
        print("Baidu credential saved." if present else "Baidu credential missing.")
        return 0 if present else 1
    if args.console:
        return console_authorize(args.client_id, not args.no_browser)
    try:
        return gui_authorize(args.client_id, not args.no_browser)
    except (ImportError, RuntimeError):
        return console_authorize(args.client_id, not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
