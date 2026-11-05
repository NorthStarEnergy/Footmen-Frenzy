param([string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps')
$repositoryRoot=$PSScriptRoot
while(-not(Test-Path -LiteralPath (Join-Path $repositoryRoot 'tools\Install-Wc3Map.ps1'))){
 $parent=Split-Path -Parent $repositoryRoot
 if(-not $parent -or $parent -eq $repositoryRoot){throw 'Cannot locate repository installer'}
 $repositoryRoot=$parent
}
. (Join-Path $repositoryRoot 'tools\Legacy-TestDelivery.ps1')
$ErrorActionPreference='Stop'
$project=$PSScriptRoot
$release=Join-Path $project 'release\Solo Foots 6 Player FFA v1.w3x'
$expected=(Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash
$results=@()
$results+=@(Install-LegacyTestMap -Source $release -MapType 'FFA Foots' -MapsRoot $MapsRoot)
$results | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $project 'delivery.json')
$results | Format-Table path,verified

