"""Build the debug farm command card and shared shop from Warcraft object records."""
from copy import deepcopy
import struct
from restore_rc6_item_text import parse, dump
from build_799x_items_catalog import merged_objects

ICON = r"ReplaceableTextures\CommandButtons\BTNFootsPageTurn.blp"
ORDERS = ["thunderclap","roar","stomp","berserk","fanofknives","howlofterror","windwalk","avatar","immolation"]
# These art paths are inherited from standard Warcraft units when no override exists.
ART = ["Footman","Knight","Knight","Archer","Dryad","Dryad","Raider","Abomination","Abomination",
       "Banshee","ChaosWarlock","MortarTeam","MortarTeam","CryptFiend","SpellBreaker","DruidOfTheTalon",
       "HeadHunterBerserker","Ghoul","Peasant","SkeletonMage","Ghost","Rifleman","Huntress","Grunt","Tauren","Tauren"]

# Stock objects whose name or command icon comes from the Warcraft data files.
HERO_DEFAULTS = {
    "Edem": ("Demon Hunter","HeroDemonHunter"), "Edmm": ("Demon Hunter (Demon Form)","Metamorphosis"),
    "Eevi": ("Illidan","EvilIllidan"), "Ekee": ("Keeper of the Grove","KeeperOfTheGrove"),
    "Ekgg": ("Keeper of the Grove","KeeperGhostBlue"), "Emoo": ("Priestess of the Moon","PriestessOfTheMoon"),
    "Ewar": ("Warden","HeroWarden"), "Hamg": ("Archmage","HeroArchMage"),
    "Harf": ("Arthas","Arthas"), "Hblm": ("Blood Mage","HeroBloodElfPrince"),
    "Hgam": ("Ghostly Archmage","GhostOfKelThuzad"), "Hjai": ("Jaina","Jaina"),
    "Hlgr": ("Lord Garithos","Garithos"), "Hmkg": ("Mountain King","HeroMountainKing"),
    "Hpal": ("Paladin","HeroPaladin"), "Hvwd": ("Sylvanas Windrunner","SylvanusWindrunner"),
    "Naka": ("Akama","Akama"), "Nal2": ("Alchemist (Chemical Rage)","HeroAlchemist"),
    "Nal3": ("Alchemist (Chemical Rage)","HeroAlchemist"), "Nalc": ("Alchemist","HeroAlchemist"),
    "Nalm": ("Alchemist (Chemical Rage)","HeroAlchemist"), "Nbrn": ("Dark Ranger","BansheeRanger"),
    "Nbst": ("Beastmaster","BeastMaster"), "Nfir": ("Firelord","HeroAvatarOfFlame"),
    "Nngs": ("Naga Sea Witch","NagaSeaWitch"), "Npbm": ("Pandaren Brewmaster","PandarenBrewmaster"),
    "Nplh": ("Pit Lord","PitLord"), "Nrob": ("Robo-Goblin","RoboGoblin"),
    "Nswt": ("Sea Witch","NagaSeaWitch"), "Ntin": ("Tinker","HeroTinker"),
    "Obla": ("Blademaster","HeroBlademaster"), "Ofar": ("Far Seer","HeroFarseer"),
    "Oshd": ("Shadow Hunter","ShadowHunter"), "Otch": ("Tauren Chieftain","HeroTaurenChieftain"),
    "Othr": ("Thrall","Thrall"), "Ucrl": ("Crypt Lord","HeroCryptLord"),
    "Udea": ("Death Knight","HeroDeathKnight"), "Udre": ("Dreadlord","HeroDreadLord"),
    "Ulic": ("Lich","HeroLich"),
}

def value(v):
    if isinstance(v,str):
        return 3,v.encode()+b'\0'
    if isinstance(v,float):
        return 1,struct.pack('<f',v)
    return 0,struct.pack('<i',v)

def set_mod(mods,field,v):
    field=field.encode()
    k,b=value(v)
    for m in mods:
        if m[0]==field:
            m[1:3]=[k,b]
            return
    mods.append([field,k,b,bytes(4)])

def add_record(table,old,new,mods):
    assert not any(h[4:8]==new.encode() for h,_ in table[1][1]),new
    # Reuse the baseline's version-specific object header after the rawcodes.
    prefix=table[1][1][0][0][8:]
    table[1][1].append([old.encode()+new.encode()+prefix,mods])

