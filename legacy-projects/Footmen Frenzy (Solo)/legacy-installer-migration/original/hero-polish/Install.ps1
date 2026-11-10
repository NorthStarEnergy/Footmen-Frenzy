$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$workspace=Split-Path $root
$records=@()
$plans=@(
 @{variant='799x';folder='Test';old='FF799X_Rx_WC3Icons_v25.w3x';project='799x-backport'},
 @{variant='mini';folder='Mini Foots';old='Mini Foots v9.w3x';project='mini-foots'},
 @{variant='solo';folder='Foots FFA';old='Solo Foots 6 Player FFA v2.w3x';project='six-player-ffa'}
)
function Archive-Map($file,$archive,$boundary) {
 $from=[IO.Path]::GetFullPath($file.FullName)
 $to=[IO.Path]::GetFullPath((Join-Path $archive ($file.BaseName+' - before hero polish '+[guid]::NewGuid().ToString('N')+'.w3x')))
 $prefix=[IO.Path]::GetFullPath($boundary).TrimEnd('\')+'\'
 if (-not $from.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -or -not $to.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) {throw 'Archive target escaped named directory'}
 New-Item -ItemType Directory -Force $archive | Out-Null
 Move-Item -LiteralPath $from -Destination $to
}
foreach ($plan in $plans) {
 $report=Get-Content -LiteralPath (Join-Path $root ($plan.variant+'\verification.json')) -Raw | ConvertFrom-Json
 if (-not $report.passed) {throw 'Validation failed'}
 $source=$report.output
 if ((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $report.sha256) {throw 'Release changed after validation'}
 foreach ($maps in @('C:\Users\User\Documents\Warcraft III\Maps','C:\Users\User\OneDrive\Documents\Warcraft III\Maps')) {
  $active=Join-Path $maps $plan.folder
  $archive=Join-Path $maps ($plan.folder+' Archive')
  New-Item -ItemType Directory -Force $active | Out-Null
  $dest=Join-Path $active ([IO.Path]::GetFileName($source))
  $filter=if ($plan.variant -eq 'mini') {'*.w3x'} else {$plan.old}
  foreach ($file in Get-ChildItem -LiteralPath $active -File -Filter $filter) {
   if ($file.FullName -ne $dest) {Archive-Map $file $archive $maps}
  }
  Copy-Item -LiteralPath $source -Destination $dest -Force
  $hash=(Get-FileHash -LiteralPath $dest).Hash.ToLowerInvariant()
  if ($hash -ne $report.sha256) {throw 'Installation checksum failed'}
  $records+=@{path=$dest;sha256=$hash;verified=$true}
 }
 $project=Join-Path $workspace $plan.project
 $release=Join-Path $project 'release'
 if ($plan.variant -eq 'mini') {
  foreach ($file in Get-ChildItem -LiteralPath $release -File -Filter '*.w3x') {
   if ($file.Name -ne [IO.Path]::GetFileName($source)) {Archive-Map $file (Join-Path $project 'archive') $project}
  }
 }
 Copy-Item -LiteralPath $source -Destination $release -Force
 Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($source,'.sha256')) -Destination $release -Force
}
$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'delivery.json')
$records | ConvertTo-Json -Depth 5
