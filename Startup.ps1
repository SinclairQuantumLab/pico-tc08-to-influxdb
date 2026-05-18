$ErrorActionPreference = "Stop"

# PowerShell script to run the specified Python script,
# independent of the PWD this script is run from.

# script to run
$pyPath = ".\main.py"
$pyArgs = $args

# move working directory to the project folder
Write-Host ">>> cd to the project directory..."
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "<<< Working directory set to: $PWD"
Write-Host ""

# use the local virtual environment created by uv
Write-Host ">>> venv checking..."
$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Cannot find venv python: $venvPython"
}
Write-Host "<<< venv ready: $venvPython"
Write-Host ""
Write-Host ""

# run the main script
Write-Host ">>> Starting app: $pyPath $($pyArgs -join ' ')"
Write-Host ""

& $venvPython $pyPath @pyArgs
$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "<<< End of the script: $pyPath"

exit $exitCode
