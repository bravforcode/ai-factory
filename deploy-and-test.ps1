# =============================================================================
# deploy-and-test.ps1
# End-to-end deploy + smoke test for sales_pages
#
# SAFE BY DESIGN:
#   - Reads ALL secrets from environment variables (NEVER from chat/files)
#   - Uses Stripe TEST mode by default (set -Live for production)
#   - Refuses to run if STRIPE_SECRET_KEY looks like sk_live_ + not in -Live mode
#   - No real customer charges in test mode
#
# USAGE:
#   # Test mode (safe, no real money):
#   $env:STRIPE_SECRET_KEY = "sk_test_xxxxxxxxxxxxx"
#   $env:VERCEL_TOKEN = "your_vercel_token"
#   .\deploy-and-test.ps1
#
#   # Live mode (real money, double-check before running):
#   $env:STRIPE_SECRET_KEY = "sk_live_xxxxxxxxxxxxx"
#   $env:VERCEL_TOKEN = "your_vercel_token"
#   .\deploy-and-test.ps1 -Live
#
# PREREQUISITES:
#   - PowerShell 5.1+ (Windows default) or PowerShell 7+ (cross-platform)
#   - Vercel CLI: `npm install -g vercel`
#   - Stripe API key with write access to Products
# =============================================================================

[CmdletBinding()]
param(
    [switch]$Live,
    [switch]$SkipDeploy,
    [switch]$SkipStripe,
    [switch]$SkipTests,
    [string]$VercelProjectName = "Ai Factory-sales-pages",
    [string]$StripeKey = "",  # Optional: pass inline instead of env var (NOT for chat)
    [string]$VercelToken = ""  # Optional: pass inline instead of env var (NOT for chat)
)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$ProductsJsonPath = Join-Path $ScriptDir "products.json"
$LogFile = Join-Path $ScriptDir "deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Write-Step { param($msg) Write-Host "`n>> $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "    $msg" -ForegroundColor Gray }

Start-Transcript -Path $LogFile -Append | Out-Null

# =============================================================================
# 0. Safety checks
# =============================================================================
Write-Step "Phase 0: Safety checks"

# Accept key from -StripeKey param or env var
if ($StripeKey) {
    $stripeKey = $StripeKey
    Write-Info "Using Stripe key from -StripeKey parameter (length: $($stripeKey.Length))"
}
else {
    $stripeKey = $env:STRIPE_SECRET_KEY
    Write-Info "Using Stripe key from `$env:STRIPE_SECRET_KEY"
}
$vercelToken = $env:VERCEL_TOKEN
if ($VercelToken) {
    $vercelToken = $VercelToken
    Write-Info "Using Vercel token from -VercelToken parameter (length: $($vercelToken.Length))"
}

if (-not $stripeKey) {
    Write-Err "STRIPE_SECRET_KEY env var is empty"
    Write-Info "Set it first:"
    Write-Info "  PowerShell: `$env:STRIPE_SECRET_KEY = 'sk_test_xxxxxxxxx'"
    Write-Info "  Bash:       export STRIPE_SECRET_KEY='sk_test_xxxxxxxxx'"
    Write-Info "Get a test key: https://dashboard.stripe.com/test/apikeys"
    Stop-Transcript | Out-Null
    exit 1
}

if ($stripeKey -match '^sk_live_' -and -not $Live) {
    Write-Err "STRIPE_SECRET_KEY starts with sk_live_ but -Live flag not set"
    Write-Info "This is a SAFETY guard. Live mode = real money."
    Write-Info "If intentional, re-run with: .\deploy-and-test.ps1 -Live"
    Stop-Transcript | Out-Null
    exit 1
}

if ($Live) {
    Write-Warn "LIVE MODE - real money will be charged to customers"
    Write-Warn "Press Ctrl+C in 5 seconds to cancel..."
    Start-Sleep -Seconds 5
    Write-OK "Continuing in LIVE mode (you waited 5s)"
}

$expectedPrefix = if ($Live) { "sk_live_" } else { "sk_test_" }
if (-not $stripeKey.StartsWith($expectedPrefix)) {
    Write-Err "Key does not start with $expectedPrefix (Live=$Live)"
    Stop-Transcript | Out-Null
    exit 1
}
Write-OK "Stripe key format: $expectedPrefix***"

