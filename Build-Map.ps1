[CmdletBinding()]
param(
 [Parameter(Mandatory)][ValidateSet('799x','solo','mini','ffa')][string]$Project,
 [Parameter(Mandatory)][string]$Name,
 [string]$Python='python',
 [string]$MapsRoot=(Join-Path $env:USERPROFILE 'Documents\Warcraft III\Maps')
)
$ErrorActionPreference='Stop'
& $Python (Join-Path $PSScriptRoot 'tools\build_map.py') $Project --name $Name
if($LASTEXITCODE -ne 0){throw 'Map build or verification failed; nothing installed'}
$meta=Get-Content -LiteralPath (Join-Path $PSScriptRoot "projects\$Project\project.json") -Raw|ConvertFrom-Json
$source=Join-Path $PSScriptRoot "build\$Project\$Name"
& (Join-Path $PSScriptRoot 'tools\Install-Wc3Map.ps1') -Source $source -Channel Tests -MapType $meta.map_type -MapsRoot $MapsRoot
$hash=(Get-FileHash -LiteralPath $source).Hash
foreach($folder in @("Tests\$($meta.map_type)",$meta.map_type)){
 $directory=Join-Path $MapsRoot $folder
 $maps=@(Get-ChildItem -LiteralPath $directory -File|Where-Object Extension -in @('.w3x','.w3m'))
 if($maps.Count -ne 1 -or $maps[0].Name -ne $Name -or (Get-FileHash -LiteralPath $maps[0].FullName).Hash -ne $hash){throw "Delivery verification failed: $directory"}
}
"Built, verified, and installed $Name for $($meta.map_type)."
