from pathlib import Path
import sys,shutil,json,ctypes,hashlib
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W/'hero-polish'));from archive_helpers import storm,read_storm,c,archive,entries
base=W/'tf-wc3-icons-v50/release/FF799X_Rx_TF_Guardian_WC3Icons_v50.w3x';test=R/'compaction-trial.w3x';shutil.copy2(base,test)
a=archive(base);old=entries(a)
storm.SFileCompactArchive.argtypes=[c.c_void_p,c.c_wchar_p,c.c_bool];storm.SFileCompactArchive.restype=c.c_bool;h=c.c_void_p();assert storm.SFileOpenArchive(str(test),0,0,c.byref(h));ok=storm.SFileCompactArchive(h,str(R/'known-files.txt'),False);err=ctypes.windll.kernel32.GetLastError();storm.SFileCloseArchive(h)
print('compact',ok,'error',err,'before',base.stat().st_size,'after',test.stat().st_size)
if ok:
 b=archive(test);new=entries(b);changed=[str(k) for k in old if k not in new or old[k]!=new[k]];print('old',len(old),'new',len(new),'changed',len(changed));(R/'compaction.json').write_text(json.dumps(dict(success=not changed,before=base.stat().st_size,after=test.stat().st_size,saved=base.stat().st_size-test.stat().st_size,old=len(old),new=len(new),changed=changed),indent=2))
else:(R/'compaction.json').write_text(json.dumps(dict(success=False,winerror=err),indent=2))


