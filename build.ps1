.\lint.ps1
pip freeze > requirements.txt
pyinstaller .\entp.spec
Set-Location dist
7z a -t7z entp.7z .\entp
