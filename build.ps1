# Builds dist\Holdup\Holdup.exe (PyInstaller onedir), then the installer if Inno Setup 6 is installed.
# Run from the repo root after: .venv\Scripts\python -m pip install -e ".[build]"
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

& .venv\Scripts\pyinstaller --noconfirm --clean --windowed --name Holdup `
    --paths src `
    --add-data "src\holdup\models;holdup\models" `
    --collect-binaries mediapipe `
    src\holdup\__main__.py
if ($LASTEXITCODE) { throw "PyInstaller failed" }

$iscc = @(
    (Get-Command iscc -ErrorAction SilentlyContinue).Source,
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $iscc) {
    Write-Warning "Inno Setup 6 not found; skipped the installer. Install it (winget install JRSoftware.InnoSetup) and rerun."
    exit 0
}
& $iscc installer.iss
if ($LASTEXITCODE) { throw "Inno Setup failed" }
