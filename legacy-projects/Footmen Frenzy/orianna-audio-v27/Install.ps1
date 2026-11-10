param([string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps')
. 'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\Legacy-TestDelivery.ps1'
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$report=Get-Content -LiteralPath (Join-Path $root 'verification.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $report.output).Hash.ToLowerInvariant() -ne $report.sha256) {throw 'The verified 799X release changed'}
$records=@()
$records+=@(Install-LegacyTestMap -Source $report.output -MapType '799X' -MapsRoot $MapsRoot)
$release=Join-Path (Split-Path $root) '799x-backport\release'
Copy-Item -LiteralPath $report.output -Destination $release -Force
Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($report.output,'.sha256')) -Destination $release -Force
$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'delivery.json')
$records | ConvertTo-Json -Depth 5
