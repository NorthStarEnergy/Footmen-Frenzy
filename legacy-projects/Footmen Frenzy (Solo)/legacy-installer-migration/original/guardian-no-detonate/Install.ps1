$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$report=Get-Content -LiteralPath (Join-Path $root 'verification.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $report.output).Hash.ToLowerInvariant() -ne $report.sha256) {throw 'The verified 799X release changed'}
$records=@()
foreach ($maps in @('C:\Users\User\Documents\Warcraft III\Maps','C:\Users\User\OneDrive\Documents\Warcraft III\Maps')) {
 $active=Join-Path $maps 'Test'
 $archive=Join-Path $maps 'Test Archive'
 New-Item -ItemType Directory -Force $active,$archive | Out-Null
 $old=Join-Path $active 'FF799X_Rx_OriannaAudio_v27.w3x'
 if (Test-Path -LiteralPath $old) {
  $from=[IO.Path]::GetFullPath($old)
  $to=[IO.Path]::GetFullPath((Join-Path $archive ('FF799X_Rx_OriannaAudio_v27 - before Guardian update '+[guid]::NewGuid().ToString('N')+'.w3x')))
  $prefix=[IO.Path]::GetFullPath($maps).TrimEnd('\')+'\'
  if (-not $from.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -or -not $to.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) {throw 'Archive path escaped Maps'}
  Move-Item -LiteralPath $from -Destination $to
 }
 $dest=Join-Path $active ([IO.Path]::GetFileName($report.output))
 Copy-Item -LiteralPath $report.output -Destination $dest -Force
 $hash=(Get-FileHash -LiteralPath $dest).Hash.ToLowerInvariant()
 if ($hash -ne $report.sha256) {throw 'Installed map checksum mismatch'}
 $records+=@{path=$dest;sha256=$hash;verified=$true}
}
$release=Join-Path (Split-Path $root) '799x-backport\release'
Copy-Item -LiteralPath $report.output -Destination $release -Force
Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($report.output,'.sha256')) -Destination $release -Force
$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'delivery.json')
$records | ConvertTo-Json -Depth 5

