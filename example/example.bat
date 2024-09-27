@echo off

mkdir output

for %%F in ("CNBS_FOEorigin_missing_1_*.xlsx") do (
    @REM start "" powershell .\example.ps1 search %%F output/%%~nF_output > NUL 2>&1
    start "" /B /MIN powershell .\example.ps1 search %%F output/%%~nF_output > NUL 2>&1
)

pause