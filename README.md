# Screen OCR

Aplikacja Windows: **wycinasz fragment ekranu** (jak narzędzie Wycinanie), a program **zamienia obraz na tekst** (OCR po polsku).

## Jak używać

1. Uruchom `ScreenOCR.exe` (albo `python run.py`).
2. Aplikacja działa w tle — ikona w zasobniku systemowym (obok zegara).
3. Naciśnij **Ctrl+Shift+S** (albo kliknij ikonę → *Wytnij i OCR*).
4. Zaznacz prostokątem tekst na ekranie.
5. Wynik pojawi się w oknie i **od razu trafi do schowka** (Ctrl+V).

**Esc** anuluje zaznaczanie.

## Wymagania

- Windows 10 / 11
- Pakiet językowy **polski** w systemie (Ustawienia → Czas i język → Język), żeby OCR dobrze czytał polskie znaki (ą, ę, ł, …).  
  Bez niego aplikacja spróbuje angielskiego OCR.

## Budowa .exe

```bat
build.bat
```

Powstanie plik: `dist\ScreenOCR.exe`.

## Uruchomienie z Pythona (dev)

```bat
python -m pip install -r requirements.txt
python run.py
```

## Uwagi

- Skrót globalny wymaga czasem uruchomienia z uprawnieniami administratora (zależnie od innych programów i UAC).
- Działa na wielu monitorach.
- Silnik: wbudowany **Windows.Media.Ocr** (bez Tesseract / bez internetu).
