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
if ($hash -ne $report.sha256) { throw 'Release does not match verified checksum.' }
$records = @(Install-LegacyTestMap -Source $report.output -MapType '799X' -MapsRoot $MapsRoot)
foreach ($folder in @((Join-Path (Split-Path $PSScriptRoot) '799x-backport\release'))) {
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) { throw "Missing destination: $folder" }
    $destination = Join-Path $folder ([IO.Path]::GetFileName($report.output))
    if (Test-Path -LiteralPath $destination) {
        if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hash) { throw "A different map already occupies $destination" }
    } else {
        Copy-Item -LiteralPath $report.output -Destination $destination
    }
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hash) { throw "Installed checksum mismatch: $destination" }
    Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($report.output,'.sha256')) -Destination ([IO.Path]::ChangeExtension($destination,'.sha256')) -Force
    $records += [pscustomobject]@{ path=$destination; sha256=$hash }
}
$records | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'delivery.json')
$records

