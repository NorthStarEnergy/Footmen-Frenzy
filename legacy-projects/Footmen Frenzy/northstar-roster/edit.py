from pathlib import Path
p = Path(__file__).parent / 'field-roster.js'
s = p.read_text(encoding='utf-8-sig')
s = s.replace("const siteOf = r =>", "const siteOf = r => /iroquois.*(?:230|\\bHV\\b|\\bTS\\b)/i.test(String(r.siteId || '')+' '+String(r.site || '')) ? (window.NorthStarSites?.resolve('site:iroquois-falls-230-kv') || {id:'site:iroquois-falls-230-kv',name:'Iroquois Falls 230 kV'}) :")
s = s.replace("  function render() {", """  const companyOf = r => String(r.company || (r.kind==='Contractor'?'Contractor':'NorthStar')).trim();
  const companyKey = r => {
    const key=companyOf(r).toLowerCase().replace(/[^a-z0-9]/g,'');
    return ['northstar','northstarenergy'].includes(key)?'northstar':key;
  };
  const companyTone = r => companyKey(r)==='northstar'?0:1+[...companyKey(r)].reduce((h,c)=>(h*31+c.charCodeAt(0))>>>0,0)%5;
  function render() {""")
start=s.index('    const selectedSites=')
end=s.index('      if (!people.length)',start)
s=s[:start]+"""    let layout=[];
    try { layout=JSON.parse(document.querySelector('#nsStatusWorkers')?.dataset.stationGroups || '[]'); } catch {}
    const siteKey = s => window.NorthStarSites?.resolve(s.id)?.id || window.NorthStarSites?.resolve(s.name)?.id || s.id;
    const layoutIds=layout.map(names=>names.map(name=>window.NorthStarSites?.resolve(name)?.id || name));
    const groupOf = s => {const i=layoutIds.findIndex(ids=>ids.includes(siteKey(s)));return i<0?layout.length:i;};
    const selectedSites=sites.filter(s=>!station.value || s.id===station.value).sort((a,b)=>groupOf(a)-groupOf(b) || (layoutIds[groupOf(a)]?.indexOf(siteKey(a))??0)-(layoutIds[groupOf(b)]?.indexOf(siteKey(b))??0) || a.name.localeCompare(b.name));
    let previousArea=-1;
    $('tbody').innerHTML=selectedSites.map(s=>{
      const people=rows.filter(r=>siteOf(r).id===s.id && (presence.value==='all' || (presence.value==='out')===(r.status==='checked-out')) && `${r.name} ${r.company || ''}`.toLowerCase().includes(query)).sort((a,b)=>Number(companyKey(b)==='northstar')-Number(companyKey(a)==='northstar') || companyKey(a).localeCompare(companyKey(b)) || Number(Boolean(b.alone))-Number(Boolean(a.alone)) || a.name.localeCompare(b.name));
"""+s[end:]
s=s.replace("      return (compact?'':", """      const area=groupOf(s), areaStart=area!==previousArea;
      previousArea=area;
      const areaHeading=!compact && layout.length && areaStart ? `<tr class="fr-area"><th colspan="7" scope="rowgroup">${esc(layout[area]?.join(' · ') || 'Other sites')}</th></tr>` : '';
      return areaHeading+(compact?'':""")
s=s.replace('people.map(r=>{', 'people.map((r,index)=>{')
s=s.replace("        const company=r.company || (r.kind==='Contractor'?'Contractor':'NorthStar');", """        const company=companyOf(r);
        const key=companyKey(r), first=index===0 || companyKey(people[index-1])!==key, last=index===people.length-1 || companyKey(people[index+1])!==key;
        const companyClass=`fr-company-${companyTone(r)}${first?' fr-company-start':''}${last?' fr-company-end':''}`;""")
s=s.replace('class="${r.needsHelp?', 'class="${companyClass} ${r.needsHelp?')
p.write_text(s,encoding='utf-8')
p=Path(__file__).parent/'field-roster.css'
s=p.read_text(encoding='utf-8-sig').replace('font-size:16px!important;font-weight:600','font-size:13px!important;font-weight:600').replace('min-height:26px!important','min-height:22px!important').replace('font-size:16px!important;line-height:1.35;height:34px','font-size:13px!important;line-height:1.35;height:30px')
s+='''
/* Geographic sections mirror the fixed worker dashboard; company colors are stable. */
:is(#fieldRoster,#overviewWorkerList) .fr-area th{border:3px solid #718a9d;background:#23313c;color:#edf4fa;padding:9px 10px;font-size:12px;font-weight:700;white-space:normal;line-height:1.4}
:is(#fieldRoster,#overviewWorkerList) .fr-station th{border:2px solid #536978;background:#18242d;padding:6px 9px}
:is(#fieldRoster,#overviewWorkerList) .fr-company-0{--company-rgb:69,168,142}
:is(#fieldRoster,#overviewWorkerList) .fr-company-1{--company-rgb:99,158,218}
:is(#fieldRoster,#overviewWorkerList) .fr-company-2{--company-rgb:174,134,211}
:is(#fieldRoster,#overviewWorkerList) .fr-company-3{--company-rgb:211,163,93}
:is(#fieldRoster,#overviewWorkerList) .fr-company-4{--company-rgb:91,175,192}
:is(#fieldRoster,#overviewWorkerList) .fr-company-5{--company-rgb:205,130,154}
:is(#fieldRoster,#overviewWorkerList) tr[data-fr-id] td{background:rgba(var(--company-rgb),.10)}
:is(#fieldRoster,#overviewWorkerList) tr[data-fr-id] td:first-child{border-left:3px solid rgba(var(--company-rgb),.8)}
:is(#fieldRoster,#overviewWorkerList) tr[data-fr-id] td:last-child{border-right:2px solid rgba(var(--company-rgb),.65)}
:is(#fieldRoster,#overviewWorkerList) .fr-company-start td{border-top:2px solid rgba(var(--company-rgb),.65)}
:is(#fieldRoster,#overviewWorkerList) .fr-company-end td{border-bottom:2px solid rgba(var(--company-rgb),.65)}
'''
p.write_text(s,encoding='utf-8')
