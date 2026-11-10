$ErrorActionPreference='Stop'
$root='C:\Users\User\Documents\Warcraft III\Maps'
$oldRoot='C:\Users\User\OneDrive\Documents\Warcraft III\Maps'
$plan=Get-Content -LiteralPath "$PSScriptRoot\foot-consolidation-plan.json" -Raw|ConvertFrom-Json
$installs=Get-Content -LiteralPath "$PSScriptRoot\foot-family-install-plan.json" -Raw|ConvertFrom-Json
# Validate the entire plan before writing or moving any map.
foreach($row in $plan){
 $src=[IO.Path]::GetFullPath($row.source);$dst=[IO.Path]::GetFullPath($row.destination)
 if(-not ($src.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase) -or $src.StartsWith($oldRoot+'\',[StringComparison]::OrdinalIgnoreCase))){throw "Source outside map roots: $src"}
 if(-not $dst.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Destination outside local Maps: $dst"}
 if(-not(Test-Path -LiteralPath $src -PathType Leaf)){throw "Missing source: $src"}
 if(Test-Path -LiteralPath $dst){throw "Destination exists: $dst"}
}
foreach($row in $installs){& "$PSScriptRoot\Install-Wc3Map.ps1" -Source $row.source -Channel Main -MapType $row.family}
foreach($family in @('799X','Solo Foots','Mini Foots','FFA Foots')){
 $current=@(Get-ChildItem -LiteralPath (Join-Path $root $family) -File|Where-Object Extension -in @('.w3x','.w3m'))
 if($current.Count -ne 1){throw "Expected one current main map: $family"}
 & "$PSScriptRoot\Install-Wc3Map.ps1" -Source $current[0].FullName -Channel Tests -MapType $family
}
$log=[Collections.Generic.List[object]]::new()
foreach($row in $plan){
 $hash=(Get-FileHash -LiteralPath $row.source -Algorithm SHA256).Hash
 New-Item -ItemType Directory -Force -Path (Split-Path -Parent $row.destination)|Out-Null
 Move-Item -LiteralPath $row.source -Destination $row.destination
 if((Get-FileHash -LiteralPath $row.destination -Algorithm SHA256).Hash -ne $hash){throw "Hash mismatch: $($row.destination)"}
 $log.Add([pscustomobject]@{Source=$row.source;Destination=$row.destination;SHA256=$hash})
 $log|ConvertTo-Json -Depth 4|Set-Content -LiteralPath "$PSScriptRoot\foot-consolidation-manifest.json" -Encoding UTF8
}
"Moved and hash-verified $($log.Count) maps."
Get-ChildItem -LiteralPath (Join-Path $root Tests) -Directory|ForEach-Object {
 $active=@(Get-ChildItem -LiteralPath $_.FullName -File|Where-Object Extension -in @('.w3x','.w3m'))
 if($active.Count -ne 1){throw "Expected exactly one active test in $($_.FullName), found $($active.Count)"}
 [pscustomobject]@{Family=$_.Name;CurrentTest=$active[0].Name}
}
