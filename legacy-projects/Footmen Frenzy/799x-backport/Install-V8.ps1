param([string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps')
. 'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\Legacy-TestDelivery.ps1'
$ErrorActionPreference = 'Stop'
$release = Join-Path $PSScriptRoot 'release\FF799X_Rx_Orianna_v8.w3x'
$expected = (Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash
$records = @()
$records+=@(Install-LegacyTestMap -Source $release -MapType '799X' -MapsRoot $MapsRoot)
$records | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'audit\installation-v8.json')
$records | ConvertTo-Json

