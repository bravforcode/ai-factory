# run-with-test-key.ps1
# Wrapper: sets STRIPE_SECRET_KEY then calls deploy-and-test.ps1
# Usage: powershell -File run-with-test-key.ps1 -Phase All|Products|Tests
#
# SECURITY: This file is for one-time use only. DELETE after running.

[CmdletBinding()]
param(
    [string]$StripeKey = "REPLACE_ME",
    [string]$Phase = "All"  # All | Products | Tests
)

# Set the env var
$env:STRIPE_SECRET_KEY = $StripeKey
Write-Host "STRIPE_SECRET_KEY set (length: $($StripeKey.Length))" -ForegroundColor Green

# Build args
$scriptPath = Join-Path $PSScriptRoot "deploy-and-test.ps1"
$deployArgs = @()

switch ($Phase) {
    "All" { }
    "Products" { $deployArgs += "-SkipDeploy", "-SkipTests" }
    "Tests" { $deployArgs += "-SkipStripe" }
    default { Write-Host "Unknown phase: $Phase" -ForegroundColor Red; exit 1 }
}

Write-Host "Running: deploy-and-test.ps1 $($deployArgs -join ' ')" -ForegroundColor Cyan
& $scriptPath @deployArgs
exit $LASTEXITCODE
