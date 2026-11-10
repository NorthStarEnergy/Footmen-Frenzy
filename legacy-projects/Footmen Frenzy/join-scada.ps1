$ErrorActionPreference = 'Stop'
$parts = 'C:\SCADA\H2O-SPlus-parts'
$target = 'C:\SCADA\H2O-Oshawa-SPlus-VM.tar.gz'
if (Test-Path -LiteralPath $target) { throw 'Archive already exists; refusing to overwrite it.' }
$files = for ($i=0; $i -le 65; $i++) { $p = Join-Path $parts ('H2O-Oshawa-SPlus-VM.tar.gz.part{0:D3}' -f $i); $f = Get-Item -LiteralPath $p; $expected = if ($i -eq 65) { 230686720 } else { 524288000 }; if ($f.Length -ne $expected) { throw "Unexpected size: $p" }; $f }
$out = [System.IO.File]::Open($target, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
try { foreach ($f in $files) { $inputStream = [System.IO.File]::OpenRead($f.FullName); try { $inputStream.CopyTo($out, 4194304) } finally { $inputStream.Dispose() } } } finally { $out.Dispose() }
Get-Item -LiteralPath $target | Select-Object FullName,Length
