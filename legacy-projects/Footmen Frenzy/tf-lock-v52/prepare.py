from pathlib import Path
import sys
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W/'hero-polish'));from archive_helpers import storm,read_storm,c,functions
base=W/'tf-orb-v51/release/FF799X_Rx_TF_Guardian_Orbs_v51.w3x';h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h));s=read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n');assert storm.SFileCloseArchive(h)
f=functions(s)['TF33_Show'];g=f.replace('    call SetUnitX(orb,GetUnitX(c))','''    local integer ticks=LoadInteger(TF33_H,h,6)
    local real pulse=0.
    local real scale
    if LoadBoolean(TF33_H,h,5) and ticks<8 then
        set pulse=Sin(3.14159265*I2R(ticks)/8.)
    endif
    set scale=1.8*(1.+.08*pulse)
    call SetUnitX(orb,GetUnitX(c))''').replace('GetUnitFlyHeight(c)+330.','GetUnitFlyHeight(c)+330.+12.*pulse').replace('SetUnitScale(orb,1.8,1.8,1.8)','SetUnitScale(orb,scale,scale,scale)');assert f!=g;s=s.replace(f,g,1);(R/'src/war3map.j').write_text(s,encoding='utf8');print('Lock animation prepared')


