$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$toolPages = @(
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

foreach ($page in $toolPages) {
  $path = Join-Path $root $page
  $html = Get-Content -Raw -Encoding UTF8 $path
  if ($html -notmatch '<a[^>]+class=["'']home-link["''][^>]+href=["'']index\.html["'']') {
    throw "$page is missing a home link"
  }
}

$theme = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'theme.css')
if ($theme -notmatch '\.home-link\s*\{' -or $theme -notmatch 'home-link[^}]*position:\s*fixed') {
  throw 'theme.css is missing home-link styling'
}

$themeDocs = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'docs\THEME.md')
$namingDocs = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'docs\NAMING.md')
if ($themeDocs -notmatch 'home-link' -or $themeDocs -notmatch 'index\.html') {
  throw 'THEME.md is missing home navigation guidance'
}
if ($namingDocs -notmatch 'index\.html') {
  throw 'NAMING.md is missing index guidance'
}

Write-Output "Home link contract passed: $($toolPages.Count) tool pages"
