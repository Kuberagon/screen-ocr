"""Screen OCR — snipping tool + OCR (Windows)."""

from __future__ import annotations

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageDraw

from app.capture import grab_region
from app.dpi import enable_dpi_awareness
from app.ocr import recognize
from app.overlay import Region, SelectionOverlay
from app.result_window import ResultWindow

HOTKEY = "ctrl+shift+s"
APP_NAME = "Screen OCR"


def _resource_path(*parts: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base.joinpath(*parts)


def _make_tray_icon() -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((6, 6, 58, 58), radius=12, fill=(33, 150, 243, 255))
    draw.rectangle((18, 22, 46, 28), fill=(255, 255, 255, 255))
    draw.rectangle((18, 34, 40, 40), fill=(255, 255, 255, 220))
    return img


class ScreenOcrApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        # Ukryte główne okno — aplikacja żyje w trayu
        self.root.withdraw()
        self.root.attributes("-topmost", True)

        self._busy = False
        self._tray = None
        self._hotkey_ok = False

        self._build_tray()
        self._register_hotkey()
        self._show_startup_hint()

    def _build_tray(self) -> None:
        try:
            import pystray
            from pystray import MenuItem as Item
        except ImportError:
            # Bez trayu — pokaż mini-okno sterujące
            self._show_fallback_panel()
            return

        menu = pystray.Menu(
            Item("Wytnij i OCR  (Ctrl+Shift+S)", self._tray_snip, default=True),
            Item("O aplikacji", self._tray_about),
            Item("Wyjdź", self._tray_quit),
        )
        self._tray = pystray.Icon("screen_ocr", _make_tray_icon(), APP_NAME, menu)
        threading.Thread(target=self._tray.run, daemon=True).start()

    def _show_fallback_panel(self) -> None:
        panel = tk.Toplevel(self.root)
        panel.title(APP_NAME)
        panel.geometry("320x140")
        panel.resizable(False, False)
        panel.configure(bg="#1e1e1e")
        panel.attributes("-topmost", True)
        tk.Label(
            panel,
            text=APP_NAME,
            fg="#fff",
            bg="#1e1e1e",
            font=("Segoe UI", 12, "bold"),
        ).pack(pady=(16, 4))
        tk.Label(
            panel,
            text=f"Skrót: {HOTKEY.upper()}",
            fg="#aaa",
            bg="#1e1e1e",
            font=("Segoe UI", 9),
        ).pack()
        tk.Button(
            panel,
            text="Wytnij i OCR",
            command=self.start_snip,
            font=("Segoe UI", 10),
        ).pack(pady=12)
        panel.protocol("WM_DELETE_WINDOW", self.quit)

    def _register_hotkey(self) -> None:
        try:
            import keyboard

            keyboard.add_hotkey(HOTKEY, lambda: self.root.after(0, self.start_snip))
            self._hotkey_ok = True
        except Exception as exc:
            print(f"Nie udało się zarejestrować skrótu: {exc}", file=sys.stderr)

    def _show_startup_hint(self) -> None:
        hint = (
            f"{APP_NAME} działa w tle.\n\n"
            f"Skrót: {HOTKEY.upper()}\n"
            "Albo kliknij ikonę w zasobniku systemowym."
        )
        # Krótki toast jako Toplevel (bez blokowania)
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(bg="#222")
        try:
            toast.attributes("-alpha", 0.92)
        except tk.TclError:
            pass
        tk.Label(
            toast,
            text=hint,
            fg="#eee",
            bg="#222",
            font=("Segoe UI", 10),
            justify="left",
            padx=18,
            pady=14,
        ).pack()
        toast.update_idletasks()
        sw = toast.winfo_screenwidth()
        sh = toast.winfo_screenheight()
        w, h = toast.winfo_reqwidth(), toast.winfo_reqheight()
        toast.geometry(f"+{sw - w - 24}+{sh - h - 72}")
        toast.after(3500, toast.destroy)

    def start_snip(self) -> None:
        if self._busy:
            return
        self._busy = True
        SelectionOverlay(self.root, on_done=self._on_region).show()

    def _on_region(self, region: Region | None) -> None:
        if region is None:
            self._busy = False
            return

        try:
            image = grab_region(region.left, region.top, region.width, region.height)
        except Exception as exc:
            self._busy = False
            messagebox.showerror(APP_NAME, f"Nie udało się przechwycić ekranu:\n{exc}")
            return

        # Lekkie powiększenie pomaga OCR przy małym tekście
        w, h = image.size
        if max(w, h) < 900:
            scale = max(2, int(900 / max(w, h)))
            image = image.resize((w * scale, h * scale), Image.Resampling.LANCZOS)

        self.root.config(cursor="watch")
        self.root.update_idletasks()

        def work() -> None:
            err: Exception | None = None
            text = ""
            try:
                text = recognize(image, lang="pl-PL")
            except Exception as e:
                err = e

            def done() -> None:
                self.root.config(cursor="")
                self._busy = False
                if err is not None:
                    messagebox.showerror(
                        APP_NAME,
                        "OCR nie powiódł się.\n\n"
                        "Upewnij się, że w Windows masz zainstalowany pakiet językowy "
                        "polski (Ustawienia → Czas i język → Język i region).\n\n"
                        f"Szczegóły: {err}",
                    )
                    return
                ResultWindow(self.root, text, on_again=self.start_snip)

            self.root.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _tray_snip(self, _icon=None, _item=None) -> None:
        self.root.after(0, self.start_snip)

    def _tray_about(self, _icon=None, _item=None) -> None:
        def show() -> None:
            messagebox.showinfo(
                APP_NAME,
                f"{APP_NAME}\n\n"
                "Zaznacz fragment ekranu — aplikacja wypisze tekst (OCR).\n\n"
                f"Skrót klawiszowy: {HOTKEY.upper()}\n"
                "Silnik: Windows.Media.Ocr (wbudowany OCR Windows).",
            )

        self.root.after(0, show)

    def _tray_quit(self, _icon=None, _item=None) -> None:
        self.root.after(0, self.quit)

    def quit(self) -> None:
        try:
            import keyboard

            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        if self._tray is not None:
            try:
                self._tray.stop()
            except Exception:
                pass
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    enable_dpi_awareness()
    app = ScreenOcrApp()
    app.run()


if __name__ == "__main__":
    main()
