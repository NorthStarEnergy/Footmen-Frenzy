param([string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps')
$repositoryRoot=$PSScriptRoot
while(-not(Test-Path -LiteralPath (Join-Path $repositoryRoot 'tools\Install-Wc3Map.ps1'))){
 $parent=Split-Path -Parent $repositoryRoot
 if(-not $parent -or $parent -eq $repositoryRoot){throw 'Cannot locate repository installer'}
 $repositoryRoot=$parent
}
. (Join-Path $repositoryRoot 'tools\Legacy-TestDelivery.ps1')
$ErrorActionPreference = 'Stop'
$report = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'verification.json') -Raw | ConvertFrom-Json
$hash = (Get-FileHash -LiteralPath $report.output -Algorithm SHA256).Hash.ToLowerInvariant()
if ($hash -ne $report.sha256) { throw 'Verified map checksum does not match.' }
$records = @()
$records+=@(Install-LegacyTestMap -Source $report.output -MapType '799X' -MapsRoot $MapsRoot)
$release = Join-Path (Split-Path $PSScriptRoot) '799x-backport\release'
Copy-Item -LiteralPath $report.output -Destination $release -Force
Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($report.output,'.sha256')) -Destination $release -Force
$records | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'delivery.json')
$records

