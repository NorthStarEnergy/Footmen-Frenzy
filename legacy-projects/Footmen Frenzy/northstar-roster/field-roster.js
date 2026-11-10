/* Compact field roster; records and actions use the existing check-in service. */
(() => {
  'use strict';
  const section = document.querySelector('#crew');
  if (!section) return;
  section.querySelector(':scope > .panel').dataset.moduleId ||= 'crew-module-0';
  const root = document.createElement('article');
  root.id = 'fieldRoster'; root.className = 'panel field-roster'; root.dataset.moduleId = 'field-roster';
  section.append(root);
  const mounted = new WeakMap(), referenceRoot = root;
  function mount(root, {mirrorAppearance=true,compact=false}={}) {
  if(mounted.has(root))return mounted.get(root);
  root.classList.add('field-roster');
  const overview = root.id === 'overviewWorkerList';
  root.setAttribute('aria-label', 'Active Workers');
  root.innerHTML = `<div class="fr-toolbar"><h2>Active Workers</h2><input type="search" aria-label="Find person or company" placeholder="Find person / company"><select aria-label="Station"><option value="">All stations</option></select><select aria-label="Presence"><option value="active">In the field</option><option value="all">All visits</option><option value="out">Checked out</option></select><button type="button" data-fr-refresh>Refresh</button><button type="button" data-fr-add>Add person</button><details class="fr-columns"><summary>Columns</summary><div></div></details><span role="status">Loading…</span></div><div class="fr-scroll"><table aria-label="People by station"><thead><tr><th scope="col">Person</th><th scope="col" data-fr-col="company">Company</th><th scope="col" data-fr-col="in">Time in</th><th scope="col" data-fr-col="out">Time out</th><th scope="col" data-fr-col="seen">Last seen</th><th scope="col" data-fr-col="status">Status</th><th scope="col">Actions</th></tr></thead><tbody></tbody></table></div>`;
  if(compact)root.querySelector('thead').innerHTML='<tr><th scope="col">Person</th><th scope="col" data-fr-col="company">Company</th><th scope="col">Station</th><th scope="col" data-fr-col="in">Time in</th><th scope="col" data-fr-col="seen">Last seen</th><th scope="col" data-fr-col="status">Status</th></tr>';
  const $ = s => root.querySelector(s), esc = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const search = $('input[type=search]'), station = $('select[aria-label=Station]'), presence = $('select[aria-label=Presence]'), status = $('[role=status]');
  const stamp = (v, row) => {
    if (!v || !Number.isFinite(Date.parse(v))) return '—';
    const date = new Date(v);
    if (!overview) return date.toLocaleString([], compact?{hour:'2-digit',minute:'2-digit',hourCycle:'h23'}:{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});
    const start = new Date(row.checkedIn), end = row.status === 'checked-out' ? new Date(row.checkedOutAt) : new Date();
    const overnight = Number.isFinite(start.getTime()) && Number.isFinite(end.getTime()) && start.toDateString() !== end.toDateString();
    const time = date.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
    return (overnight ? `${String(date.getMonth()+1).padStart(2,'0')}/${String(date.getDate()).padStart(2,'0')} ` : '') + time;
  };
  const siteOf = r => /iroquois.*(?:230|\bHV\b|\bTS\b)/i.test(String(r.siteId || '')+' '+String(r.site || '')) ? (window.NorthStarSites?.resolve('site:iroquois-falls-230-kv') || {id:'site:iroquois-falls-230-kv',name:'Iroquois Falls 230 kV'}) : window.NorthStarSites?.resolve(r.siteId) || window.NorthStarSites?.resolve(r.site) || {id:r.siteId || r.site || 'unknown',name:r.site || 'Unassigned'};
  let rows = [], failed = false, loading = false;
  const busy = new Set(), hidden = new Set();
  try { for (const col of JSON.parse(localStorage.getItem('northstarFieldRosterColumnsV1') || '[]')) hidden.add(col); } catch {}
  for (const [key,title] of Object.entries({company:'Company',in:'Time in',out:'Time out',seen:'Last seen',status:'Status'})) {
    if(compact&&key==='out')continue;
    const label=document.createElement('label'); label.innerHTML=`<input type="checkbox" ${hidden.has(key)?'':'checked'} value="${key}">${title}`;
    label.querySelector('input').onchange=event=>{event.target.checked?hidden.delete(key):hidden.add(key);try{localStorage.setItem('northstarFieldRosterColumnsV1',JSON.stringify([...hidden]));}catch{}render();};
    $('.fr-columns > div').append(label);
  }
  function stations() {
    const map = new Map((window.NorthStarSites?.stations() || []).map(s=>[s.id,s]));
    rows.forEach(r=>{const s=siteOf(r);map.set(s.id,s);});
    return [...map.values()];
  }
  function syncAppearance() {
    if(root===referenceRoot || !mirrorAppearance)return;
    const style=getComputedStyle(referenceRoot);
    for(const name of ['--panel','--panel2','--line','--text','--muted','--blue','--gold'])root.style.setProperty(name,style.getPropertyValue(name));
    for(const name of ['background-color','color','padding'])root.style.setProperty(name,style.getPropertyValue(name),'important');
    const heading=getComputedStyle(referenceRoot.querySelector('.fr-toolbar h2'));
    for(const name of ['font','margin','letter-spacing','color'])$('.fr-toolbar h2').style.setProperty(name,heading.getPropertyValue(name),'important');
    root.parentElement.style.setProperty('--ns-roster-background',style.backgroundColor);
    root.parentElement.style.setProperty('--ns-roster-border',style.borderColor);
  }
  if(root!==referenceRoot && mirrorAppearance){
    const appearance=new MutationObserver(syncAppearance);
    appearance.observe(referenceRoot,{attributes:true,attributeFilter:['style','class','data-ns-theme']});
    appearance.observe(document.body,{attributes:true,attributeFilter:['class','data-ui-style']});
  }
  const companyOf = r => String(r.company || (r.kind==='Contractor'?'Contractor':'NorthStar')).trim();
  const companyKey = r => {
    const key=companyOf(r).toLowerCase().replace(/[^a-z0-9]/g,'');
    return ['northstar','northstarenergy'].includes(key)?'northstar':key;
  };
  const companyTone = r => companyKey(r)==='northstar'?0:1+[...companyKey(r)].reduce((h,c)=>(h*31+c.charCodeAt(0))>>>0,0)%5;
  function render() {
    syncAppearance();
    const focusId = document.activeElement?.closest('[data-fr-id]')?.dataset.frId;
    const focusAction = document.activeElement?.dataset.frAction;
    const selected=station.value, sites=stations();
    station.innerHTML='<option value="">All stations</option>'+sites.map(s=>`<option value="${esc(s.id)}">${esc(s.name)}</option>`).join(''); station.value=selected;
    const query=search.value.trim().toLowerCase(); let count=0;
    let layout=window.NorthStarWorkerSiteGroups || [];
    if(!layout.length)try { layout=JSON.parse(document.querySelector('#nsStatusWorkers')?.dataset.stationGroups || '[]'); } catch {}
    const siteKey = s => window.NorthStarSites?.resolve(s.id)?.id || window.NorthStarSites?.resolve(s.name)?.id || s.id;
    const layoutIds=layout.map(names=>names.map(name=>window.NorthStarSites?.resolve(name)?.id || name));
    const groupOf = s => {const i=layoutIds.findIndex(ids=>ids.includes(siteKey(s)));return i<0?layout.length:i;};
    const selectedSites=sites.filter(s=>!station.value || s.id===station.value).sort((a,b)=>groupOf(a)-groupOf(b) || (layoutIds[groupOf(a)]?.indexOf(siteKey(a))??0)-(layoutIds[groupOf(b)]?.indexOf(siteKey(b))??0) || a.name.localeCompare(b.name));
    let previousArea=-1;
    $('tbody').innerHTML=selectedSites.map(s=>{
      const people=rows.filter(r=>siteOf(r).id===s.id && (presence.value==='all' || (presence.value==='out')===(r.status==='checked-out')) && `${r.name} ${r.company || ''}`.toLowerCase().includes(query)).sort((a,b)=>Number(companyKey(b)==='northstar')-Number(companyKey(a)==='northstar') || companyKey(a).localeCompare(companyKey(b)) || Number(Boolean(b.alone))-Number(Boolean(a.alone)) || a.name.localeCompare(b.name));
      if (!people.length) return '';
      count+=people.length;
      const area=groupOf(s), areaStart=area!==previousArea;
      previousArea=area;
      const areaHeading=!compact && layout.length && areaStart ? `<tr class="fr-area"><th colspan="7" scope="rowgroup">${esc(layout[area]?.join(' · ') || 'Other sites')}</th></tr>` : '';
      return areaHeading+(compact?'':`<tr class="fr-station"><th colspan="7" scope="rowgroup">${esc(s.name)} <span>${people.length}</span></th></tr>`)+ (people.map((r,index)=>{
        const out=r.status==='checked-out', provisional=r.status==='provisional', contact=String(r.notes || '').startsWith('[Crew contact]');
        const company=companyOf(r);
        const key=companyKey(r), first=index===0 || companyKey(people[index-1])!==key, last=index===people.length-1 || companyKey(people[index+1])!==key;
        const companyClass=`fr-company-${companyTone(r)}${first?' fr-company-start':''}${last?' fr-company-end':''}`;
        const state=r.needsHelp?'Needs help':out?'Checked out':provisional?'Pending review':r.overdue || r.status==='overdue'?'Overdue':r.alone?'Working alone':'On site';
        if(compact)return `<tr data-fr-id="${esc(r.id)}" class="${companyClass} ${r.needsHelp?'fr-help':r.overdue?'fr-overdue':''}"><td><button type="button" class="fr-person" data-fr-action="profile" title="Open person details">${esc(r.name)}${overview && r.alone ? ' <strong class="fr-alone">Alone</strong>' : ''}</button></td><td data-fr-col="company" title="${esc(company)}">${esc(company)}</td><td title="${esc(s.name)}">${esc(s.name)}</td><td data-fr-col="in" title="${esc(r.checkedIn)}">${esc(stamp(r.checkedIn,r))}</td><td data-fr-col="seen" title="${esc(r.lastHeard)}">${esc(stamp(r.lastHeard,r))}</td><td data-fr-col="status" title="${esc(state)}" data-presence="${r.needsHelp?'help':r.overdue||r.status==='overdue'?'overdue':out?'out':provisional?'pending':'active'}">${state}</td></tr>`;
        return `<tr data-fr-id="${esc(r.id)}" class="${companyClass} ${r.needsHelp?'fr-help':r.overdue?'fr-overdue':''}"><td><button type="button" class="fr-person" data-fr-action="profile" title="Open person details">${esc(r.name)}${overview && r.alone ? ' <strong class="fr-alone">Alone</strong>' : ''}${contact?` <span>— ${esc(company)} · crew contact</span>`:''}</button></td><td data-fr-col="company" title="${esc(company)}">${esc(company)}</td><td data-fr-col="in">${esc(stamp(r.checkedIn,r))}</td><td data-fr-col="out">${esc(stamp(r.checkedOutAt,r))}</td><td data-fr-col="seen">${esc(stamp(r.lastHeard,r))}</td><td data-fr-col="status">${state}</td><td class="fr-actions">${out?'<button type="button" data-fr-action="return">Check in</button>':provisional?'<button type="button" data-fr-action="accept">Accept</button><button type="button" data-fr-action="reject">Reject</button>':'<button type="button" data-fr-action="in">Check in</button><button type="button" data-fr-action="out">Check out</button>'}</td></tr>`;
      }).join('') || '<tr><td colspan="'+(compact?6:7)+'" class="fr-empty">No matching people</td></tr>');
    }).join('') || '<tr><td colspan="'+(compact?6:7)+'" class="fr-empty">No matching people</td></tr>';
    root.querySelectorAll('[data-fr-col]').forEach(el=>el.hidden=hidden.has(el.dataset.frCol));
    root.querySelectorAll('[data-fr-id]').forEach(el=>el.querySelectorAll('.fr-actions button').forEach(b=>b.disabled=failed || loading || busy.has(el.dataset.frId)));
    if(focusId)root.querySelector(`[data-fr-id="${CSS.escape(focusId)}"] [data-fr-action="${CSS.escape(focusAction || 'profile')}"]`)?.focus({preventScroll:true});
    if(!failed)status.textContent=loading?'Refreshing…':`${count} people`;
  }
  async function refresh() {
    if(loading)return; loading=true; render();
    try {
      await window.northstarOperatorSession;
      const response=await fetch('/api/checkins?include=all&ts='+Date.now(),{cache:'no-store'});
      if(!response.ok)throw Error('Roster unavailable. Refresh to retry.');
      const data=await response.json(); if(!Array.isArray(data))throw Error('Invalid roster response.');
      rows=data; failed=false;window.dispatchEvent(new CustomEvent('northstar:field-roster-data',{detail:rows}));
    } catch(error) {failed=true;status.textContent=error.message+' Displayed records may be stale.';}
    finally {loading=false;render();}
  }
  function add(row) {
    const site = row ? siteOf(row).name : stations().find(s=>s.id===station.value)?.name;
    if(!site){status.textContent='Select a station to add a person.';station.focus();return;}
    window.NorthstarWorkerDetails?.signIn(site);
    if(row) {document.querySelector('#siteWorkerName').value=row.name;document.querySelector('#siteWorkerKind').value=row.kind;document.querySelector('#siteWorkerCompany').value=row.company || '';}
  }
  root.addEventListener('click',async event=>{
    const button=event.target.closest('[data-fr-action]'), tr=button?.closest('[data-fr-id]');if(!tr)return;
    const row=rows.find(r=>String(r.id)===tr.dataset.frId), action=button.dataset.frAction;if(!row)return;
    if(action==='profile'){window.NorthstarWorkerDetails?.openProfile(row.id,button);return;}
    if(action==='return'){add(row);return;}
    if(busy.has(row.id))return;
    if(action==='reject'&&!confirm('Reject this provisional check-in? Its history is retained.'))return;
    busy.add(row.id);render();
    try {
      const path='/api/checkins/'+encodeURIComponent(row.id)+(action==='in'?'/heartbeat':['accept','reject'].includes(action)?'/provisional':'');
      const response=await fetch(path,{method:action==='out'?'DELETE':'POST',headers:{'Content-Type':'application/json'},...(action==='out'?{}:{body:JSON.stringify(action==='in'?{}:{accept:action==='accept'})})});
      if(!response.ok)throw Error('Action failed. No change confirmed; refresh and retry.');
      await refresh();window.loadStaff?.();
    } catch(error) {status.textContent=error.message;}
    finally {busy.delete(row.id);tr.querySelectorAll('button').forEach(b=>b.disabled=false);root.querySelectorAll(`[data-fr-id="${CSS.escape(String(row.id))}"] .fr-actions button`).forEach(b=>b.disabled=failed);}
  });
  root.addEventListener('dblclick',event=>{if(event.target.closest('button,input,select'))return;const tr=event.target.closest('[data-fr-id]');if(tr)window.NorthstarWorkerDetails?.openProfile(tr.dataset.frId,tr.querySelector('.fr-person'));});
  search.oninput=render;station.onchange=render;presence.onchange=render;
  $('[data-fr-refresh]').onclick=refresh;$('[data-fr-add]').onclick=()=>add();
  window.addEventListener('northstar:field-roster-data',event=>{rows=event.detail;failed=false;render();});
  window.addEventListener('northstar:sites-display-change',render);
  window.addEventListener('northstar:worker-site-groups',render);
  document.querySelector('#siteWorkerDialog')?.addEventListener('close',refresh);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden&&root.getClientRects().length)refresh();});
  setInterval(()=>{if(!document.hidden&&root.getClientRects().length)refresh();},30000);
  Promise.resolve(window.NorthStarSites?.ready).then(()=>{window.NorthstarModules?.refresh();refresh();});
  const view={refresh};mounted.set(root,view);return view;
  }
  window.NorthstarFieldRoster={mount};
  mount(root);
})();