def ability(table,skin,id,title,desc,art,x,y,order,target=False):
    fields = [(f,0,0,v) for f,v in dict(anam=title,aart=art,abpx=x,abpy=y,ahky="").items()]
    fields.extend([("atp1",1,0,title),("aub1",1,0,desc)])
    if not skin:
        fields += [(f,0,0,v) for f,v in dict(aher=0,aite=0,alev=1,arlv=1,areq="",acat="",atat="",aeat="").items()]
        fields += [(f,1,i,v) for i,(f,v) in enumerate([("Ncl1",0.),("Ncl2",int(target)),("Ncl3",1),("Ncl4",0.),("Ncl5",0),("Ncl6",order)],1)]
        fields += [(f,1,0,v) for f,v in dict(aran=99999. if target else 0.,atar="air,ground,hero,friend,enemy,neutral,self,vuln,invu" if target else "",amcs=0,acdn=0.,acas=0.).items()]
    mods=[]
    for f,l,p,v in fields:
        k,b=value(v)
        mods.append([f.encode(),k,struct.pack('<ii',l,p)+b,bytes(4)])
    add_record(table,'ANcl',id,mods)

def build(arc,src,wts,roster,registered):
    units=merged_objects(arc,wts,'w3u')
    heroes=[id for id,row in units.items() if id[0].isupper() and row['parent'][0].isupper() and id!='H0R0']
    heroes=list(dict.fromkeys([id for id in registered if id in heroes]+heroes))
    for skin in (False,True):
        prefix='war3mapSkin' if skin else 'war3map'
        data=arc.read(prefix+'.w3u')
        table=parse(data)
        assert dump(table)==data
        records={h[4:8].decode():mods for h,mods in table[1][1]}
        if skin:
            for k,v in dict(usca=1.25,ussc=1.45,unam="Debug Farm",utip="Debug Farm").items():
                set_mod(records['n034'],k,v)
        else:
            set_mod(records['n034'],'uabi','Avul,aFLu,aFLd,aFPg')
            # Sell ordinary units as hire buttons to bypass hero-tier requirements and food limits.
            for i,id in enumerate(heroes):
                record=units[id]
                fields=units.get(record['parent'],{}).get('fields',{}) | record['fields']
                base_name,base_art=HERO_DEFAULTS.get(record['parent'],('',''))
                name=fields.get(('unam',0),base_name)
                art=fields.get(('uico',0),rf"ReplaceableTextures\CommandButtons\BTN{base_art}.blp")
                assert name and (fields.get(('uico',0)) or base_art)
                slot=i%10
                mods=deepcopy(records['hTNP'])
                for k,v in dict(unam=name,utip=name,utub=f"Hire {name} at level 18.",uico=art,
                                usma=2,ubpx=slot%4,ubpy=slot//4,uhot="",uabi="Aloc").items():
                    set_mod(mods,k,v)
                add_record(table,'hfoo',f'd{i:03}',mods)
        if 'hTNP' in records:
            set_mod(records['hTNP'],'uico',ICON)
        mods=[]
        for k,v in (dict(unam="Hero Tavern",utip="Hero Tavern",umdl=r"buildings\other\Tavern\Tavern.mdl") if skin else
                    dict(useu="",uabi="Ane2,Avul,Asud",upat="",ucol=0.,uacq=700.)).items():
            set_mod(mods,k,v)
        add_record(table,'ntav','nDbT',mods)
        (src/(prefix+'.w3u')).write_bytes(dump(table))
        data=arc.read(prefix+'.w3a')
        table=parse(data,extended=True)
        assert dump(table)==data
        for i,(name,id) in enumerate(roster):
            slot=i%9
            art=units[id]['fields'].get(('uico',0),rf"ReplaceableTextures\CommandButtons\BTN{ART[i]}.blp")
            ability(table,skin,f'aF{i:02}',name,f"Spawn one Neutral Hostile {name} near the middle shop.",art,slot%4,slot//4,ORDERS[slot])
        for id,name,detail,art,slot,order,target in [
            ('aFLu','Level Up','Target a hero to raise its level by one.','BTNStatUp',9,'innerfire',True),
            ('aFLd','Level Down','Target a hero to lower its level by one. Minimum level 1.','BTNStatDown',10,'curse',True),
            ('aFPg','Turn Page','Show the next page of army units. Page three returns to page one.','BTNFootsPageTurn',11,'divineshield',False)]:
            ability(table,skin,id,name,detail,rf"ReplaceableTextures\CommandButtons\{art}.blp",slot%4,slot//4,order,target)
        (src/(prefix+'.w3a')).write_bytes(dump(table))
    return heroes
