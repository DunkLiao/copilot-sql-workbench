$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$htmlFiles = Get-ChildItem -LiteralPath $root -Filter '*.html' -File
$requiredTokens = @(
  '--theme-page', '--theme-surface', '--theme-surface-alt', '--theme-text',
  '--theme-muted', '--theme-border', '--theme-primary', '--theme-success',
  '--theme-warning', '--theme-danger', '--theme-info'
)

$themePath = Join-Path $root 'theme.css'
if (-not (Test-Path -LiteralPath $themePath)) {
  throw 'theme.css is missing'
}

$themeScriptPath = Join-Path $root 'theme.js'
if (-not (Test-Path -LiteralPath $themeScriptPath)) {
  throw 'theme.js is missing'
}

$theme = Get-Content -Raw -Encoding UTF8 $themePath
foreach ($token in $requiredTokens) {
  if ($theme -notmatch [regex]::Escape($token)) {
    throw "Missing theme token: $token"
  }
}

foreach ($file in $htmlFiles) {
  $content = Get-Content -Raw -Encoding UTF8 $file.FullName
  if ($content -match '\u83AB\u862D\u8FEA|\u96E2\u7DDA\u6A21\u5F0F|\u96E2\u7DDA\u7248|offline mode') {
    throw "$($file.Name) still contains removed theme or offline copy"
  }
  if ($content -notmatch '<link[^>]+href=["'']theme\.css["'']') {
    throw "$($file.Name) does not reference theme.css"
  }
  if ($content -notmatch '<button[^>]+id=["'']themeToggle["'']') {
    throw "$($file.Name) is missing themeToggle"
  }
  if ($content -notmatch '<script[^>]+src=["'']theme\.js["'']') {
    throw "$($file.Name) does not reference theme.js"
  }
  $headEnd = $content.IndexOf('</head>')
  if ($headEnd -lt 0) {
    throw "$($file.Name) is missing </head>"
  }
  $head = $content.Substring(0, $headEnd)
  if ($head -notmatch '<script[^>]+src=["'']theme\.js["'']') {
    throw "$($file.Name) must load theme.js in <head> so the saved theme applies before first paint"
  }
}

$catalog = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'sql-spa-tools-catalog.html')
if ($catalog -notmatch "style-src 'self' 'unsafe-inline'") {
  throw 'Catalog CSP does not allow theme.css'
}

$pii = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'sql-spa-tools-pii-cleaner.html')
if ($pii -notmatch "style-src 'self' 'unsafe-inline'") {
  throw 'PII Cleaner CSP does not allow theme.css'
}

$formatter = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'sql-spa-tools-oracle-formatter.html')
if ($formatter -notmatch 'background:#f4f4f4' -or $formatter -notmatch 'border:1px solid #d1d1d1') {
  throw 'Formatter report does not use theme colors'
}

$compare = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'sql-spa-tools-sql-compare.html')
if ($compare -notmatch 'background:#f4f4f4' -or $compare -notmatch 'border:1px solid #d1d1d1') {
  throw 'SQL Compare report does not use theme colors'
}

if ($catalog -notmatch 'background:#f4f4f4' -or $catalog -notmatch 'color:#616161') {
  throw 'Catalog report does not use theme colors'
}

if ($theme -notmatch 'header button:disabled' -or $theme -notmatch 'header button:disabled\s*\{[^}]*opacity:\s*1' -or $theme -notmatch 'header button:disabled\s*\{[^}]*color:\s*var\(--theme-muted\)') {
  throw 'Header disabled button contrast contract missing'
}

if ($theme -notmatch ':root\[data-theme=''dark''\]' -or $theme -notmatch '--theme-page:\s*#f6f6f6' -or $theme -notmatch '--theme-primary:\s*#444444' -or $theme -notmatch '--theme-page:\s*#202020') {
  throw 'Light theme is not the default'
}

if ($theme -notmatch '--m-id:\s*#3d3d3d' -or $theme -notmatch '--m-ban:\s*#565656') {
  throw 'Dark-mode highlight tokens are missing'
}

$themeScript = Get-Content -Raw -Encoding UTF8 $themeScriptPath
if ($themeScript -notmatch 'sql_spa_tools_theme' -or $themeScript -notmatch "=== 'dark'") {
  throw 'Theme persistence contract missing'
}

Write-Output "Theme contract passed: $($htmlFiles.Count) HTML pages, $($requiredTokens.Count) tokens"
