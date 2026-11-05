[CmdletBinding(SupportsShouldProcess)]
param(
 [Parameter(Mandatory)][string]$Source,
 [string]$MapsRoot='C:\Users\User\Documents\Warcraft III\Maps'
)
$ErrorActionPreference='Stop'
& (Join-Path (Split-Path -Parent $PSScriptRoot) 'Install-Wc3Map.ps1') -Source $Source -MapType 'Mini Foots' -Channel Tests -MapsRoot $MapsRoot -WhatIf:$WhatIfPreference
