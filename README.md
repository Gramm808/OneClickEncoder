# One-Click Video Encoder

Simple desktop GUI app for batch re-encoding videos to H.264/AAC `.mp4` using FFmpeg.

## Why Windows Shows a "Untrusted App" Warning

The distributed `.exe` is currently unsigned. Windows SmartScreen warns on unsigned apps, especially when the file is new or has few downloads.

This does **not** automatically mean malware, but users should verify source and checksums before running binaries.

## Trust and Verification

This repository includes the exact Python source used to build the app:

- Main app: `one_click_encoder.py`
- Build config: `OneClickEncoder.spec`

Before running a release binary, verify its SHA256 hash:

```powershell
Get-FileHash .\OneClickEncoder.exe -Algorithm SHA256
```

Compare that value with the hash published in the release notes.

## Features

- Batch encode common video formats (`.mp4`, `.mov`, `.mkv`, `.avi`, `.m4v`, `.flv`, `.wmv`, `.webm`)
- Output to compatibility-focused H.264 + AAC `.mp4`
- Select max resolution (`1080` or `720`) while preserving aspect ratio
- Per-file and overall progress bars
- Stop button to cancel current work

## Requirements

- Python 3.10+ (for source run)
- FFmpeg + FFprobe available in PATH

## Run From Source

```powershell
python .\one_click_encoder.py
```

## Build a Windows Executable (PyInstaller)

```powershell
python -m pip install --upgrade pyinstaller
pyinstaller .\OneClickEncoder.spec --clean
```

Executable output:

- `dist\OneClickEncoder.exe`

## Suggested Public Release Process

1. Build a fresh executable from this repo.
2. Generate SHA256 hash.
3. Upload `.exe` plus hash to a GitHub Release.
4. Link users to this source repo and release page.
5. Optional: upload binary to VirusTotal and link the scan result.

## Notes

- The app does not require network access for encoding.
- FFmpeg handles media processing; this app is a local GUI wrapper around FFmpeg commands.
