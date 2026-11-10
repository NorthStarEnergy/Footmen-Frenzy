$ErrorActionPreference='Stop'
$project=$PSScriptRoot
$release=Join-Path $project 'release\Solo Foots 6 Player FFA v1.w3x'
$expected=(Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash
$destinations=@(
 'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Foots FFA',
 'C:\Users\User\Documents\Warcraft III\Maps\Foots FFA',
 'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test',
 'C:\Users\User\Documents\Warcraft III\Maps\Test'
)
$results=@()
foreach ($directory in $destinations) {
 New-Item -ItemType Directory -Force -Path $directory | Out-Null
 $target=Join-Path $directory (Split-Path $release -Leaf)
 Copy-Item -LiteralPath $release -Destination $target
 $actual=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
 if ($actual -ne $expected) { throw "Installed hash mismatch: $target" }
 $results+=@{path=$target;sha256=$actual.ToLower();verified=$true}
}
$results | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $project 'delivery.json')
$results | Format-Table path,verified
