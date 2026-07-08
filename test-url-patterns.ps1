param()

$tests = @(
    'https://Ai Factory-sales-pages.vercel.app/t/prompt-pack-th',
    'https://Ai Factory-sales-pages.vercel.app/t/prompt-pack-th/',
    'https://Ai Factory-sales-pages.vercel.app/01-prompt-pack-th.html',
    'https://Ai Factory-sales-pages.vercel.app/01-prompt-pack-th',
    'https://Ai Factory-sales-pages.vercel.app/products',
    'https://Ai Factory-sales-pages.vercel.app/products/',
    'https://Ai Factory-sales-pages.vercel.app/demo',
    'https://Ai Factory-sales-pages.vercel.app/demo/',
    'https://Ai Factory-sales-pages.vercel.app/demo/index.html',
    'https://Ai Factory-sales-pages.vercel.app/thanks/prompt-pack-th',
    'https://Ai Factory-sales-pages.vercel.app/thanks/finance-tracker-thb',
    'https://Ai Factory-sales-pages.vercel.app/buy.stripe.com',
    'https://Ai Factory-sales-pages.vercel.app/vercel.json'
)

Write-Host "URL Pattern Tests" -ForegroundColor Cyan
foreach ($t in $tests) {
    try {
        $r = Invoke-WebRequest -Uri $t -Method Head -UseBasicParsing -TimeoutSec 10 -MaximumRedirection 0 -ErrorAction Stop
        $code = $r.StatusCode
        $color = if ($code -eq 200) { 'Green' } elseif ($code -eq 308) { 'Yellow' } else { 'Yellow' }
        Write-Host "  [$code] $t" -ForegroundColor $color
    }
    catch {
        $code = $_.Exception.Response.StatusCode.value__
        if (-not $code) { $code = 'ERR' }
        $color = if ($code -eq 200 -or $code -eq 308) { 'Green' } else { 'Red' }
        Write-Host "  [$code] $t" -ForegroundColor $color
    }
}
