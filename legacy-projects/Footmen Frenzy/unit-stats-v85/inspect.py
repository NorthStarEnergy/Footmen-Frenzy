from pathlib import Path
import sys
W=Path.cwd();sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions
for v in ['799x','solo']:
 s=(W/'shared-sync-v85'/v/'src/war3map.j').read_text(encoding='utf8');f=functions(s)
 for n in ['FFGS_ApplyUnit','SoloFootsSpawnPrepareStats','SoloFootsSpawnApplyStats','SoloFootsSpawnCapacity','SoloFootsSpawnStart','SoloFootsSpawnTick','FFGS_ProcessIndex']:
  if n in f:print(v,f[n])
