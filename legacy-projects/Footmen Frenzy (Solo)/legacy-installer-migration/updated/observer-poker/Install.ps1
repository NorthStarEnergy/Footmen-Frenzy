param([string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps')
. 'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\Legacy-TestDelivery.ps1'
$ErrorActionPreference='Stop'
$release=Join-Path $PSScriptRoot 'release\FF799X_Observer_Poker_v2.w3x'
$expected=(Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash
$results=@()
$results+=@(Install-LegacyTestMap -Source $release -MapType '799X' -MapsRoot $MapsRoot)
$results | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'delivery.json')
$results | ForEach-Object { [pscustomobject]$_ } | Format-Table path,verified
