# =============================================================================
# test-smoke.ps1
# Local-only smoke tests (no API calls, no deploy, no internet)
# Verifies file structure, HTML validity, and link integrity
#
# USAGE:
#   .\test-smoke.ps1
#   .\test-smoke.ps1 -Verbose
# =============================================================================

[CmdletBinding()]
param(
    [switch]$ShowAll
)

$ErrorActionPreference = "Continue"
$ScriptDir = $PSScriptRoot
$passCount = 0
$failCount = 0
$warnCount = 0

function Test-Pass { param($msg) Write-Host "  [PASS] $msg" -ForegroundColor Green; $script:passCount++ }
function Test-Fail { param($msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red; $script:failCount++ }
function Test-Warn { param($msg) Write-Host "  [WARN] $msg" -ForegroundColor Yellow; $script:warnCount++ }
function Test-Info { param($msg) Write-Host "    $msg" -ForegroundColor Gray }

Write-Host ""
Write-Host "Smoke Tests - sales_pages/" -ForegroundColor Cyan
Write-Host "Location: $ScriptDir" -ForegroundColor Gray
Write-Host ""

# 1. Required files
Write-Host "[1] File structure" -ForegroundColor Cyan
$requiredFiles = @(
    "index.html",
    "products.json",
    "vercel.json",
    "netlify.toml",
    "_redirects",
    "README.md",
    "LAUNCH-CHECKLIST.md",
    "SECURITY.md",
    ".env.example",
    ".gitignore",
    "replace-stripe-links.ps1",
    "deploy-and-test.ps1",
    "STRATEGY.md",
    "validation-strategy.md",
    "email-templates.md",
    "product-09-build-spec.md"
)
foreach ($f in $requiredFiles) {
    $path = Join-Path $ScriptDir $f
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        Test-Pass "$f ($size bytes)"
    }
    else {
        Test-Fail "$f MISSING"
    }
}

# Landing pages
Write-Host ""
Write-Host "[2] Landing pages (10 expected)" -ForegroundColor Cyan
$products = Get-Content (Join-Path $ScriptDir "products.json") -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($p in $products.products) {
    $file = Join-Path $ScriptDir "$($p.slug).html"
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Test-Pass "$($p.slug).html ($size bytes)"
    }
    else {
        Test-Fail "$($p.slug).html MISSING"
    }
}

# Thank-you pages
Write-Host ""
Write-Host "[3] Thank-you pages (10 expected)" -ForegroundColor Cyan
foreach ($p in $products.products) {
    $file = Join-Path $ScriptDir "thanks-$($p.slug).html"
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Test-Pass "thanks-$($p.slug).html ($size bytes)"
    }
    else {
        Test-Fail "thanks-$($p.slug).html MISSING"
    }
}

# Product downloads
Write-Host ""
Write-Host "[4] Product downloads (10 expected)" -ForegroundColor Cyan
$downloadsDir = Join-Path $ScriptDir "downloads"
foreach ($p in $products.products) {
    $found = $false
    $expectedFiles = @("$($p.slug).md", "$($p.slug).html", "$($p.slug)/", "$($p.slug)-guide.md", "$($p.slug)-guide/")
    foreach ($ef in $expectedFiles) {
        if (Test-Path (Join-Path $downloadsDir $ef)) {
            Test-Pass "downloads/$ef"
            $found = $true
            break
        }
    }
    if (-not $found) {
        Test-Fail "downloads/$($p.slug) - none of md/html/folder found"
    }
}

# Demo page
$demoFile = Join-Path $ScriptDir "demo/index.html"
if (Test-Path $demoFile) { Test-Pass "demo/index.html" }
else { Test-Fail "demo/index.html MISSING" }

# Marketing files
Write-Host ""
Write-Host "[5] Marketing files" -ForegroundColor Cyan
$marketingFiles = @("facebook-ads.md", "objection-faq.md", "twitter-x-threads.md", "tiktok-scripts.md", "line-oa-messages.md")
foreach ($f in $marketingFiles) {
    $path = Join-Path $ScriptDir "marketing/$f"
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        Test-Pass "marketing/$f ($size bytes)"
    }
    else {
        Test-Fail "marketing/$f MISSING"
    }
}

# 2. HTML validity (basic check)
Write-Host ""
Write-Host "[6] HTML validity (basic check)" -ForegroundColor Cyan
$htmlFiles = @(Get-ChildItem $ScriptDir -Filter "*.html" -File)
$demoFiles = @(Get-ChildItem (Join-Path $ScriptDir "demo") -Filter "*.html" -File -Recurse -ErrorAction SilentlyContinue)
$downloadFiles = @(Get-ChildItem $downloadsDir -Filter "*.html" -File -Recurse -ErrorAction SilentlyContinue)
$allHtml = @($htmlFiles + $demoFiles + $downloadFiles)

