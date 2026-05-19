$ErrorActionPreference = "Stop"

# PowerShell script to run the specified Python script,
# independent of the PWD this script is run from.

# script to run
$pyPath = ".\main.py"
$pyArgs = $args

# terminal window options
$terminalColumns = 140
$terminalRows = 30
$terminalBufferRows = 3000
$pauseOnError = $true

function Wait-BeforeClosingOnError {
    if ($pauseOnError) {
        Write-Host ""
        Read-Host "Press Enter to close this window"
    }
}

function Get-TomlSN {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*sn\s*=\s*["'']?([^"'']+)["'']?\s*(#.*)?$') {
            return $Matches[1].Trim()
        }
    }

    return $null
}

function Set-TerminalLayout {
    param(
        [string]$Title,
        [int]$Columns,
        [int]$Rows,
        [int]$BufferRows
    )

    try {
        $Host.UI.RawUI.WindowTitle = $Title

        if ($Columns -le 0 -or $Rows -le 0) {
            return
        }

        $rawUI = $Host.UI.RawUI
        $bufferWidth = [Math]::Max($Columns, $rawUI.BufferSize.Width)
        $bufferHeight = [Math]::Max([Math]::Max($BufferRows, $Rows), $rawUI.BufferSize.Height)
        $rawUI.BufferSize = New-Object System.Management.Automation.Host.Size -ArgumentList $bufferWidth, $bufferHeight
        $rawUI.WindowSize = New-Object System.Management.Automation.Host.Size -ArgumentList $Columns, $Rows
    }
    catch {
        Write-Host "Warning: Could not update terminal title/size: $($_.Exception.Message)"
    }
}

trap {
    Write-Host ""
    Write-Host "Startup.ps1 failed before or during app launch."
    Write-Host $_.Exception.Message
    if ($_.ScriptStackTrace) {
        Write-Host ""
        Write-Host $_.ScriptStackTrace
    }
    Wait-BeforeClosingOnError
    exit 1
}

# move working directory to the project folder
Write-Host ">>> cd to the project directory..."
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "<<< Working directory set to: $PWD"
Write-Host ""

# set terminal title and size
$settingsPath = if ($pyArgs.Count -gt 0) { [string]$pyArgs[0] } else { ".\settings.toml" }
$sn = Get-TomlSN -Path $settingsPath
if ([string]::IsNullOrWhiteSpace($sn)) {
    $sn = "unknown"
}
$terminalTitle = "Pico TC-08 logger (SN: $sn)"
Set-TerminalLayout -Title $terminalTitle -Columns $terminalColumns -Rows $terminalRows -BufferRows $terminalBufferRows
Write-Host "Terminal title = $terminalTitle"
Write-Host "Terminal size = ${terminalColumns}x${terminalRows}"
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

if ($exitCode -ne 0) {
    Write-Host "main.py exited with code $exitCode."
    Wait-BeforeClosingOnError
}

exit $exitCode
