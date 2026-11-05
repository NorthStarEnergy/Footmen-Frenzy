# Shared delivery for historical installers. Keep validation at each call site.
function Install-LegacyTestMap {
 param([Parameter(Mandatory)][string]$Source,[Parameter(Mandatory)][string]$MapType,[string]$MapsRoot)
 & (Join-Path $PSScriptRoot 'Install-Wc3Map.ps1') -Source $Source -MapType $MapType -Channel Tests -MapsRoot $MapsRoot | Out-Null
 $expected=(Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
 foreach($folder in @((Join-Path $MapsRoot "Tests\$MapType"),(Join-Path $MapsRoot $MapType))){
  $active=@(Get-ChildItem -LiteralPath $folder -File|Where-Object Extension -in @('.w3x','.w3m'))
  $path=Join-Path $folder ([IO.Path]::GetFileName($Source))
  if($active.Count -ne 1 -or $active[0].FullName -ne $path -or (Get-FileHash -LiteralPath $path).Hash -ne $expected){throw "Installation verification failed: $folder"}
  [pscustomobject]@{path=$path;sha256=$expected.ToLowerInvariant();verified=$true;onlyMapInTest=$true}
 }
}
