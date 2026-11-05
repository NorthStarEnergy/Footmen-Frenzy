$ErrorActionPreference='Stop'
$staged=$PSScriptRoot
$project='C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots'
$python='C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$expected=(Get-FileHash -LiteralPath (Join-Path $staged 'Mini Foots v7.w3x')).Hash
$folders=@('C:\Users\User\Documents\Warcraft III\Maps\Mini Foots','C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Mini Foots',(Join-Path $project 'release'))
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
  try { Move-Item -LiteralPath $old -Destination $target } catch { Copy-Item -LiteralPath $old -Destination $target; Write-Output "Old map is open; kept it in place and saved an archive copy: $old" }
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

