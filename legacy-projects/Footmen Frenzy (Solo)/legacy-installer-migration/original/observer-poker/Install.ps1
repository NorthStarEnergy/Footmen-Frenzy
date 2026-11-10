$ErrorActionPreference='Stop'
$release=Join-Path $PSScriptRoot 'release\FF799X_Observer_Poker_v2.w3x'
$expected=(Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash
$results=@()
foreach ($directory in @('C:\Users\User\Documents\Warcraft III\Maps\Test','C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test','C:\Users\User\Documents\Warcraft III\Maps\Observer Poker','C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Observer Poker')) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
    $target=Join-Path $directory 'FF799X_Observer_Poker_v2.w3x'
    Copy-Item -LiteralPath $release -Destination $target
    $actual=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
    if ($actual -ne $expected) {throw "Installed hash mismatch: $target"}
    $results+=@{path=$target;sha256=$actual.ToLower();verified=$true}
}
$results | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'delivery.json')
$results | ForEach-Object { [pscustomobject]$_ } | Format-Table path,verified
