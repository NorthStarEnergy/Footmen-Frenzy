[CmdletBinding(SupportsShouldProcess)]
param(
 [Parameter(Mandatory)][string]$Source,
 [string]$MapType='799X',
 [ValidateSet('Tests','Foots','Main')][string]$Channel='Tests',
 [string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps'
)
$ErrorActionPreference='Stop'
& 'C:\Users\User\Documents\ChatGPT\Footmen Frenzy (Solo)\Install-Wc3Map.ps1' -Source $Source -MapType $MapType -Channel $Channel -MapsRoot $MapsRoot -WhatIf:$WhatIfPreference
