<# 
  Add Dark Mode to ALL sales pages
  Run from: C:\Users\menum\sales_pages
#>

$ErrorActionPreference = "Stop"
$baseDir = "C:\Users\menum\sales_pages"

# Files to process (exclude templates, og-image, inspect-stripe, downloads, demo)
$files = @(
    "index.html",
    "01-prompt-pack-th.html",
    "02-obsidian-student-kit.html",
    "03-freelance-pricing-calculator.html",
    "04-cold-email-template-pack.html",
    "05-ai-automation-workflow.html",
    "06-cv-international-template.html",
    "07-n8n-sme-workflow-pack.html",
    "08-content-calendar-90d.html",
    "09-finance-tracker-thb.html",
    "10-ai-agent-starter-github.html",
    "thanks-01-prompt-pack-th.html",
    "thanks-02-obsidian-student-kit.html",
    "thanks-03-freelance-pricing-calculator.html",
    "thanks-04-cold-email-template-pack.html",
    "thanks-05-ai-automation-workflow.html",
    "thanks-06-cv-international-template.html",
    "thanks-07-n8n-sme-workflow-pack.html",
    "thanks-08-content-calendar-90d.html",
    "thanks-09-finance-tracker-thb.html",
    "thanks-10-ai-agent-starter-github.html"
)

# Also process templates
$files += "_template.html", "_thanks_template.html"

# ============================================
# DARK MODE INJECTION SNIPPETS
# ============================================

# Script to load preference immediately (goes in <head> before closing tag)
$headScript = @'
<script>
  // Dark mode - load preference immediately to prevent flash
  (function() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    }
  })();
</script>
'@

# Tailwind dark mode config (for Tailwind pages only)
$tailwindConfig = @'
<script>
  tailwind.config = {
    darkMode: 'class',
  }
</script>
'@

