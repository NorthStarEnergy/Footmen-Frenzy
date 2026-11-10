$ErrorActionPreference = 'Stop'
$release = Join-Path $PSScriptRoot 'release\FF799X_Rx_Orianna_v9.w3x'
$expected = (Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash
$roots = @(
    'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test',
    'C:\Users\User\Documents\Warcraft III\Maps\Test'
)
$records = @()
foreach ($root in $roots) {
    $resolved = (Resolve-Path -LiteralPath $root).Path
    if ($resolved -ne $root) { throw "Unexpected destination: $resolved" }
    $archive = Join-Path $resolved 'Archive'
    New-Item -ItemType Directory -Path $archive -Force | Out-Null
    $pending = Join-Path $resolved 'FF799X_Rx_Orianna_v9.pending'
    $destination = Join-Path $resolved 'FF799X_Rx_Orianna_v9.w3x'
    Copy-Item -LiteralPath $release -Destination $pending
    if ((Get-FileHash -LiteralPath $pending -Algorithm SHA256).Hash -ne $expected) { throw 'Copy hash mismatch' }
    $locked = @()
    foreach ($map in Get-ChildItem -LiteralPath $resolved -File | Where-Object { $_.Extension -in @('.w3x', '.w3m') }) {
        if ($map.DirectoryName -ne $resolved) { throw "Map escaped Test: $($map.FullName)" }
        $archived = [IO.Path]::GetFullPath((Join-Path $archive $map.Name))
        if (-not $archived.StartsWith($archive + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Archive path escaped Test' }
        if (Test-Path -LiteralPath $archived) {
            $archived = Join-Path $archive ($map.BaseName + '-' + [guid]::NewGuid().ToString('N') + $map.Extension)
        }
        try {
            Move-Item -LiteralPath $map.FullName -Destination $archived -ErrorAction Stop
        } catch {
            if ($_.Exception.Message -notlike '*being used by another process*') { throw }
            $locked += $map.FullName
        }
    }
    Move-Item -LiteralPath $pending -Destination $destination
    $maps = @(Get-ChildItem -LiteralPath $resolved -File | Where-Object { $_.Extension -in @('.w3x', '.w3m') })
    $exclusive = $maps.Count -eq 1 -and $maps[0].Name -eq 'FF799X_Rx_Orianna_v9.w3x'
    $actual = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if ($actual -ne $expected) { throw 'Installed hash mismatch' }
    $records += @{path=$destination;sha256=$actual.ToLower();onlyMapInTest=$exclusive;lockedMapsAwaitingArchive=$locked}
}
$records | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'audit\installation-v9.json')
$records | ConvertTo-Json

