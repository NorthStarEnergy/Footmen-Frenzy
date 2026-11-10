param([string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps')
. 'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\Legacy-TestDelivery.ps1'
$ErrorActionPreference='Stop'
$project=$PSScriptRoot
$release=Join-Path $project 'release\Solo Foots 6 Player FFA v1.w3x'
$expected=(Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash
$results=@()
$results+=@(Install-LegacyTestMap -Source $release -MapType 'FFA Foots' -MapsRoot $MapsRoot)
$results | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $project 'delivery.json')
$results | Format-Table path,verified
