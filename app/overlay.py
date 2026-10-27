"""Pełnoekranowe zaznaczanie obszaru (jak narzędzie Wycinanie)."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Optional

from app.capture import virtual_desktop_bounds


@dataclass
class Region:
    left: int
    top: int
    width: int
    height: int


class SelectionOverlay:
    """Półprzezroczysty overlay — przeciągnij, żeby zaznaczyć obszar."""

    def __init__(self, root: tk.Tk, on_done: Callable[[Optional[Region]], None]) -> None:
        self._root = root
        self._on_done = on_done
        self._start: Optional[tuple[int, int]] = None
        self._rect_id: Optional[int] = None
        self._win: Optional[tk.Toplevel] = None

    def show(self) -> None:
        left, top, width, height = virtual_desktop_bounds()

        win = tk.Toplevel(self._root)
        self._win = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        # Lekkie przyciemnienie — nadal widać treść pod spodem
        try:
            win.attributes("-alpha", 0.35)
        except tk.TclError:
            pass

        win.geometry(f"{width}x{height}+{left}+{top}")
        win.configure(bg="#111111", cursor="crosshair")

        canvas = tk.Canvas(
            win,
            width=width,
            height=height,
            highlightthickness=0,
            bg="#111111",
            cursor="crosshair",
        )
        canvas.pack(fill="both", expand=True)
        self._canvas = canvas
        self._origin = (left, top)

        hint = canvas.create_text(
            width // 2,
            40,
            text="Zaznacz obszar  ·  Esc — anuluj",
            fill="#FFFFFF",
            font=("Segoe UI", 14),
        )
        self._hint_id = hint

        canvas.bind("<ButtonPress-1>", self._on_press)
        canvas.bind("<B1-Motion>", self._on_drag)
        canvas.bind("<ButtonRelease-1>", self._on_release)
        win.bind("<Escape>", self._cancel)
        win.focus_force()
        win.grab_set()

    def _to_screen(self, x: int, y: int) -> tuple[int, int]:
        ox, oy = self._origin
        return ox + x, oy + y

    def _on_press(self, event: tk.Event) -> None:
        self._start = (event.x, event.y)
        if self._rect_id is not None:
            self._canvas.delete(self._rect_id)
            self._rect_id = None
        if hasattr(self, "_hint_id"):
            self._canvas.delete(self._hint_id)

    def _on_drag(self, event: tk.Event) -> None:
        if self._start is None:
            return
        x0, y0 = self._start
        if self._rect_id is not None:
            self._canvas.delete(self._rect_id)
        # Jaśniejszy prostokąt = „wycięty” obszar
        self._rect_id = self._canvas.create_rectangle(
            x0,
            y0,
            event.x,
            event.y,
            outline="#4FC3F7",
            width=2,
            fill="#FFFFFF",
            stipple="gray50",
        )

    def _on_release(self, event: tk.Event) -> None:
        if self._start is None:
            return
        x0, y0 = self._start
        x1, y1 = event.x, event.y
        left = min(x0, x1)
        top = min(y0, y1)
        width = abs(x1 - x0)
        height = abs(y1 - y0)

        self._close()

        if width < 4 or height < 4:
            self._on_done(None)
            return

        sx, sy = self._to_screen(left, top)
        self._on_done(Region(left=sx, top=sy, width=width, height=height))

    def _cancel(self, _event: tk.Event | None = None) -> None:
        self._close()
        self._on_done(None)

    def _close(self) -> None:
        if self._win is not None:
            try:
                self._win.grab_release()
            except tk.TclError:
                pass
            self._win.destroy()
            self._win = None
