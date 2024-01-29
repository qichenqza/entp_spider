@echo off

mkdir output

for %%F in ("ZGC_*.xlsx") do (
    start "" /B /MIN powershell .\example.ps1 search %%F output/%%~nF_output > NUL 2>&1
)

pause