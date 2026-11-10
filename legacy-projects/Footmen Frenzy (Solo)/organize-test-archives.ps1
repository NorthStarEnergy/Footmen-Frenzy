$ErrorActionPreference='Stop'
$wcRoot=[IO.Path]::GetFullPath('C:\Users\User\Documents\Warcraft III\Maps')
function MapPath([string]$relative){$p=[IO.Path]::GetFullPath((Join-Path $wcRoot $relative));if(-not $p.StartsWith($wcRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Path outside Maps'};return $p}
$old=MapPath 'Test';$new=MapPath 'Tests';if(Test-Path -LiteralPath $new){throw 'Tests exists'}
Move-Item -LiteralPath $old -Destination $new
foreach($family in @('799X','Solo Foots','Mini Foots','FFA Foots','Other')){New-Item -ItemType Directory -Force -Path (MapPath "Tests\$family\Test Archives")|Out-Null}
$archiveRoot=MapPath 'Archive\Test\Previous layout 2026-11-05'
$files=@(Get-ChildItem -LiteralPath $archiveRoot -Recurse -File)
$soloOld=MapPath 'Archive\Foots\Solo Foots\Previous layout 2026-11-05\Solo Tests'
$files+=@(Get-ChildItem -LiteralPath $soloOld -File)
$relocation=@()
foreach($file in $files){
 $family=if($file.Name -match '(?i)FFA|8P|6 Player'){'FFA Foots'}elseif($file.Name -match '(?i)Solo|^SF_'){'Solo Foots'}elseif($file.Name -match '(?i)Mini'){'Mini Foots'}else{'799X'}
 if($file.FullName.StartsWith($archiveRoot+'\')){$rel=$file.FullName.Substring($archiveRoot.Length+1)}else{$rel='Solo Tests\'+$file.Name}
 $dest=MapPath "Tests\$family\Test Archives\Previous layout 2026-11-05\$rel"
 $source=[IO.Path]::GetFullPath($file.FullName);if(-not $source.StartsWith($wcRoot+'\')){throw 'Invalid source'}
 if(Test-Path -LiteralPath $dest){throw "Destination exists: $dest"}
 $relocation+=[pscustomobject]@{Source=$source;Destination=$dest;Hash=(Get-FileHash -LiteralPath $source).Hash}
}
$relocation|ConvertTo-Json -Depth 4|Set-Content (Join-Path $PSScriptRoot 'test-archive-move-manifest.json')
foreach($entry in $relocation){New-Item -ItemType Directory -Force -Path (Split-Path -Parent $entry.Destination)|Out-Null;Move-Item -LiteralPath $entry.Source -Destination $entry.Destination;if((Get-FileHash -LiteralPath $entry.Destination).Hash -ne $entry.Hash){throw 'Checksum mismatch'}}
Write-Output "Tests renamed and $($relocation.Count) older test files archived under their map types."
