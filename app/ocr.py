"""OCR obrazu — Windows.Media.Ocr (wbudowany w Windows)."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image


def recognize(image: Image.Image, lang: str = "pl-PL") -> str:
    """Rozpoznaje tekst z obrazu PIL. Zwraca pusty string przy braku tekstu."""
    return asyncio.run(_recognize_async(image, lang))


async def _recognize_async(image: Image.Image, lang: str) -> str:
    import winocr

    # winocr akceptuje kody typu "pl", "en", "pl-PL"
    lang_code = lang.split("-")[0] if lang else "pl"
    try:
        result = await winocr.recognize_pil(image, lang_code)
    except Exception:
        # Fallback: angielski, jeśli polski pakiet językowy OCR nie jest zainstalowany
        if lang_code != "en":
            result = await winocr.recognize_pil(image, "en")
        else:
            raise

    text = getattr(result, "text", None) or ""
    return text.strip()
