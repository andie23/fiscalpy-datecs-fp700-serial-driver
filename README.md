# Chrome Integration
## Extension setup (Developer Mode)
1. Go to extensions page
2. Enable developer mode
3. Load Unpacked
4. Select "chrome_extension" folder

## Building Native App
1. Compile `fp700\stdioFP700.py` using `pyinstaller --onefile --hidden-import charset_normalizer.md__mypyc stdioFp700.py`
2. Use Innosetup.exe app and load setup script found in "fp700\appsetup.iss"
3. Using the Innosetup GUI, compile exe file
4. Run setup file