from pathlib import Path
import re,json
root=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy')
out=Path('legacy-installer-migration');out.mkdir(exist_ok=True)
helper=r'''# Shared delivery for historical installers. Keep validation at each call site.
function Install-LegacyTestMap {
 param([Parameter(Mandatory)][string]$Source,[Parameter(Mandatory)][string]$MapType,[string]$MapsRoot)
 & 'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\Install-Wc3Map.ps1' -Source $Source -MapType $MapType -Channel Tests -MapsRoot $MapsRoot | Out-Null
 $expected=(Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
 foreach($folder in @((Join-Path $MapsRoot "Tests\$MapType"),(Join-Path $MapsRoot $MapType))){
  $active=@(Get-ChildItem -LiteralPath $folder -File|Where-Object Extension -in @('.w3x','.w3m'))
  $path=Join-Path $folder ([IO.Path]::GetFileName($Source))
  if($active.Count -ne 1 -or $active[0].FullName -ne $path -or (Get-FileHash -LiteralPath $path).Hash -ne $expected){throw "Installation verification failed: $folder"}
  [pscustomobject]@{path=$path;sha256=$expected.ToLowerInvariant();verified=$true;onlyMapInTest=$true}
 }
}
'''
(out/'Legacy-TestDelivery.ps1').write_text(helper)
def replace_loop(s,pattern,new):
 m=re.search(pattern,s);assert m,pattern
 start=m.start();op=s.index('{',m.end());depth=0
 # Balanced braces; these legacy loop bodies have balanced string braces too.
 for i in range(op,len(s)):
  if s[i]=='{':depth+=1
  elif s[i]=='}':
   depth-=1
   if depth==0:return s[:start]+new+s[i+1:]
 raise ValueError('unbalanced')
header="param([string]$MapsRoot='C:\\Users\\User\\Documents\\Warcraft III\\Maps')\n. 'C:\\Users\\User\\Documents\\ChatGPT\\Footmen Frenzy\\Legacy-TestDelivery.ps1'\n"
plan=[]
for p in root.rglob('Install*.ps1'):
 s=p.read_text(encoding='utf-8-sig')
 if 'OneDrive' not in s:continue
 rel=p.relative_to(root);name=rel.parts[0]
 if name=='hero-sync':
  s=re.sub(r'\$destinations=@\([^\n]+\)\n','',s)
  new="""foreach ($variant in @('mini','solo')) {
 $report=Get-Content -LiteralPath (Join-Path $root "$variant\\verification.json") -Raw | ConvertFrom-Json
 $source=$report.output
 if ((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $report.sha256) {throw 'Verified release changed'}
 $family=if($variant -eq 'mini'){'Mini Foots'}else{'FFA Foots'}
 $records+=@(Install-LegacyTestMap -Source $source -MapType $family -MapsRoot $MapsRoot)
}"""
  s=replace_loop(s,r'foreach \(\$maps in \$destinations\)',new)
 elif name=='hero-polish':
  s=s.replace("folder='Test'","folder='799X'")
  s=replace_loop(s,r'foreach \(\$maps in @\([^\n]+\)\)',"$family=if($plan.variant -eq 'mini'){'Mini Foots'}elseif($plan.variant -eq 'solo'){'FFA Foots'}else{'799X'}\n $records+=@(Install-LegacyTestMap -Source $source -MapType $family -MapsRoot $MapsRoot)")
 elif name=='799x-backport':
  s=re.sub(r'\$roots = @\([\s\S]*?\n\)\n','',s)
  s=replace_loop(s,r'foreach \(\$root in \$roots\)',"$records+=@(Install-LegacyTestMap -Source $release -MapType '799X' -MapsRoot $MapsRoot)")
 elif name in ('observer-poker','six-player-ffa'):
  s=re.sub(r'\$destinations=@\([\s\S]*?\n\)\n','',s)
  family='799X' if name=='observer-poker' else 'FFA Foots'
  s=replace_loop(s,r'foreach \(\$directory in [^\n]+\)',f"$results+=@(Install-LegacyTestMap -Source $release -MapType '{family}' -MapsRoot $MapsRoot)")
 elif 'foreach ($folder in' in s:
  # Preserve the existing project-release copy loop and checksum sidecars.
  s=re.sub(r"foreach \(\$folder in @\([^\n]+\)\) \{", "foreach ($folder in @((Join-Path (Split-Path $PSScriptRoot) '799x-backport\\\\release'))) {",s)
  s=s.replace('$records = @()',"$records = @(Install-LegacyTestMap -Source $report.output -MapType '799X' -MapsRoot $MapsRoot)")
 else:
  s=replace_loop(s,r'foreach \(\$maps in @\([^\n]+\)\)',"$records+=@(Install-LegacyTestMap -Source $report.output -MapType '799X' -MapsRoot $MapsRoot)")
 assert 'OneDrive' not in s,str(rel)
 assert not re.search(r'Maps[\\/]Test(?:[\\/\x27\x22]|$)',s),str(rel)
 target=out/'updated'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(header+s,encoding='utf-8-sig')
 backup=out/'original'/rel;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(p.read_bytes())
 plan.append({'source':str(target.resolve()),'destination':str(p)})
plan.append({'source':str((out/'Legacy-TestDelivery.ps1').resolve()),'destination':str(root/'Legacy-TestDelivery.ps1')})
(out/'plan.json').write_text(json.dumps(plan,indent=2));print('Staged',len(plan)-1,'legacy installers and shared delivery helper')
