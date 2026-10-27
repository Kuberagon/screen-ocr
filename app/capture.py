"""Przechwytywanie fragmentu ekranu."""

from __future__ import annotations

from PIL import Image
import mss


def grab_region(left: int, top: int, width: int, height: int) -> Image.Image:
    """Zrzut prostokąta ekranu (współrzędne wirtualnego pulpitu)."""
    if width < 1 or height < 1:
        raise ValueError("Obszar jest zbyt mały")

    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")


def virtual_desktop_bounds() -> tuple[int, int, int, int]:
    """Zwraca (left, top, width, height) całego wirtualnego pulpitu."""
    with mss.mss() as sct:
        # monitor 0 = all monitors
        m = sct.monitors[0]
        return m["left"], m["top"], m["width"], m["height"]
