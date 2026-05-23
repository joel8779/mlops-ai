$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

function Resolve-ProjectPython {
    $candidates = @(
        @("py", "-3.11"),
        @("py", "-3.12"),
        @("python", "")
    )
    foreach ($candidate in $candidates) {
        $exe = $candidate[0]
        $versionArg = $candidate[1]
        $args = @()
        if ($versionArg) {
            $args += $versionArg
        }
        $args += @("-c", "import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 13) else 1)")
        try {
            & $exe @args *> $null
            if ($LASTEXITCODE -eq 0) {
                return @($exe, $versionArg) | Where-Object { $_ }
            }
        }
        catch {
            continue
        }
    }
    throw "Python 3.11 or 3.12 is required. Install Python 3.11/3.12, then rerun scripts\bootstrap.ps1."
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Update secrets before production use."
}

$ProjectPython = Resolve-ProjectPython
$VenvArgs = @()
if ($ProjectPython.Length -gt 1) {
    $VenvArgs += $ProjectPython[1..($ProjectPython.Length - 1)]
}
$VenvArgs += @("-m", "venv", ".venv")
Invoke-Checked $ProjectPython[0] @VenvArgs
Invoke-Checked ".\.venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
Invoke-Checked ".\.venv\Scripts\python.exe" -m pip install -r apps/api/requirements-dev.txt

if (Test-Path "apps\web\package.json") {
    Push-Location "apps\web"
    Invoke-Checked "npm" install
    Pop-Location
}

Invoke-Checked ".\.venv\Scripts\python.exe" scripts\verify_env.py
Write-Host "Bootstrap complete. Activate with: .\.venv\Scripts\Activate.ps1"
