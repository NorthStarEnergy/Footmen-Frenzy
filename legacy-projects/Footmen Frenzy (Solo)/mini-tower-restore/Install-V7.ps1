$ErrorActionPreference='Stop'
$staged=$PSScriptRoot
$project='C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots'
$python='C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$backup=Join-Path $project 'archive\v6-before-v7-towers-heroes'
if (Test-Path -LiteralPath $backup) {throw 'Backup already exists; refusing to overwrite'}
$expected=(Get-FileHash -LiteralPath (Join-Path $staged 'Mini Foots v7.w3x')).Hash
$folders=@('C:\Users\User\Documents\Warcraft III\Maps\Mini Foots','C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Mini Foots',(Join-Path $project 'release'))
foreach ($folder in $folders) {
 if (Test-Path -LiteralPath (Join-Path $folder 'Mini Foots v7.w3x')) {throw "v7 already exists: $folder"}
}
New-Item -ItemType Directory -Path $backup | Out-Null
$sources=@('war3map.j','war3map.wts','war3map.w3i','war3map.w3u')
$scripts=@('build_source.py','Pack-Map.ps1','verify.py','record_delivery.py','render_audit.py')
New-Item -ItemType Directory -Path (Join-Path $backup 'src') | Out-Null
foreach ($name in $sources) {
 Copy-Item -LiteralPath (Join-Path $project ('src\'+$name)) -Destination (Join-Path $backup ('src\'+$name))
 Copy-Item -LiteralPath (Join-Path $staged $name) -Destination (Join-Path $project ('src\'+$name)) -Force
}
foreach ($name in ($scripts+@('README.md','changes.json','verification.json','last-build.txt'))) {
 Copy-Item -LiteralPath (Join-Path $project $name) -Destination (Join-Path $backup $name)
}
foreach ($name in ($scripts+@('hero_policy.py','hero-policy.json'))) {
 Copy-Item -LiteralPath (Join-Path $staged $name) -Destination (Join-Path $project $name) -Force
}
$build=Join-Path $project 'build-v7-towers-heroes'
New-Item -ItemType Directory -Path $build | Out-Null
Copy-Item -LiteralPath (Join-Path $staged 'final-roundtrip') -Destination (Join-Path $build 'roundtrip') -Recurse
$build | Set-Content -LiteralPath (Join-Path $project 'last-build.txt')
$changes=Get-Content -LiteralPath (Join-Path $project 'changes.json') -Raw | ConvertFrom-Json
$changes.name='Mini Foots v7'
$changes | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $project 'changes.json')
foreach ($folder in $folders) {
 New-Item -ItemType Directory -Path $folder -Force | Out-Null
 $dest=Join-Path $folder 'Mini Foots v7.w3x'
 Copy-Item -LiteralPath (Join-Path $staged 'Mini Foots v7.w3x') -Destination $dest
 if ((Get-FileHash -LiteralPath $dest).Hash -ne $expected) {throw "Installed hash mismatch: $dest"}
 $old=Join-Path $folder 'Mini Foots v6.w3x'
 if (Test-Path -LiteralPath $old) {
  $archive=if ($folder -eq (Join-Path $project 'release')) {Join-Path $project 'archive'} else {Join-Path (Split-Path $folder -Parent) 'Mini Foots Archive'}
  New-Item -ItemType Directory -Path $archive -Force | Out-Null
  $target=Join-Path $archive 'Mini Foots v6 - before towers and hero restrictions.w3x'
  if (Test-Path -LiteralPath $target) {throw "Archive already exists: $target"}
  # Resolved explicit paths must remain in the approved Mini Foots directories.
  if ([IO.Path]::GetFullPath($old) -ne $old -or [IO.Path]::GetFullPath($target) -ne $target) {throw 'Unexpected archive path'}
  Move-Item -LiteralPath $old -Destination $target
 }
}
$readme=Get-Content -LiteralPath (Join-Path $project 'README.md') -Raw
$readme=$readme.Replace('Current release: Mini Foots v6.','Current release: Mini Foots v7.')
$readme+="`n`n### Mini Foots v7 - edge towers and hero availability`nRestores all 16 towers to their original v2 terrain edge pads, preserving eight-player ownership and current base positions. Blocks Twisted Fate, Mundo, Demon Knight, Santa, Death Sheep, Killa and other non-roster/test hero recruitment, including normal/random/debug stock paths. Orianna, Gragus and the random-pick token remain available. The 799X v13 Orianna/Gragus/zoom functions are already identical and verified; Stats keeps Mini's eight-player layout. JASS parser, 652 regression checks, and additional policy/tower/donor checks pass. Live Warcraft testing remains pending.`n"
$readme | Set-Content -LiteralPath (Join-Path $project 'README.md') -Encoding utf8
$audit=Join-Path $project 'audit\v7-towers-heroes'
New-Item -ItemType Directory -Path $audit -Force | Out-Null
foreach ($name in @('verification.json','hero-policy.json','positions.json','terrain-positions.png','ui-differences.json')) {
 Copy-Item -LiteralPath (Join-Path $staged $name) -Destination (Join-Path $audit $name)
}
& $python (Join-Path $project 'verify.py')
if ($LASTEXITCODE -ne 0) {throw 'Installed regression checks failed'}
& $python (Join-Path $project 'record_delivery.py')
if ($LASTEXITCODE -ne 0) {throw 'Delivery verification failed'}
Write-Output "Installed Mini Foots v7 in both Maps folders; SHA256 $expected"
