$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$workspace=Split-Path $root
$destinations=@('C:\Users\User\Documents\Warcraft III\Maps','C:\Users\User\OneDrive\Documents\Warcraft III\Maps')
$records=@()
foreach ($maps in $destinations) {
 foreach ($variant in @('mini','solo')) {
  $report=Get-Content -LiteralPath (Join-Path $root "$variant\verification.json") -Raw | ConvertFrom-Json
  $source=$report.output
  if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $report.sha256) {throw 'Verified release changed'}
  $folder=if ($variant -eq 'mini') {'Mini Foots'} else {'Foots FFA'}
  $active=Join-Path $maps $folder
  $archive=Join-Path $maps ($folder+' Archive')
  New-Item -ItemType Directory -Path $active,$archive -Force | Out-Null
  $destination=Join-Path $active ([IO.Path]::GetFileName($source))
  if ($variant -eq 'mini') {$old=Get-ChildItem -LiteralPath $active -Filter '*.w3x' -File}
  else {$old=Get-ChildItem -LiteralPath $active -Filter 'Solo Foots 6 Player FFA v1.w3x' -File}
  foreach ($file in $old) {
   if ($file.FullName -eq $destination) {continue}
   # Resolve every move endpoint and keep it within this explicitly named Maps directory.
   $from=[IO.Path]::GetFullPath($file.FullName)
   $to=[IO.Path]::GetFullPath((Join-Path $archive ($file.BaseName+' - before hero sync '+[guid]::NewGuid().ToString('N')+'.w3x')))
   $prefix=[IO.Path]::GetFullPath($maps).TrimEnd('\')+'\'
   if (-not $from.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -or -not $to.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) {throw 'Archive path escaped Maps'}
   Move-Item -LiteralPath $from -Destination $to
  }
  Copy-Item -LiteralPath $source -Destination $destination -Force
  $hash=(Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($hash -ne $report.sha256) {throw 'Installed hash mismatch'}
  $records+=@{path=$destination;sha256=$hash;verified=$true}
 }
}
# Keep the established Mini release directory current; preserve each older map in its archive.
$release=Join-Path $workspace 'mini-foots\release'
$archive=Join-Path $workspace 'mini-foots\archive'
New-Item -ItemType Directory -Force $archive | Out-Null
foreach ($file in Get-ChildItem -LiteralPath $release -Filter '*.w3x' -File) {
 if ($file.Name -eq 'Mini Foots v9.w3x') {continue}
 $from=[IO.Path]::GetFullPath($file.FullName)
 $to=[IO.Path]::GetFullPath((Join-Path $archive ($file.BaseName+' - before hero sync '+[guid]::NewGuid().ToString('N')+'.w3x')))
 $prefix=[IO.Path]::GetFullPath((Join-Path $workspace 'mini-foots')).TrimEnd('\')+'\'
 if (-not $from.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -or -not $to.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) {throw 'Release archive path escaped workspace'}
 Move-Item -LiteralPath $from -Destination $to
}
Copy-Item -LiteralPath (Join-Path $root 'release\Mini Foots v9.w3x') -Destination $release -Force
Copy-Item -LiteralPath (Join-Path $root 'release\Mini Foots v9.sha256') -Destination $release -Force
Copy-Item -LiteralPath (Join-Path $root 'release\Solo Foots 6 Player FFA v2.w3x') -Destination (Join-Path $workspace 'six-player-ffa\release') -Force
Copy-Item -LiteralPath (Join-Path $root 'release\Solo Foots 6 Player FFA v2.sha256') -Destination (Join-Path $workspace 'six-player-ffa\release') -Force
$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'delivery.json')
$records | ConvertTo-Json -Depth 5
