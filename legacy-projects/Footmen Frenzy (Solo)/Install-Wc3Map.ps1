[CmdletBinding(SupportsShouldProcess)]
param(
 [Parameter(Mandatory)][string]$Source,
 [Parameter(Mandatory)][ValidateSet('Foots','Tests','Main')][string]$Channel,
 [Parameter(Mandatory)][string]$MapType,
 [string]$MapsRoot=(Join-Path $env:USERPROFILE 'Documents\Warcraft III\Maps')
)
$ErrorActionPreference='Stop'
& 'C:\Users\User\Documents\GitHub\Footmen Frenzy\tools\Install-Wc3Map.ps1' -Source $Source -Channel $Channel -MapType $MapType -MapsRoot $MapsRoot -WhatIf:$WhatIfPreference