if (-not (Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Err "vercel CLI not found. Install: npm install -g vercel"
    Stop-Transcript | Out-Null
    exit 1
}
Write-OK "Vercel CLI: $(vercel --version)"

if (-not (Test-Path $ProductsJsonPath)) {
    Write-Err "products.json not found at $ProductsJsonPath"
    Stop-Transcript | Out-Null
    exit 1
}
$products = Get-Content $ProductsJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
Write-OK "Loaded $($products.products.Count) products from products.json"

# =============================================================================
# 1. Create Stripe products + payment links
# =============================================================================
$createdLinks = @{}
$linkMapPath = Join-Path $ScriptDir "stripe-links.json"

if (-not $SkipStripe) {
    Write-Step "Phase 1: Create Stripe products + payment links"

    if (Test-Path $linkMapPath) {
        Write-Warn "stripe-links.json exists - will skip products that already have a link"
        $existing = Get-Content $linkMapPath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($p in $existing.PSObject.Properties) {
            $createdLinks[$p.Name] = $p.Value
        }
    }

    foreach ($p in $products.products) {
        $slug = $p.slug
        Write-Info "Processing: $slug ($($p.name_th)) - $($p.price_thb) THB"

        if ($createdLinks[$slug]) {
            Write-OK "  Already exists: $($createdLinks[$slug])"
            continue
        }

        # Create product (form-urlencoded)
        $productBody = @{
            "name" = $p.name_th
            "description" = $p.tagline
            "metadata[slug]" = $slug
            "metadata[source]" = "Ai Factory-sales-pages"
            "metadata[created_at]" = (Get-Date).ToString("o")
        }

        try {
            $productResp = Invoke-RestMethod -Uri "https://api.stripe.com/v1/products" `
                -Method Post -Headers @{ Authorization = "Bearer $stripeKey" } `
                -Body $productBody -ErrorAction Stop
            Write-OK "  Product created: $($productResp.id)"
        }
        catch {
            $errDetail = $_.Exception.Message
            if ($_.Exception.Response) {
                try {
                    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                    $errDetail = $reader.ReadToEnd()
                } catch {}
            }
            Write-Err "  Failed to create product: $errDetail"
            continue
        }

        # Create price
        $priceBody = @{
            "product" = $productResp.id
            "unit_amount" = ($p.price_thb * 100)
            "currency" = "thb"
        }

        try {
            $priceResp = Invoke-RestMethod -Uri "https://api.stripe.com/v1/prices" `
                -Method Post -Headers @{ Authorization = "Bearer $stripeKey" } `
                -Body $priceBody -ErrorAction Stop
            Write-OK "  Price created: $($priceResp.id) ($($p.price_thb) THB)"
        }
        catch {
            $errDetail = $_.Exception.Message
            if ($_.Exception.Response) {
                try {
                    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                    $errDetail = $reader.ReadToEnd()
                } catch {}
            }
            Write-Err "  Failed to create price: $errDetail"
            continue
        }

        # Create payment link (form-urlencoded with bracketed keys)
        $successUrl = "https://$VercelProjectName.vercel.app/thanks-$slug.html"
        $linkBody = @{
            "line_items[0][price]" = $priceResp.id
            "line_items[0][quantity]" = "1"
            "after_completion[type]" = "redirect"
            "after_completion[redirect][url]" = $successUrl
            "metadata[slug]" = $slug
        }

        try {
            $linkResp = Invoke-RestMethod -Uri "https://api.stripe.com/v1/payment_links" `
                -Method Post -Headers @{ Authorization = "Bearer $stripeKey" } `
                -Body $linkBody -ErrorAction Stop
            Write-OK "  Payment link: $($linkResp.url)"
            $createdLinks[$slug] = $linkResp.url
        }
        catch {
            $errDetail = $_.Exception.Message
            if ($_.Exception.Response) {
                try {
                    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                    $errDetail = $reader.ReadToEnd()
                } catch {}
            }
            Write-Err "  Failed to create payment link: $errDetail"
        }
    }

    # Save link map
    $createdLinks | ConvertTo-Json | Out-File $linkMapPath -Encoding UTF8
    Write-OK "Saved link map to stripe-links.json"
}
else {
    Write-Warn "Phase 1 skipped (-SkipStripe)"
    if (Test-Path $linkMapPath) {
        $existing = Get-Content $linkMapPath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($p in $existing.PSObject.Properties) {
            $createdLinks[$p.Name] = $p.Value
        }
        Write-OK "Loaded $($createdLinks.Count) existing links"
    }
}

# =============================================================================
# 2. Replace placeholders in landing pages
# =============================================================================
Write-Step "Phase 2: Replace placeholders in HTML files"

$replacedCount = 0
foreach ($p in $products.products) {
    $slug = $p.slug
    $file = Join-Path $ScriptDir "$slug.html"
    if (-not (Test-Path $file)) {
        Write-Warn "  $slug.html not found, skipping"
        continue
    }

    $content = Get-Content $file -Raw -Encoding UTF8
    $original = $content
    $placeholder = "https://buy.stripe.com/REPLACE_WITH_REAL_LINK_FOR_$($slug.ToUpper())"

    if ($createdLinks[$slug]) {
        $content = $content.Replace($placeholder, $createdLinks[$slug])
    }
    else {
        Write-Warn "  No link for $slug - placeholder kept"
        continue
    }

    if ($content -ne $original) {
        Set-Content $file -Value $content -NoNewline -Encoding UTF8
        Write-OK "  $slug.html: placeholder replaced"
        $replacedCount++
    }
    else {
        Write-Info "  $slug.html: no change"
    }
}
Write-OK "Replaced $replacedCount placeholders"

# =============================================================================
# 3. Deploy to Vercel
# =============================================================================
$deployedUrl = $null
if (-not $SkipDeploy) {
    Write-Step "Phase 3: Deploy to Vercel"

    Push-Location $ScriptDir
    try {
        $vercelJsonPath = Join-Path $ScriptDir "vercel.json"
        if (-not (Test-Path $vercelJsonPath)) {
            Write-Warn "  vercel.json not found - using defaults"
        }

        $vercelArgs = @("deploy", "--prod", "--yes")
        if ($vercelToken) {
            $vercelArgs += @("--token", $vercelToken)
        }
        $vercelArgs += @("--name", $VercelProjectName)

        Write-Info "Running: vercel $($vercelArgs -join ' ')"
        $vercelOutput = & vercel @vercelArgs 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-OK "Vercel deploy succeeded"
            $vercelText = $vercelOutput | Out-String
            $urlMatch = [regex]::Match($vercelText, 'https://[a-z0-9-]+\.vercel\.app')
            if ($urlMatch.Success) {
                $deployedUrl = $urlMatch.Value
                Write-OK "Deployed to: $deployedUrl"
            }
        }
        else {
            Write-Err "Vercel deploy failed (exit $LASTEXITCODE)"
            $vercelOutput | ForEach-Object { Write-Info $_ }
        }
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Warn "Phase 3 skipped (-SkipDeploy)"
}

# =============================================================================
# 4. Smoke tests
# =============================================================================
if (-not $SkipTests) {
    Write-Step "Phase 4: Smoke tests"

    $baseUrl = if ($deployedUrl) { $deployedUrl } else { "http://localhost:3000" }
    Write-Info "Testing against: $baseUrl"

    $testPages = @("index.html")
    foreach ($p in $products.products) {
        $testPages += "$($p.slug).html"
    }
    foreach ($p in $products.products) {
        $testPages += "thanks-$($p.slug).html"
    }
    $passCount = 0
    $failCount = 0

    foreach ($page in $testPages) {
        $url = "$baseUrl/$page"
        try {
            $resp = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                Write-OK "  $page -> 200"
                $passCount++
            }
            else {
                Write-Warn "  $page -> $($resp.StatusCode)"
                $failCount++
            }
        }
        catch {
            Write-Err "  $page -> FAILED ($($_.Exception.Message))"
            $failCount++
        }
    }

    # Verify no placeholders remain
    Write-Info "Checking for unreplaced placeholders..."
    $placeholderPattern = "REPLACE_WITH_REAL_LINK"
    $unreplaced = 0
    foreach ($p in $products.products) {
        $file = Join-Path $ScriptDir "$($p.slug).html"
        if (Test-Path $file) {
            $content = Get-Content $file -Raw -Encoding UTF8
            if ($content -match $placeholderPattern) {
                Write-Err "  $($p.slug).html: still has placeholder"
                $unreplaced++
            }
        }
    }
    if ($unreplaced -eq 0) {
        Write-OK "  All placeholders replaced"
    }

    # Mock payment note
    if (-not $Live -and $createdLinks.Count -gt 0) {
        Write-Info "Mock payment test: use Stripe test card 4242 4242 4242 4242"
        $firstLink = ($createdLinks.GetEnumerator() | Select-Object -First 1).Value
        Write-Info "First test link: $firstLink"
    }
    elseif ($Live) {
        Write-Warn "  Skipping mock payment test in LIVE mode"
        Write-Info "  To test live: use real card with small amount, then refund"
    }

    Write-OK "Smoke tests: $passCount passed, $failCount failed"
    if ($failCount -gt 0) { $exitCode = 1 } else { $exitCode = 0 }
}
else {
    Write-Warn "Phase 4 skipped (-SkipTests)"
    $exitCode = 0
}

# =============================================================================
# Summary
# =============================================================================
Write-Step "Summary"
Write-Info "Log: $LogFile"
Write-Info "Products created: $($createdLinks.Count)"
Write-Info "Placeholders replaced: $replacedCount"
if ($deployedUrl) {
    Write-Info "Deployed: $deployedUrl"
    Write-OK "Done! Test the funnel at $deployedUrl"
}
else {
    Write-Warn "Not deployed. Run without -SkipDeploy to deploy."
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Visit the homepage and click through each product" -ForegroundColor White
Write-Host "  2. Test 1 payment with card 4242 4242 4242 4242 (test mode)" -ForegroundColor White
Write-Host "  3. Verify thank-you page redirect works" -ForegroundColor White
Write-Host "  4. If live, do a real test with a refundable card" -ForegroundColor White
Write-Host "  5. Run -Live flag for production" -ForegroundColor White

Stop-Transcript | Out-Null
exit $exitCode
