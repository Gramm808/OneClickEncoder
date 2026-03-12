# Release Checklist

1. Ensure `one_click_encoder.py` runs locally.
2. Build executable:
   - `pyinstaller .\OneClickEncoder.spec --clean`
3. Compute checksum:
   - `Get-FileHash .\dist\OneClickEncoder.exe -Algorithm SHA256`
4. Create Git tag and GitHub Release.
5. Attach:
   - `dist\OneClickEncoder.exe`
   - SHA256 hash text
6. Add release notes:
   - version
   - what changed
   - checksum
   - known limitations
7. Optional but recommended:
   - submit binary to VirusTotal and include link
