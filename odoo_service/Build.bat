pyinstaller --onefile --hidden-import charset_normalizer.md__mypyc service.py
pyinstaller --onefile --hidden-import charset_normalizer.md__mypyc prompt.py
cd dist
ren service.exe "Receipt Service.exe"
ren prompt.exe "Receipt Utility.exe"
cd ../