# Dark mode CSS overrides (for Tailwind pages)
$darkModeCSS = @'
<style id="dark-mode-overrides">
  /* Dark mode overrides for Tailwind classes */
  .dark body { background-color: #0f172a !important; color: #f1f5f9 !important; }
  .dark .bg-white { background-color: #1e293b !important; }
  .dark .bg-slate-50 { background-color: #1e293b !important; }
  .dark .bg-slate-900 { background-color: #020617 !important; }
  .dark .text-slate-900 { color: #f1f5f9 !important; }
  .dark .text-slate-700 { color: #e2e8f0 !important; }
  .dark .text-slate-600 { color: #cbd5e1 !important; }
  .dark .text-slate-500 { color: #94a3b8 !important; }
  .dark .text-slate-400 { color: #64748b !important; }
  .dark .border-slate-200 { border-color: #334155 !important; }
  .dark .border-t-2 { border-color: #6366f1 !important; }
  .dark details { background-color: #1e293b !important; }
  .dark .bg-purple-100 { background-color: #312e81 !important; }
  .dark .bg-gradient-to-r { background: linear-gradient(to right, #1e293b, #1e293b) !important; }
  .dark .from-purple-50 { --tw-gradient-from: #1e293b !important; }
  .dark .to-blue-50 { --tw-gradient-to: #1e293b !important; }
  /* Fix gradient sections for dark mode */
  .dark .gradient-hero, .dark .gradient-final, .dark .gradient-success { opacity: 0.9; }
  /* Fix sticky CTA bar */
  .dark .fixed.bottom-0 { background-color: #1e293b !important; border-color: #6366f1 !important; }
</style>
'@

# Toggle button HTML (for pages with nav or sticky CTA)
# We'll inject it after the opening <body> tag or after the sticky CTA
$toggleButton = @'
<button id="theme-toggle" class="fixed top-4 right-4 z-50 bg-white/80 dark:bg-slate-800/80 backdrop-blur border border-slate-200 dark:border-slate-600 rounded-full p-2 shadow-lg hover:scale-110 transition-all duration-300" aria-label="Toggle dark mode" style="position:fixed;top:16px;right:16px;z-index:9999;">
  <svg class="sun-icon w-5 h-5 text-amber-500" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
  </svg>
  <svg class="moon-icon w-5 h-5 text-indigo-400" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
</button>
'@

# Toggle script (goes before </body>)
$toggleScript = @'
<script>
  (function() {
    const toggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    function updateIcon() {
      const isDark = html.classList.contains('dark');
      const sun = toggle.querySelector('.sun-icon');
      const moon = toggle.querySelector('.moon-icon');
      if (sun) sun.style.display = isDark ? 'none' : 'block';
      if (moon) moon.style.display = isDark ? 'block' : 'none';
    }
    
    toggle.addEventListener('click', function() {
      html.classList.toggle('dark');
      localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
      updateIcon();
    });
    
    updateIcon();
  })();
</script>
'@

# ============================================
# PROCESS EACH FILE
# ============================================

foreach ($file in $files) {
    $filePath = Join-Path $baseDir $file
    if (-not (Test-Path $filePath)) {
        Write-Host "SKIP: $file (not found)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "Processing: $file" -ForegroundColor Cyan
    $content = Get-Content -Path $filePath -Raw -Encoding UTF8
    
    # Skip if already processed
    if ($content -match 'theme-toggle') {
        Write-Host "  -> Already has dark mode, skipping" -ForegroundColor Gray
        continue
    }
    
    $isTailwind = $content -match 'tailwindcss'
    $isIndex = $file -eq 'index.html'
    
    # ---- STEP 1: Add immediate load script in <head> ----
    $content = $content -replace '(</head>)', "`n$headScript`n`$1"
    
    # ---- STEP 2: Add Tailwind config if Tailwind page ----
    if ($isTailwind) {
        # Add tailwind config right after the tailwindcss script tag
        $content = $content -replace '(<script src="https://cdn\.tailwindcss\.com"></script>)', "`$1`n$tailwindConfig"
        
        # Add dark mode CSS overrides in <style> or before </head>
        $content = $content -replace '(</head>)', "`n$darkModeCSS`n`$1"
    }
    
    # ---- STEP 3: For index.html, add CSS variables ----
    if ($isIndex) {
        $cssVars = @'
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #cbd5e1;
  --text-muted: #64748b;
  --border: #334155;
  --accent: #818cf8;
  --accent-hover: #6366f1;
  --success: #34d399;
  --warning: #fbbf24;
  --danger: #f87171;
}
:not(.dark) {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-card: #ffffff;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --border: #e2e8f0;
  --accent: #6366f1;
  --accent-hover: #4f46e5;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
}
'@
        # Inject CSS variables before the closing </style> in the first <style> block
        $content = $content -replace '(\.note p \{[^}]*color: #94a3b8;[^}]*line-height: 1\.6;\s*\})', "`$1`n`n$cssVars"
        
        # Add dark mode body styles
        $darkBodyCSS = @'

.dark body {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #f1f5f9;
}
.dark .tagline { color: #cbd5e1; }
.dark .subtext { color: #94a3b8; }
.dark .note { background: rgba(255,255,255,0.03); border-left-color: #818cf8; }
.dark .note p { color: #94a3b8; }
'@
        $content = $content -replace '(\.note p \{[^}]*color: #94a3b8;[^}]*line-height: 1\.6;\s*\})', "`$1`n$darkBodyCSS"
    }
    
    # ---- STEP 4: Add toggle button after <body> ----
    $content = $content -replace '(<body[^>]*>)', "`$1`n$toggleButton"
    
    # ---- STEP 5: Add toggle script before </body> ----
    $content = $content -replace '(</body>)', "`n$toggleScript`n`$1"
    
    # ---- STEP 6: For Tailwind pages, fix dark mode specific classes ----
    if ($isTailwind) {
        # Fix the sticky CTA bar - add dark mode classes
        $content = $content -replace 'class="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t-2 border-purple-600 p-3 shadow-2xl"', 'class="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-slate-800 border-t-2 border-purple-600 p-3 shadow-2xl dark:border-indigo-500"'
        
        # Fix body class to support dark mode
        $content = $content -replace 'class="bg-white text-slate-900 antialiased"', 'class="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 antialiased transition-colors duration-300"'
        
        # Fix sections with bg-slate-50
        $content = $content -replace 'class="py-16 md:py-24 px-4 bg-slate-50"', 'class="py-16 md:py-24 px-4 bg-slate-50 dark:bg-slate-800"'
        
        # Fix white cards
        $content = $content -replace 'class="bg-white p-6 rounded-xl shadow-sm flex items-start gap-4"', 'class="bg-white dark:bg-slate-700 p-6 rounded-xl shadow-sm flex items-start gap-4 dark:border dark:border-slate-600"'
        $content = $content -replace 'class="bg-white p-6 rounded-xl shadow-sm"', 'class="bg-white dark:bg-slate-700 p-6 rounded-xl shadow-sm dark:border dark:border-slate-600"'
        $content = $content -replace 'class="bg-white border-4 border-purple-600 rounded-3xl p-8 md:p-10 shadow-2xl"', 'class="bg-white dark:bg-slate-800 border-4 border-purple-600 rounded-3xl p-8 md:p-10 shadow-2xl dark:border-indigo-500 transition-colors duration-300"'
        $content = $content -replace 'class="bg-white border-4 border-green-500 rounded-3xl p-8 md:p-10 shadow-2xl"', 'class="bg-white dark:bg-slate-800 border-4 border-green-500 rounded-3xl p-8 md:p-10 shadow-2xl dark:border-green-400 transition-colors duration-300"'
        
        # Fix pricing card text colors
        $content = $content -replace 'class="text-center text-slate-500 mb-8"', 'class="text-center text-slate-500 dark:text-slate-400 mb-8"'
        $content = $content -replace 'class="text-2xl text-slate-500"', 'class="text-2xl text-slate-500 dark:text-slate-400"'
        $content = $content -replace 'class="text-center text-sm text-slate-500 mt-4"', 'class="text-center text-sm text-slate-500 dark:text-slate-400 mt-4"'
        $content = $content -replace 'class="space-y-3 mb-8 text-slate-700"', 'class="space-y-3 mb-8 text-slate-700 dark:text-slate-300"'
        
        # Fix solution section
        $content = $content -replace 'class="text-center text-slate-600 mb-12 text-lg"', 'class="text-center text-slate-600 dark:text-slate-400 mb-12 text-lg"'
        $content = $content -replace 'class="bg-purple-100 text-purple-600 rounded-full flex items-center justify-center font-bold text-xl"', 'class="bg-purple-100 dark:bg-indigo-900 text-purple-600 dark:text-indigo-400 rounded-full flex items-center justify-center font-bold text-xl"'
        
        # Fix included items text
        $content = $content -replace 'class="text-slate-600 mt-1"', 'class="text-slate-600 dark:text-slate-400 mt-1"'
        
        # Fix FAQ
        $content = $content -replace 'class="mt-4 text-slate-600 leading-relaxed"', 'class="mt-4 text-slate-600 dark:text-slate-400 leading-relaxed"'
        
        # Fix footer
        $content = $content -replace 'class="py-10 px-4 bg-slate-900 text-slate-400 text-center text-sm"', 'class="py-10 px-4 bg-slate-900 dark:bg-black text-slate-400 dark:text-slate-500 text-center text-sm transition-colors duration-300"'
        $content = $content -replace 'class="py-8 px-4 bg-slate-900 text-slate-400 text-center text-sm"', 'class="py-8 px-4 bg-slate-900 dark:bg-black text-slate-400 dark:text-slate-500 text-center text-sm transition-colors duration-300"'
        
        # Fix thanks page specific elements
        $content = $content -replace 'class="border-t border-slate-200 pt-6"', 'class="border-t border-slate-200 dark:border-slate-600 pt-6"'
        $content = $content -replace 'class="bg-slate-50 rounded-2xl p-8"', 'class="bg-slate-50 dark:bg-slate-800 rounded-2xl p-8 transition-colors duration-300"'
        $content = $content -replace 'class="bg-white rounded-xl p-6 shadow-sm space-y-2 text-slate-700"', 'class="bg-white dark:bg-slate-700 rounded-xl p-6 shadow-sm space-y-2 text-slate-700 dark:text-slate-300 transition-colors duration-300"'
        $content = $content -replace 'class="bg-white rounded-2xl p-6 shadow-sm inline-block max-w-md"', 'class="bg-white dark:bg-slate-700 rounded-2xl p-6 shadow-sm inline-block max-w-md transition-colors duration-300"'
        $content = $content -replace 'class="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition text-center"', 'class="bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl p-5 hover:shadow-lg transition text-center"'
        
        # Fix social proof section
        $content = $content -replace 'class="py-12 px-4 bg-gradient-to-r from-purple-50 to-blue-50"', 'class="py-12 px-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-slate-800 dark:to-slate-800 transition-colors duration-300"'
        
        # Fix cross-sell cards
        $content = $content -replace 'class="text-slate-500 text-xs mb-3"', 'class="text-slate-500 dark:text-slate-400 text-xs mb-3"'
        
        # Fix purple badge
        $content = $content -replace 'class="inline-block bg-purple-100 text-purple-700 text-sm font-bold px-3 py-1 rounded-full"', 'class="inline-block bg-purple-100 dark:bg-indigo-900 text-purple-700 dark:text-indigo-400 text-sm font-bold px-3 py-1 rounded-full"'
        
        # Fix share buttons in dark mode
        $content = $content -replace 'class="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700"', 'class="bg-blue-600 dark:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"'
        $content = $content -replace 'class="bg-sky-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-sky-600"', 'class="bg-sky-500 dark:bg-sky-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-sky-600 dark:hover:bg-sky-500 transition-colors"'
        $content = $content -replace 'class="bg-green-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-600"', 'class="bg-green-500 dark:bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-600 dark:hover:bg-green-500 transition-colors"'
        
        # Fix share text color
        $content = $content -replace 'class="text-slate-600 mb-4"', 'class="text-slate-600 dark:text-slate-400 mb-4"'
    }
    
    # ---- Write back ----
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($filePath, $content, $utf8NoBom)
    
    Write-Host "  -> DONE" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Dark mode added to all pages!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
