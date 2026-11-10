[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^SF_Test1\.7_v\d+$')]
    [string]$Version,

    [string]$BaseMap,
    [string]$SourceScript,
    [string]$DeliveryRoot = 'C:\Users\Ryan1\Documents\Warcraft III\Maps\Solo Foots\GPT',
    [switch]$Deliver,

    # pjass is the authoritative gate: it is the same compiler Warcraft III uses,
    # so it resolves symbols and types instead of only checking grammar.
    [string]$Pjass = 'C:\Program Files\Warcraft III\_retail_\x86_64\JassHelper\pjass.exe',
    [string]$CommonJ = 'C:\Users\Ryan1\Documents\Warcraft III\JassHelper\common.j',
    [string]$BlizzardJ = 'C:\Users\Ryan1\Documents\Warcraft III\JassHelper\Blizzard.j'
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($BaseMap)) {
    $BaseMap = Join-Path $projectRoot 'releases\SoloFootsv1.7-Performance-Test-6.w3x'
}
if ([string]::IsNullOrWhiteSpace($SourceScript)) {
    $SourceScript = Join-Path $projectRoot 'src\war3map.j'
}

$parser = Join-Path $PSScriptRoot 'bin\JassParseCheck\JassParseCheck.exe'
$packer = Join-Path $PSScriptRoot 'MpqAdd\bin\Debug\net8.0\MpqAdd.exe'
$extractor = Join-Path $PSScriptRoot 'bin\MpqExtract\MpqExtract.exe'
$releaseMap = Join-Path $projectRoot ("releases\{0}.w3x" -f $Version)
$roundTripRoot = Join-Path $projectRoot ("roundtrip\{0}" -f $Version)
$roundTripScript = Join-Path $roundTripRoot 'files\war3map.j'

foreach ($requiredPath in @($BaseMap, $SourceScript, $parser, $packer, $extractor, $Pjass, $CommonJ, $BlizzardJ)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file not found: $requiredPath"
    }
}
if (Test-Path -LiteralPath $releaseMap) {
    throw "Release already exists: $releaseMap"
}
if (Test-Path -LiteralPath $roundTripRoot) {
    throw "Round-trip folder already exists: $roundTripRoot"
}

Write-Host "[1/4] Compiling JASS source with pjass"
& $Pjass $CommonJ $BlizzardJ $SourceScript
if ($LASTEXITCODE -ne 0) {
    throw "pjass rejected $SourceScript (exit code $LASTEXITCODE). Warcraft III will refuse this script and the lobby will never load. Fix the errors above before building."
}

# Informational only. JassParseCheck is a grammar-only parser: it reports OK on
# forward references, duplicate symbols, undeclared names and type errors, which
# is how v43 shipped unhostable. Kept for its declaration count, never as a gate.
& $parser $SourceScript
if ($LASTEXITCODE -ne 0) {
    Write-Warning "JassParseCheck failed while pjass passed - the script may be structurally odd. Investigate before shipping."
}

Write-Host "[2/4] Packing $Version"
$stageMap = Join-Path ([System.IO.Path]::GetTempPath()) ("{0}-{1}-stage.w3x" -f $Version, [guid]::NewGuid().ToString('N'))
try {
    # MpqAdd replacement must be two-stage: --replace removes the old entry,
    # then the normal add path inserts the new script into the compact archive.
    & $packer --replace $BaseMap $SourceScript 'war3map.j' $stageMap
    if ($LASTEXITCODE -ne 0) {
        throw "Map packer remove stage failed with exit code $LASTEXITCODE"
    }
    & $packer $stageMap $SourceScript 'war3map.j' $releaseMap
    if ($LASTEXITCODE -ne 0) {
        throw "Map packer add stage failed with exit code $LASTEXITCODE"
    }
    & $packer --verify $releaseMap 'war3map.j' $SourceScript
    if ($LASTEXITCODE -ne 0) {
        throw "Packed script verification failed with exit code $LASTEXITCODE"
    }
}
finally {
    if (Test-Path -LiteralPath $stageMap -PathType Leaf) {
        Remove-Item -LiteralPath $stageMap -Force
    }
}

Write-Host "[3/4] Extracting the packed script"
& $extractor $releaseMap $roundTripRoot
$extractExitCode = $LASTEXITCODE
if (-not (Test-Path -LiteralPath $roundTripScript -PathType Leaf)) {
    throw "Round-trip extraction did not produce war3map.j (extractor exit code $extractExitCode)"
}

$sourceHash = (Get-FileHash -LiteralPath $SourceScript -Algorithm SHA256).Hash.ToLowerInvariant()
$roundTripHash = (Get-FileHash -LiteralPath $roundTripScript -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceHash -ne $roundTripHash) {
    throw "Round-trip hash mismatch. Source: $sourceHash; packed: $roundTripHash"
}

Write-Host "[4/4] Round-trip SHA256 verified: $sourceHash"

$deliveredMap = $null
if ($Deliver) {
    $deliveryFolder = Join-Path $DeliveryRoot $Version
    if (Test-Path -LiteralPath $deliveryFolder) {
        throw "Delivery folder already exists: $deliveryFolder"
    }
    New-Item -ItemType Directory -Path $deliveryFolder | Out-Null
    $deliveredMap = Join-Path $deliveryFolder ("{0}.w3x" -f $Version)
    Copy-Item -LiteralPath $releaseMap -Destination $deliveredMap
    Write-Host "Delivered: $deliveredMap"

    $archiveFolder = Join-Path $DeliveryRoot 'Archive'
    New-Item -ItemType Directory -Path $archiveFolder -Force | Out-Null
    $olderDeliveryFolders = @(Get-ChildItem -LiteralPath $DeliveryRoot -Directory -Force | Where-Object {
        $_.FullName -ne $deliveryFolder -and $_.FullName -ne $archiveFolder
    })
    foreach ($olderFolder in $olderDeliveryFolders) {
        $archiveDestination = Join-Path $archiveFolder $olderFolder.Name
        if (Test-Path -LiteralPath $archiveDestination) {
            throw "Archive destination already exists: $archiveDestination"
        }
        Move-Item -LiteralPath $olderFolder.FullName -Destination $archiveFolder
    }
    Write-Host ("Archived {0} older delivery folder(s)" -f $olderDeliveryFolders.Count)
}

[pscustomobject]@{
    Version = $Version
    Parser = 'pjass OK'
    ReleaseMap = $releaseMap
    RoundTripScript = $roundTripScript
    SHA256 = $sourceHash
    ExtractorExitCode = $extractExitCode
    DeliveredMap = $deliveredMap
}
