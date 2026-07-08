# =============================================================================
# test-deployed.ps1
# Smoke test against deployed Vercel URL
# =============================================================================

param(
    [string]$BaseUrl = "https://Ai Factory-sales-pages.vercel.app"
)

$ErrorActionPreference = "Continue"
$passCount = 0
$failCount = 0

function Test-Pass { param($msg) Write-Host "  [PASS] $msg" -ForegroundColor Green; $script:passCount++ }
function Test-Fail { param($msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red; $script:failCount++ }
function Test-Info { param($msg) Write-Host "    $msg" -ForegroundColor Gray }

Write-Host ""
Write-Host "Smoke Test - Deployed site" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host ""

# Test pages
$pages = @(
    @{ Path = "/"; Name = "Homepage" },
    @{ Path = "/01-prompt-pack-th"; Name = "Product 1 (Prompt Pack)" },
    @{ Path = "/02-obsidian-student-kit"; Name = "Product 2 (Obsidian)" },
    @{ Path = "/03-freelance-pricing-calculator"; Name = "Product 3 (Calculator)" },
    @{ Path = "/04-cold-email-template-pack"; Name = "Product 4 (Cold Email)" },
    @{ Path = "/05-ai-automation-workflow"; Name = "Product 5 (AI Automation)" },
    @{ Path = "/06-cv-international-template"; Name = "Product 6 (CV)" },
    @{ Path = "/07-n8n-sme-workflow-pack"; Name = "Product 7 (n8n)" },
    @{ Path = "/08-content-calendar-90d"; Name = "Product 8 (Calendar)" },
    @{ Path = "/09-finance-tracker-thb"; Name = "Product 9 (Finance)" },
    @{ Path = "/10-ai-agent-starter-github"; Name = "Product 10 (AI Agent)" },
    @{ Path = "/thanks-01-prompt-pack-th"; Name = "Thanks 1" },
    @{ Path = "/thanks-09-finance-tracker-thb"; Name = "Thanks 9" },
    @{ Path = "/demo"; Name = "Demo" }
)

Write-Host "[1] HTTP Status Tests" -ForegroundColor Cyan
foreach ($p in $pages) {
    $url = "$BaseUrl$($p.Path)"
    try {
        $r = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            Test-Pass "$($p.Name) ($($p.Path)) -> 200"
        }
        else {
            Test-Fail "$($p.Name) ($($p.Path)) -> $($r.StatusCode)"
        }
    }
    catch {
        $code = $_.Exception.Response.StatusCode.value__
        if (-not $code) { $code = "ERR" }
        Test-Fail "$($p.Name) ($($p.Path)) -> $code ($($_.Exception.Message))"
    }
}

# Test rewrites
Write-Host ""
Write-Host "[2] Rewrite Tests (clean URLs)" -ForegroundColor Cyan
$rewrites = @(
    @{ Path = "/t/prompt-pack-th"; Expect = "01-prompt-pack-th" },
    @{ Path = "/t/finance-tracker-thb"; Expect = "09-finance-tracker-thb" },
    @{ Path = "/products"; Expect = "index.html" }
)

foreach ($r in $rewrites) {
    $url = "$BaseUrl$($r.Path)"
    try {
        $resp = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop -MaximumRedirection 0
        Test-Pass "$($r.Path) -> 200"
    }
    catch {
        $code = $_.Exception.Response.StatusCode.value__
        if ($code -eq 200 -or $code -eq 308) {
            Test-Pass "$($r.Path) -> $code (redirect/rewrite)"
        }
        else {
            Test-Fail "$($r.Path) -> $code"
        }
    }
}

# Test content
Write-Host ""
Write-Host "[3] Content Tests" -ForegroundColor Cyan
$contentTests = @(
    @{ Path = "/"; Contains = "Ai Factory" },
    @{ Path = "/01-prompt-pack-th"; Contains = "buy.stripe.com" },
    @{ Path = "/thanks-01-prompt-pack-th"; Contains = "thank" }
)

foreach ($c in $contentTests) {
    $url = "$BaseUrl$($c.Path)"
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop
        $content = $resp.Content
        if ($content -match $c.Contains) {
            Test-Pass "$($c.Path) contains '$($c.Contains)'"
        }
        else {
            Test-Fail "$($c.Path) missing '$($c.Contains)'"
        }
    }
    catch {
        Test-Fail "$($c.Path) - cannot fetch: $($_.Exception.Message)"
    }
}

# Test security headers
Write-Host ""
Write-Host "[4] Security Headers" -ForegroundColor Cyan
try {
    $resp = Invoke-WebRequest -Uri "$BaseUrl/" -Method Head -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop
    $headers = $resp.Headers
    $expectedHeaders = @(
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Strict-Transport-Security"
    )
    foreach ($h in $expectedHeaders) {
        $val = $headers[$h]
        if ($val) {
            Test-Pass "$h = $val"
        }
        else {
            Test-Fail "$h MISSING"
        }
    }
}
catch {
    Test-Fail "Cannot fetch headers: $($_.Exception.Message)"
}

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Results" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Passed: $passCount" -ForegroundColor Green
Write-Host "  Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -gt 0) {
    Write-Host "Some tests failed. Check above." -ForegroundColor Yellow
    exit 1
}
else {
    Write-Host "All deployed pages working!" -ForegroundColor Green
    exit 0
}