foreach ($f in $allHtml) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8
    if ($content -notmatch 'DOCTYPE html') {
        Test-Fail "$($f.Name): missing DOCTYPE"
    }
    if ($content -notmatch 'html') {
        Test-Fail "$($f.Name): missing html tag"
    }
    if ($content -notmatch 'title') {
        Test-Warn "$($f.Name): missing title tag"
    }
    if ($content -notmatch 'viewport') {
        Test-Warn "$($f.Name): missing viewport meta"
    }
    if ($ShowAll) {
        Test-Info "$($f.Name): basic checks done"
    }
}

# 3. Placeholder check
Write-Host ""
Write-Host "[7] Placeholder check" -ForegroundColor Cyan
$placeholderPattern = "REPLACE_WITH_REAL_LINK"
$unreplaced = 0
foreach ($p in $products.products) {
    $file = Join-Path $ScriptDir "$($p.slug).html"
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -Encoding UTF8
        if ($content -match $placeholderPattern) {
            Test-Warn "$($p.slug).html: still has placeholder (run replace-stripe-links.ps1 or deploy-and-test.ps1)"
            $unreplaced++
        }
        else {
            Test-Pass "$($p.slug).html: placeholder replaced"
        }
    }
}

# 4. Internal link integrity
Write-Host ""
Write-Host "[8] Internal link integrity" -ForegroundColor Cyan
$homepage = Get-Content (Join-Path $ScriptDir "index.html") -Raw -Encoding UTF8
foreach ($p in $products.products) {
    $linkPattern = "$($p.slug).html"
    if ($homepage -match $linkPattern) {
        Test-Pass "index.html links to $linkPattern"
    }
    else {
        Test-Warn "index.html does not link to $linkPattern"
    }
}

# 5. Security checks
Write-Host ""
Write-Host "[9] Security checks" -ForegroundColor Cyan
$envFiles = @(".env", ".env.local", ".env.production")
foreach ($ef in $envFiles) {
    $path = Join-Path $ScriptDir $ef
    if (Test-Path $path) {
        $content = Get-Content $path -Raw -Encoding UTF8
        if ($content -match 'sk_live_[a-zA-Z0-9]+') {
            Test-Fail "${ef}: contains LIVE Stripe key (DO NOT COMMIT)"
        }
        elseif ($content -match 'sk_test_[a-zA-Z0-9]+') {
            Test-Warn "${ef}: contains test key (safe but still .gitignore)"
        }
        else {
            Test-Info "$ef exists but no key detected"
        }
    }
    else {
        Test-Pass "$ef not present (good)"
    }
}

# Hardcoded keys check
$dangerousPattern = "sk_live_[a-zA-Z0-9]{20,}"
$hits = Select-String -Path (Join-Path $ScriptDir "*.html"), (Join-Path $ScriptDir "*.md"), (Join-Path $ScriptDir "*.json"), (Join-Path $ScriptDir "*.ps1") -Pattern $dangerousPattern -ErrorAction SilentlyContinue
if ($hits) {
    foreach ($h in $hits) {
        Test-Fail "LIVE key found in $($h.Path):$($h.LineNumber)"
    }
}
else {
    Test-Pass "No hardcoded sk_live_ keys in code"
}

# .gitignore covers .env
$gitignore = Get-Content (Join-Path $ScriptDir ".gitignore") -Raw -Encoding UTF8
if ($gitignore -match '\.env') {
    Test-Pass ".gitignore covers .env"
}
else {
    Test-Fail ".gitignore does not cover .env"
}

# 6. JSON validity
Write-Host ""
Write-Host "[10] JSON validity" -ForegroundColor Cyan
$jsonFiles = @("products.json")
if (Test-Path (Join-Path $ScriptDir "stripe-links.json")) {
    $jsonFiles += "stripe-links.json"
}
foreach ($jf in $jsonFiles) {
    $path = Join-Path $ScriptDir $jf
    try {
        $content = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
        Test-Pass "${jf}: valid JSON"
    }
    catch {
        Test-Fail "${jf}: INVALID JSON - $($_.Exception.Message)"
    }
}

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Results" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Passed:  $passCount" -ForegroundColor Green
Write-Host "  Warnings: $warnCount" -ForegroundColor Yellow
Write-Host "  Failed:  $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -gt 0) {
    Write-Host "FAIL: Some tests failed. Fix before deploying." -ForegroundColor Red
    exit 1
}
elseif ($warnCount -gt 0) {
    Write-Host "WARN: Tests passed with warnings. Review before deploying." -ForegroundColor Yellow
    exit 0
}
else {
    Write-Host "PASS: All tests passed!" -ForegroundColor Green
    exit 0
}
