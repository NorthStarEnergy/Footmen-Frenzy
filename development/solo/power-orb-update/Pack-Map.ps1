$ErrorActionPreference='Stop'
$project=$PSScriptRoot
$dotnet=Join-Path $project 'tools\dotnet\dotnet.exe'
$packer='C:\Users\User\Documents\ChatGPT\Footmen Frenzy (Solo)\tools\MpqAdd\bin\Debug\net8.0\MpqAdd.dll'
$extractor='C:\Users\User\Documents\ChatGPT\Footmen Frenzy (Solo)\tools\bin\MpqExtract\MpqExtract.dll'
$env:DOTNET_ROLL_FORWARD='Major'
$stage=Join-Path $project ('build-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory $stage | Out-Null
$current='C:\Users\User\Documents\Warcraft III\Maps\Test\Archive\FF799X_Rx_HeroTavern_v1.w3x'
$i=0
foreach ($file in Get-ChildItem (Join-Path $project 'src') -File -Recurse) {
 $internalName=[System.IO.Path]::GetRelativePath((Join-Path $project 'src'),$file.FullName)
 $remove=Join-Path $stage ("$i-remove.w3x")
 $added=Join-Path $stage ("$i-added.w3x")
 $inputMap=$current
 if (Test-Path -LiteralPath (Join-Path $project ('base\files\'+$internalName))) {
  & $dotnet $packer --replace $current $file.FullName $internalName $remove
  if ($LASTEXITCODE -ne 0) {throw "Replacement failed: $($file.Name)"}
  $inputMap=$remove
 }
 $addOutput= & $dotnet $packer $inputMap $file.FullName $internalName $added 2>&1
 if ($LASTEXITCODE -ne 0 -and ($addOutput -join "`n") -match 'Archive already contains') {
  # Original MPQ may contain assets omitted from its extracted listfile.
  & $dotnet $packer --replace $inputMap $file.FullName $internalName $remove
  if ($LASTEXITCODE -ne 0) {throw "Unlisted replacement failed: $internalName"}
  & $dotnet $packer $remove $file.FullName $internalName $added
 } else { $addOutput | Write-Output }
 if ($LASTEXITCODE -ne 0) {throw "Add failed: $($file.Name)"}
 & $dotnet $packer --verify $added $internalName $file.FullName
 if ($LASTEXITCODE -ne 0) {throw "Verify failed: $($file.Name)"}
 $current=$added
 $i++
}
New-Item -ItemType Directory -Force (Join-Path $project 'release') | Out-Null
Copy-Item -LiteralPath $current -Destination (Join-Path $project 'release\Mini Foots v8.w3x')
& $dotnet $extractor (Join-Path $project 'release\Mini Foots v8.w3x') (Join-Path $stage 'roundtrip')
if ($LASTEXITCODE -ne 0) {throw 'Extraction failed'}
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $project 'extract_payloads.py') (Join-Path $stage 'roundtrip')
if ($LASTEXITCODE -ne 0) {throw 'Named payload extraction failed'}
foreach ($file in Get-ChildItem (Join-Path $project 'src') -File -Recurse) {
 $internalName=[System.IO.Path]::GetRelativePath((Join-Path $project 'src'),$file.FullName)
 $rt=Join-Path $stage ('roundtrip\files\'+$internalName)
 if ((Get-FileHash $file.FullName).Hash -ne (Get-FileHash $rt).Hash) {throw "Roundtrip mismatch: $($file.Name)"}
}
$stage | Set-Content (Join-Path $project 'last-build.txt')
Write-Output 'PACKED AND ROUNDTRIP VERIFIED'
