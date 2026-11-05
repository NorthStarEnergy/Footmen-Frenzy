[CmdletBinding(SupportsShouldProcess)]
param(
 [Parameter(Mandatory)][ValidateScript({Test-Path -LiteralPath $_ -PathType Leaf})][string]$Source,
 [Parameter(Mandatory)][ValidateSet('Foots','Tests','Main')][string]$Channel,
 [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9][A-Za-z0-9 _-]*$')][string]$MapType,
 [string]$MapsRoot=(Join-Path $env:USERPROFILE 'Documents\Warcraft III\Maps')
)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath($MapsRoot)
$sourcePath=(Resolve-Path -LiteralPath $Source).Path
if([IO.Path]::GetExtension($sourcePath) -notin @('.w3x','.w3m')){throw 'Source must be a Warcraft map'}
$destination=[IO.Path]::GetFullPath((Join-Path $root $(if($Channel -eq 'Main'){$MapType}else{"$Channel\$MapType"})))
$archive=if($Channel -eq 'Tests'){Join-Path $destination 'Test Archives'}elseif($Channel -eq 'Main'){Join-Path $root "Archive\$MapType"}else{Join-Path $root "Archive\Foots\$MapType"}
$installerPath=$PSCommandPath
function Sync-MainMap {
 if($Channel -eq 'Main'){return}
 $mainDirectory=Join-Path $root $MapType
 $newest=Get-ChildItem -LiteralPath $mainDirectory -File -ErrorAction SilentlyContinue|Where-Object Extension -in @('.w3x','.w3m')|Sort-Object LastWriteTimeUtc -Descending|Select-Object -First 1
 if($Channel -eq 'Tests' -or -not $newest -or (Get-Item -LiteralPath $sourcePath).LastWriteTimeUtc -ge $newest.LastWriteTimeUtc){
  & $installerPath -Source $sourcePath -Channel Main -MapType $MapType -MapsRoot $root -WhatIf:$WhatIfPreference
 }
}
foreach($p in @($destination,$archive)){if(-not ([IO.Path]::GetFullPath($p)).StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Invalid destination'}}
$target=Join-Path $destination ([IO.Path]::GetFileName($sourcePath))
$sourceHash=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
if((Test-Path -LiteralPath $target) -and (Get-FileHash -LiteralPath $target).Hash -eq $sourceHash){
 $extras=@(Get-ChildItem -LiteralPath $destination -File|Where-Object { $_.Extension -in @('.w3x','.w3m') -and $_.FullName -ne $target })
 if($extras.Count -and $PSCmdlet.ShouldProcess($destination,'Archive extra active maps; keep the selected current map')){
  $history=Join-Path $archive ((Get-Date -Format 'yyyy-MM-dd_HHmmss')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8))
  New-Item -ItemType Directory -Force -Path $history|Out-Null
  foreach($file in $extras){Move-Item -LiteralPath $file.FullName -Destination (Join-Path $history $file.Name)}
 }
 Write-Output "Already installed: $target";Sync-MainMap;return
}
if(-not $PSCmdlet.ShouldProcess($target,'Install map and archive previous active versions')){return}
New-Item -ItemType Directory -Force -Path $destination|Out-Null
New-Item -ItemType Directory -Force -Path $archive|Out-Null
# Stage outside Maps so an incomplete copy cannot be scanned by Warcraft.
$stageDir=Join-Path (Split-Path -Parent $root) 'Map Install Staging'
New-Item -ItemType Directory -Force -Path $stageDir|Out-Null
$stage=Join-Path $stageDir ([guid]::NewGuid().ToString()+'.pending')
Copy-Item -LiteralPath $sourcePath -Destination $stage
if((Get-FileHash -LiteralPath $stage).Hash -ne $sourceHash){throw 'Staging checksum mismatch; existing maps untouched'}
$existing=@(Get-ChildItem -LiteralPath $destination -File|Where-Object Extension -in @('.w3x','.w3m'))
$history=Join-Path $archive ((Get-Date -Format 'yyyy-MM-dd_HHmmss')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8))
if($existing.Count){New-Item -ItemType Directory -Force -Path $history|Out-Null}
foreach($file in $existing){
 $resolved=[IO.Path]::GetFullPath($file.FullName)
 if(-not $resolved.StartsWith($destination+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Archive source outside selected map type'}
 Move-Item -LiteralPath $resolved -Destination (Join-Path $history $file.Name)
}
Move-Item -LiteralPath $stage -Destination $target
if((Get-FileHash -LiteralPath $target).Hash -ne $sourceHash){throw 'Installed checksum mismatch'}
[pscustomobject]@{Installed=$target;SHA256=$sourceHash;PreviousVersionsArchived=$existing.Count;Archive=$history}
Sync-MainMap
