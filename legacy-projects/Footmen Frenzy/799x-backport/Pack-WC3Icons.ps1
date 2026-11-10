$ErrorActionPreference='Stop'
$project=$PSScriptRoot
$dotnet=Join-Path $project '..\mini-foots\tools\dotnet\dotnet.exe'
$packer='C:\Users\User\Documents\ChatGPT\Footmen Frenzy (Solo)\tools\MpqAdd\bin\Debug\net8.0\MpqAdd.dll'
$env:DOTNET_ROLL_FORWARD='Major'
$stage=Join-Path $project 'build-wc3icons-v25'
New-Item -ItemType Directory -Force $stage | Out-Null
$current=Join-Path $project 'release\FF799X_Rx_Gragus_v24.w3x'
$names=@('RxOriannaMove','RxOriannaAttackRed','RxOriannaProtect','RxOriannaShockwave','RxGragasBarrel','RxGragasFortitude','RxGragasSlam','RxGragasCask','GuardianTimeWarp','GuardianForceField','GuardianLantern','GuardianGuardianShield')
$files=@('war3map.wts')
foreach ($name in $names) {
 $files += "ReplaceableTextures\CommandButtons\BTN$name.blp"
 $files += "ReplaceableTextures\CommandButtonsDisabled\DISBTN$name.blp"
}
$i=0
foreach ($file in $files) {
 $payload=Join-Path $project ('src\'+$file)
 $removed=Join-Path $stage "$i-replaced.w3x"
 $added=Join-Path $stage "$i-added.w3x"
 & $dotnet $packer --replace $current $payload $file $removed
 if ($LASTEXITCODE -ne 0) {throw 'Replace failed'}
 & $dotnet $packer $removed $payload $file $added
 if ($LASTEXITCODE -ne 0) {throw 'Add failed'}
 & $dotnet $packer --verify $added $file $payload
 if ($LASTEXITCODE -ne 0) {throw 'Verify failed'}
 $current=$added
 $i++
}
Copy-Item -LiteralPath $current -Destination (Join-Path $project 'release\FF799X_Rx_WC3Icons_v25.w3x')
$python=Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python (Join-Path $project 'verify.py')
if ($LASTEXITCODE -ne 0) {throw 'Archive verification failed'}
