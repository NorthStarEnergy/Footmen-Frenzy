$ErrorActionPreference = 'Stop'
$report = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'verification.json') -Raw | ConvertFrom-Json
$hash = (Get-FileHash -LiteralPath $report.output -Algorithm SHA256).Hash.ToLowerInvariant()
if ($hash -ne $report.sha256) { throw 'Verified map checksum does not match.' }
$records = @()
foreach ($maps in @('C:\Users\User\Documents\Warcraft III\Maps\Test', 'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')) {
    New-Item -ItemType Directory -Force -Path $maps | Out-Null
    $dest = Join-Path $maps ([IO.Path]::GetFileName($report.output))
    Copy-Item -LiteralPath $report.output -Destination $dest -Force
    if ((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hash) { throw 'Installed map checksum does not match.' }
    $records += $dest
}
$release = Join-Path (Split-Path $PSScriptRoot) '799x-backport\release'
Copy-Item -LiteralPath $report.output -Destination $release -Force
Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($report.output,'.sha256')) -Destination $release -Force
$records | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'delivery.json')
$records
