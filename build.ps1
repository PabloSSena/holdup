# Builds dist\Holdup\Holdup.exe (PyInstaller onedir), then the installer if Inno Setup 6 is installed.
# Run from the repo root after: .venv\Scripts\python -m pip install -e ".[build]"
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

& .venv\Scripts\pyinstaller --noconfirm --clean --windowed --name Holdup --icon assets\holdup.ico `
    --paths src `
    --add-data "src\holdup\models;holdup\models" `
    --add-data "src\holdup\fonts;holdup\fonts" `
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
$version = & .venv\Scripts\python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"
if ($LASTEXITCODE) { throw "Could not read the version from pyproject.toml" }
& $iscc "/DAppVersion=$version" installer.iss
if ($LASTEXITCODE) { throw "Inno Setup failed" }
