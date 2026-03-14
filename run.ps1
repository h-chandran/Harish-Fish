# Run from project root: installs deps and starts the app.
# Usage: .\run.ps1   (from PowerShell in the Harish-Fish folder)

Set-Location $PSScriptRoot

if (Test-Path ".\venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
} elseif (Test-Path ".\.venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
}

pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

uvicorn app.main:app --reload
