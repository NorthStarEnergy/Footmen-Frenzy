$ErrorActionPreference='Stop'
$wcRoot=[IO.Path]::GetFullPath('C:\Users\User\Documents\Warcraft III\Maps')
function SafeMapPath([string]$relative) {
 $full=[IO.Path]::GetFullPath((Join-Path $wcRoot $relative))
 if(-not $full.StartsWith($wcRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Path outside Maps: $full"}
 return $full
}
$steps=@(
 @('Download','Downloads'),
 @('Test','Archive\Test\Previous layout 2026-11-05'),
 @('Solo Foots','Archive\Foots\Solo Foots\Previous layout 2026-11-05'),
 @('Foots FFA','Archive\Foots\FFA Foots\Older maps 2026-11-05'),
 @('Foots FFA Versions','Archive\Foots\FFA Foots\Versions'),
 @('Foots FFA Archive','Archive\Foots\FFA Foots\Previous empty archive'),
 @('Foots FFA Latest','Foots\FFA Foots'),
 @('Mini Foots','Foots\Mini Foots'),
 @('Archive\Test\Previous layout 2026-11-05\FF799X_Rx_Shared_Fixes_v85_TEST.w3x','Test\799X\FF799X_Rx_Shared_Fixes_v85_TEST.w3x'),
 @('Archive\Foots\Solo Foots\Previous layout 2026-11-05\Solo Tests\Solo_Foots_v1.8_4P_SHARED_FIXES_UPDATE09.w3x','Test\Solo Foots\Solo_Foots_v1.8_4P_SHARED_FIXES_UPDATE09.w3x'),
 @('Archive\Foots\Solo Foots\Previous layout 2026-11-05\Production\Solo_Foots_Production.w3x','Foots\Solo Foots\Solo_Foots_Production.w3x'),
 @('All-Heroes-Test-Arena-v1.w3x','Test\Other\All-Heroes-Test-Arena-v1.w3x'),
 @('microtrain_reforged_beta1.0.w3x','Downloads\microtrain_reforged_beta1.0.w3x')
)
# Validate every resolved destination and source before recursive directory moves.
foreach($step in $steps){$null=SafeMapPath $step[0];$dest=SafeMapPath $step[1];if(Test-Path -LiteralPath $dest){throw "Destination already exists: $dest"}}
$manifest=@()
foreach($name in @('Download','Test','Solo Foots','Foots FFA','Foots FFA Versions','Foots FFA Latest','Mini Foots')) {
 $source=SafeMapPath $name
 if((Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Directory is a link: $source"}
 foreach($file in Get-ChildItem -LiteralPath $source -Recurse -File){
  $relative=$file.FullName.Substring($wcRoot.Length+1)
  $new=$relative
  foreach($step in $steps){if($new -eq $step[0]){$new=$step[1]}elseif($new.StartsWith($step[0]+'\')){$new=$step[1]+$new.Substring($step[0].Length)}}
  $manifest+= [pscustomobject]@{Source=$relative;Destination=$new;Hash=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash;Length=$file.Length}
 }
}
foreach($name in @('All-Heroes-Test-Arena-v1.w3x','microtrain_reforged_beta1.0.w3x')){
 $step=$steps|Where-Object {$_[0] -eq $name};$file=Get-Item -LiteralPath (SafeMapPath $name)
 $manifest+=[pscustomobject]@{Source=$name;Destination=$step[1];Hash=(Get-FileHash -LiteralPath $file.FullName).Hash;Length=$file.Length}
}
$manifest|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'map-move-manifest.json')
foreach($step in $steps){
 $source=SafeMapPath $step[0];$dest=SafeMapPath $step[1]
 if(Test-Path -LiteralPath $dest){throw "Destination appeared: $dest"}
 New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest)|Out-Null
 Move-Item -LiteralPath $source -Destination $dest
}
foreach($channel in @('Foots','Test')){foreach($family in @('799X','Solo Foots','Mini Foots','FFA Foots')){New-Item -ItemType Directory -Force -Path (SafeMapPath "$channel\$family")|Out-Null;New-Item -ItemType Directory -Force -Path (SafeMapPath "Archive\$channel\$family")|Out-Null}}
foreach($entry in $manifest){$dest=SafeMapPath $entry.Destination;if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash -ne $entry.Hash){throw "Checksum mismatch: $dest"}}
Write-Output "Moved and SHA256-verified $($manifest.Count) files. Existing Archive content and W3Champions preserved."
Get-ChildItem -LiteralPath $wcRoot -Directory|Select-Object Name
