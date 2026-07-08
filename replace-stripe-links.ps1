# ============================================================================
# replace-stripe-links.ps1
# Replaces {{STRIPE_LINK}} placeholders in landing page HTML files with real
# Stripe Payment Links.
#
# Usage:
#   1. Create all 10 Payment Links in your Stripe Dashboard (LIVE mode)
#   2. Update stripe-links.json with the live URLs
#   3. Run this script in PowerShell: .\replace-stripe-links.ps1
#   4. Script reads URLs from stripe-links.json and replaces placeholders
#   5. Script writes a summary at the end
#
# Run from: C:\Users\menum\sales_pages\
#
# LIVE PAYMENT LINKS — paste your 10 live URLs here:
#   01: https://buy.stripe.com/___LIVE_LINK_01___
#   02: https://buy.stripe.com/___LIVE_LINK_02___
#   03: https://buy.stripe.com/___LIVE_LINK_03___
#   04: https://buy.stripe.com/___LIVE_LINK_04___
#   05: https://buy.stripe.com/___LIVE_LINK_05___
#   06: https://buy.stripe.com/___LIVE_LINK_06___
#   07: https://buy.stripe.com/___LIVE_LINK_07___
#   08: https://buy.stripe.com/___LIVE_LINK_08___
#   09: https://buy.stripe.com/___LIVE_LINK_09___
#   10: https://buy.stripe.com/___LIVE_LINK_10___
# ============================================================================

$ErrorActionPreference = "Stop"
$folder = $PSScriptRoot
$pattern = '0?\d-*.html'
$placeholderRegex = 'https://buy\.stripe\.com/REPLACE_WITH_REAL_LINK_FOR_[A-Z0-9-]+'

# Color helpers (work on PS 5.1+)
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Warn    { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Err     { param($msg) Write-Host $msg -ForegroundColor Red }
function Write-Info    { param($msg) Write-Host $msg -ForegroundColor Cyan }

# Find target files
$files = Get-ChildItem -Path $folder -Filter "*.html" -File |
    Where-Object { $_.Name -match "^$pattern$" } |
    Sort-Object Name

if (-not $files) {
    Write-Err "No landing page HTML files found in $folder"
    Write-Err "Expected files matching: 01-...html through 10-...html"
    exit 1
}

Write-Info ""
Write-Info "Found $($files.Count) landing page file(s):"
$files | ForEach-Object { Write-Info "  - $($_.Name)" }
Write-Info ""
Write-Info "For each file, paste the Stripe Payment Link."
Write-Info "Press Enter to skip (placeholder will remain)."
Write-Info ""

$results = @()
$skipped = 0
$updated = 0

foreach ($file in $files) {
    Write-Info "=== $($file.Name) ==="
    $link = Read-Host "Stripe Payment Link (Enter to skip)"

    if ([string]::IsNullOrWhiteSpace($link)) {
        Write-Warn "  Skipped"
        $results += [PSCustomObject]@{ File = $file.Name; Status = "Skipped" }
        $skipped++
        continue
    }

    # Basic validation: must look like a Stripe link
    if ($link -notmatch '^https://buy\.stripe\.com/') {
        Write-Err "  Invalid Stripe link (must start with https://buy.stripe.com/)"
        $results += [PSCustomObject]@{ File = $file.Name; Status = "Invalid link" }
        $skipped++
        continue
    }

    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        if ($content -notmatch $placeholderRegex) {
            Write-Warn "  No placeholder found in this file (already updated?)"
            $results += [PSCustomObject]@{ File = $file.Name; Status = "No placeholder" }
            $skipped++
            continue
        }
        $newContent = $content -replace $placeholderRegex, $link
        Set-Content -Path $file.FullName -Value $newContent -NoNewline -Encoding UTF8
        Write-Success "  Updated"
        $results += [PSCustomObject]@{ File = $file.Name; Status = "Updated" }
        $updated++
    }
    catch {
        Write-Err "  Failed: $($_.Exception.Message)"
        $results += [PSCustomObject]@{ File = $file.Name; Status = "Error: $($_.Exception.Message)" }
    }

    Write-Info ""
}

# Summary
Write-Info "================================================"
Write-Info "  Summary"
Write-Info "================================================"
$results | Format-Table -AutoSize | Out-String | Write-Host
Write-Info "Updated: $updated | Skipped: $skipped | Total: $($files.Count)"
Write-Info ""

if ($updated -gt 0) {
    Write-Success "Done! Your landing pages are now live-ready."
    Write-Info "Next steps:"
    Write-Info "  1. Open one of the HTML files and verify the link"
    Write-Info "  2. Deploy to Netlify (drag & drop this folder)"
    Write-Info "  3. Test the payment flow with card 4242 4242 4242 4242 (test mode)"
} else {
    Write-Warn "No files were updated. Run again when you have Payment Links ready."
}
