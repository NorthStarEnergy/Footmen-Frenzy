param([string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps')
. 'C:\Users\User\Documents\ChatGPT\Footmen Frenzy (Solo)\legacy-installer-migration\Legacy-TestDelivery.ps1'
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$workspace=Split-Path $root
$records=@()
$plans=@(
 @{variant='799x';folder='799X';old='FF799X_Rx_WC3Icons_v25.w3x';project='799x-backport'},
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
 $family=if($plan.variant -eq 'mini'){'Mini Foots'}elseif($plan.variant -eq 'solo'){'FFA Foots'}else{'799X'}
 $records+=@(Install-LegacyTestMap -Source $source -MapType $family -MapsRoot $MapsRoot)
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
