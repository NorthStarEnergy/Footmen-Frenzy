$ErrorActionPreference='Stop'
$project=$PSScriptRoot
$python=Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python (Join-Path $project 'check_runtime.py')
if ($LASTEXITCODE -ne 0) {throw 'Orianna runtime checks failed'}
& $python (Join-Path $project 'check_debug_heroes.py')
if ($LASTEXITCODE -ne 0) {throw 'Debug recruitment checks failed'}
& $python (Join-Path $project 'check_gragus.py')
if ($LASTEXITCODE -ne 0) {throw 'Gragus checks failed'}
$jass=Join-Path $env:USERPROFILE 'Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Documents\Warcraft III\JassHelper'
& (Join-Path $env:USERPROFILE 'Documents\Codex\2026-10-28\thi\work\jasshelper\pjass.exe') (Join-Path $jass 'common.j') (Join-Path $jass 'Blizzard.j') (Join-Path $project 'src\war3map.j')
if ($LASTEXITCODE -ne 0) {throw 'JASS compile check failed'}
$dotnet=Join-Path $project '..\mini-foots\tools\dotnet\dotnet.exe'
$packer='C:\Users\User\Documents\ChatGPT\Footmen Frenzy (Solo)\tools\MpqAdd\bin\Debug\net8.0\MpqAdd.dll'
$extractor='C:\Users\User\Documents\ChatGPT\Footmen Frenzy (Solo)\tools\bin\MpqExtract\MpqExtract.dll'
$env:DOTNET_ROLL_FORWARD='Major'
$stage=Join-Path $project ('build-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory $stage | Out-Null
$current='C:\Users\User\Documents\Warcraft III\Maps\Test\Archive\FF799X_Rx_HeroTavern_v1.w3x'
$i=0
$existing=Get-Content (Join-Path $project 'base-payloads.json') -Raw | ConvertFrom-Json
foreach ($file in Get-ChildItem (Join-Path $project 'src') -File -Recurse) {
 $internalName=[System.IO.Path]::GetRelativePath((Join-Path $project 'src'),$file.FullName)
 $remove=Join-Path $stage ("$i-remove.w3x")
 $added=Join-Path $stage ("$i-added.w3x")
 $inputMap=$current
 if ($internalName -in $existing) {
  & $dotnet $packer --replace $current $file.FullName $internalName $remove
  if ($LASTEXITCODE -ne 0) {throw "Replacement failed: $($file.Name)"}
  $inputMap=$remove
 }
 & $dotnet $packer $inputMap $file.FullName $internalName $added
 if ($LASTEXITCODE -ne 0) {throw "Add failed: $($file.Name)"}
 & $dotnet $packer --verify $added $internalName $file.FullName
 if ($LASTEXITCODE -ne 0) {throw "Verify failed: $($file.Name)"}
 $current=$added
 $i++
}
New-Item -ItemType Directory -Force (Join-Path $project 'release') | Out-Null
Copy-Item -LiteralPath $current -Destination (Join-Path $project 'release\FF799X_Rx_Orianna_v18.w3x')
# Validate by MPQ hash entries, including inherited members absent from listfile.
$python=Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python (Join-Path $project 'verify.py')
if ($LASTEXITCODE -ne 0) {throw 'Full archive verification failed'}
$stage | Set-Content (Join-Path $project 'last-build.txt')
Write-Output 'PACKED AND ROUNDTRIP VERIFIED'

