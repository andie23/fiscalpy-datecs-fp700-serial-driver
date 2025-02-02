## Compiling the app
1. Compile `fp700\stdioFP700.py` with `pyinstaller --onefile --hidden-import charset_normalizer.md__mypyc stdioFp700.py`
2. Use Innosetup.exe app and load setup script found in "{PROJECT_DIR}\windows_innosetup.iss"
3. Using the Innosetup GUI, compile exe file
4. Run setup file / distribute

## Chrome Extension setup
1. Enable developer mode
2. Load Unpacked Extension
3. Select installation folder in "C:\ProgramData\Fiscalpy\"
4. Copy the extension ID after it's successfully loaded
5. Edit the "fiscalpy_chrome_manifest.json" file with extension id