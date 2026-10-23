$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$path = Join-Path $root 'index.html'
if (-not (Test-Path -LiteralPath $path)) {
  throw 'index.html is missing'
}

$html = Get-Content -Raw -Encoding UTF8 $path
if ($html -notmatch '<title>SQL SPA Tools[^<]+</title>') {
  throw 'index.html title is invalid'
}
if ($html -notmatch '<h1[^>]*>SQL SPA Tools[^<]+</h1>') {
  throw 'index.html heading is invalid'
}
if ($html -notmatch '<link[^>]+href=["'']theme\.css["'']' -or $html -notmatch '<script[^>]+src=["'']theme\.js["'']') {
  throw 'index.html theme references are missing'
}
if ($html -notmatch '<button[^>]+id=["'']themeToggle["'']') {
  throw 'index.html themeToggle is missing'
}

$targets = @(
  'sql-spa-tools-oracle-formatter.html',
  'sql-spa-tools-sql-compare.html',
  'sql-spa-tools-pii-cleaner.html',
  'sql-spa-tools-catalog.html',
  'sql-spa-tools-column-lineage.html',
  'sql-spa-tools-sqlscriptmanage.html',
  'sql-spa-tools-excel-csv-sql.html',
  'sql-spa-tools-excel-csv-sql-cte.html',
  'sql-spa-tools-sql-lab.html',
  'sql-spa-tools-data-quality-audit-center.html',
  'sql-spa-tools-data-relationship-explorer.html',
  'sql-spa-tools-schema-studio.html'
)
foreach ($target in $targets) {
  if ($html -notmatch ('href=["'']' + [regex]::Escape($target) + '["'']')) {
    throw "index.html is missing link: $target"
  }
}

if (($html | Select-String -Pattern 'class=["'']tool-card["'']' -AllMatches).Matches.Count -ne 12) {
  throw 'index.html must contain twelve tool cards'
}

Write-Output 'Index contract passed: title, theme, toggle, twelve tool links'
