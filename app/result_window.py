"""Okno z rozpoznanym tekstem."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

import pyperclip


class ResultWindow:
    def __init__(
        self,
        root: tk.Tk,
        text: str,
        on_again: Optional[Callable[[], None]] = None,
    ) -> None:
        self._root = root
        self._on_again = on_again
        self._text = text

        win = tk.Toplevel(root)
        self._win = win
        win.title("Screen OCR — wynik")
        win.attributes("-topmost", True)
        win.geometry("520x320")
        win.minsize(360, 220)
        win.configure(bg="#1e1e1e")

        style = ttk.Style(win)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        header = tk.Frame(win, bg="#1e1e1e")
        header.pack(fill="x", padx=14, pady=(14, 6))

        tk.Label(
            header,
            text="Rozpoznany tekst",
            fg="#e8e8e8",
            bg="#1e1e1e",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        self._status = tk.Label(
            header,
            text="",
            fg="#81c784",
            bg="#1e1e1e",
            font=("Segoe UI", 9),
        )
        self._status.pack(side="right")

        frame = tk.Frame(win, bg="#1e1e1e")
        frame.pack(fill="both", expand=True, padx=14, pady=6)

        self._box = tk.Text(
            frame,
            wrap="word",
            font=("Consolas", 12),
            bg="#2d2d2d",
            fg="#f0f0f0",
            insertbackground="#ffffff",
            relief="flat",
            padx=10,
            pady=10,
            undo=True,
        )
        scroll = ttk.Scrollbar(frame, command=self._box.yview)
        self._box.configure(yscrollcommand=scroll.set)
        self._box.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._box.insert("1.0", text)
        if not text.strip():
            self._box.insert("1.0", "(nie wykryto tekstu — spróbuj większy / ostrzejszy fragment)")

        buttons = tk.Frame(win, bg="#1e1e1e")
        buttons.pack(fill="x", padx=14, pady=(6, 14))

        ttk.Button(buttons, text="Kopiuj", command=self._copy).pack(side="left", padx=(0, 8))
        if on_again:
            ttk.Button(buttons, text="Wytnij ponownie", command=self._again).pack(
                side="left", padx=(0, 8)
            )
        ttk.Button(buttons, text="Zamknij", command=win.destroy).pack(side="right")

        win.bind("<Control-c>", lambda e: self._copy())
        win.protocol("WM_DELETE_WINDOW", win.destroy)

        # Auto-kopiuj, jeśli coś jest
        if text.strip():
            self._copy(silent=False)

        win.focus_force()

    def _copy(self, silent: bool = False) -> None:
        content = self._box.get("1.0", "end-1c")
        try:
            pyperclip.copy(content)
            self._status.configure(text="Skopiowano do schowka")
        except Exception:
            self._root.clipboard_clear()
            self._root.clipboard_append(content)
            self._status.configure(text="Skopiowano do schowka")
        if not silent:
            self._win.after(2500, lambda: self._status.configure(text=""))

    def _again(self) -> None:
        self._win.destroy()
        if self._on_again:
            self._on_again()
