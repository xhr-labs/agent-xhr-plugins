from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from .auth import AuthManager


def run_auth_dialog(manager: AuthManager | None = None) -> int:
    auth_manager = manager or AuthManager()
    root = tk.Tk()
    root.title("xHR Assistant authentication")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    result = {"exit_code": 2}
    token = tk.StringVar()

    frame = tk.Frame(root, padx=20, pady=18)
    frame.pack()
    tk.Label(frame, text="Paste the access token generated in xHR Platform.").pack(anchor="w")
    tk.Label(frame, text="The token is saved to the OS credential store and is not sent to the agent host.").pack(
        anchor="w", pady=(2, 12)
    )
    entry = tk.Entry(frame, textvariable=token, show="•", width=64)
    entry.pack(fill="x")

    def submit() -> None:
        try:
            auth_manager.import_token(token.get())
        except Exception as exc:
            messagebox.showerror("Authentication failed", str(exc), parent=root)
            entry.focus_set()
            return
        token.set("")
        result["exit_code"] = 0
        messagebox.showinfo("xHR Assistant", "Authentication completed.", parent=root)
        root.destroy()

    buttons = tk.Frame(frame)
    buttons.pack(fill="x", pady=(14, 0))
    tk.Button(buttons, text="Cancel", command=root.destroy).pack(side="right")
    tk.Button(buttons, text="Authenticate", command=submit, default="active").pack(
        side="right", padx=(0, 8)
    )
    root.bind("<Return>", lambda _event: submit())
    root.bind("<Escape>", lambda _event: root.destroy())
    entry.focus_set()
    root.mainloop()
    token.set("")
    return result["exit_code"]
