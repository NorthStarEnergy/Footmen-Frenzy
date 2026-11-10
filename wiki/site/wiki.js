(function () {
  'use strict';
  document.addEventListener('keydown', event => { if ((event.key === 'Enter' || event.key === ' ') && event.target.matches('.hero-row, .model-item-row')) { event.preventDefault(); event.target.click(); } });
  const D = window.FFWikiData || {};
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const num = value => value == null || value === '' ? '—' : typeof value === 'number' && Number.isFinite(value) ? Number(value.toFixed(3)) : value;
  const pct = value => { const n = Number(value); return Number.isFinite(n) ? `${(n * 100).toFixed(1)}%` : num(value); };
  const variants = D.unitVariants || {};
  let heroEdition = '799W';
  let unitEdition = Object.keys(variants)[0] || '799x';

  function go(page) {
    if (!document.getElementById(`page-${page}`)) page = 'home';
    $$('.page').forEach(el => el.classList.toggle('active', el.id === `page-${page}`));
    $$('.nav').forEach(el => el.classList.toggle('active', el.dataset.page === page));
    if (location.hash !== `#${page}`) history.replaceState(null, '', `#${page}`);
    const main = $('#content'); if (main) main.focus({preventScroll:true});
    window.scrollTo(0, 0);
  }
  $$('.nav').forEach(button => button.addEventListener('click', () => go(button.dataset.page)));
  $$('[data-open]').forEach(button => button.addEventListener('click', () => go(button.dataset.open)));

  const heroSelect = $('#hero-variant');
  if (heroSelect && D.heroVariants) {
    heroSelect.innerHTML = Object.keys(D.heroVariants).map(k => `<option value="${esc(k)}">${esc(D.heroVariants[k].label)}</option>`).join('');
    if (D.heroVariants['799W']) heroSelect.value = '799W';
    heroEdition = heroSelect.value;
    heroSelect.addEventListener('change', () => { heroEdition = heroSelect.value; $('#hero-detail').classList.add('hidden'); renderHeroes(); });
  }
  function currentHeroes() { return (D.heroVariants && D.heroVariants[heroEdition] && D.heroVariants[heroEdition].heroes) || []; }
  function heroValues(h) {
    const isLegacy = heroEdition === '799W';
    return {
      id: h.id || h.rawcode || '', name: h.name || '', category: isLegacy ? h.category : h.category,
      str: isLegacy ? h.str : h.STR_base, strInc: isLegacy ? h.strInc : h.STR_inc,
      agi: isLegacy ? h.agi : h.AGI_base, agiInc: isLegacy ? h.agiInc : h.AGI_inc,
      int: isLegacy ? h.int : h.INT_base, intInc: isLegacy ? h.intInc : h.INT_inc,
      move: isLegacy ? h.move : h.move_base, turn: isLegacy ? h.turn : h.turnrate, index: h.index,
      cardPath: isLegacy ? h.cardPath : '', wikiPath: isLegacy ? h.wikiPath : '',
      icon: isLegacy ? h.icon : '', iconSource: isLegacy ? h.iconSource : ''
    };
  }
  function decorateSpellHtml(html) {
    const icons = (D.icons799W && D.icons799W.abilities) || {};
    if (!Object.keys(icons).length) return html;
    const root = document.createElement('div');
    root.innerHTML = html;
    $$('h3', root).forEach(heading => {
      const abilityLine = heading.nextElementSibling;
      const match = abilityLine && abilityLine.textContent.match(/\bAbility\s+([A-Za-z0-9]{4})\b/i);
      const src = match && icons[match[1]];
      if (!src) return;
      const image = document.createElement('img');
      image.className = 'spell-icon';
      image.src = src;
      image.alt = `${heading.textContent.trim()} ability icon`;
      image.loading = 'lazy';
      heading.classList.add('icon-heading');
      heading.prepend(image);
    });
    return root.innerHTML;
  }
  function renderHeroes() {
    if (!$('#heroes-body')) return;
    $('#page-heroes > .eyebrow').textContent = D.heroVariants[heroEdition].label;
    const query = ($('#hero-search').value || '').trim().toLowerCase();
    const rows = currentHeroes().map(heroValues).filter(h => `${h.name} ${h.id} ${h.category}`.toLowerCase().includes(query));
    $('#heroes-body').innerHTML = rows.map(h => `<tr class="hero-row" tabindex="0" role="button" aria-label="View ${esc(h.name)}" data-hero-id="${esc(h.id)}"><td>${esc(h.index)}</td><td class="hero-art">${h.icon ? `<img src="${esc(h.icon)}" alt="${esc(h.name)} portrait" title="${esc(h.iconSource)}" loading="lazy">` : '<span class="muted">—</span>'}</td><td class="hero-name">${esc(h.name)}</td><td class="rawcode">${esc(h.id)}</td><td>${esc(h.category)}</td><td>${esc(num(h.str))}<span class="muted"> +${esc(num(h.strInc))}</span></td><td>${esc(num(h.agi))}<span class="muted"> +${esc(num(h.agiInc))}</span></td><td>${esc(num(h.int))}<span class="muted"> +${esc(num(h.intInc))}</span></td><td>${esc(num(h.move))}</td></tr>`).join('');
    $('#hero-count').textContent = `${rows.length} of ${currentHeroes().length} heroes`;
    const navCount = $('#nav-hero-count'); if (navCount) navCount.textContent = currentHeroes().length;
    $('#heroes-body').querySelectorAll('.hero-row').forEach(row => row.addEventListener('click', () => showHero(row.dataset.heroId)));
  }
  function showHero(id) {
    const raw = currentHeroes().find(x => String(x.id || x.rawcode) === id); if (!raw) return;
    const h = heroValues(raw); const panel = $('#hero-detail');
    const stats = `<div class="hero-metrics"><span class="pill">RAWCODE <b>${esc(h.id)}</b></span><span class="pill">CATEGORY <b>${esc(h.category)}</b></span><span class="pill">STR <b>${esc(h.str)} + ${esc(h.strInc)}</b></span><span class="pill">AGI <b>${esc(h.agi)} + ${esc(h.agiInc)}</b></span><span class="pill">INT <b>${esc(h.int)} + ${esc(h.intInc)}</b></span><span class="pill">MOVE <b>${esc(h.move)}</b></span><span class="pill">TURN <b>${esc(h.turn)}</b></span></div>`;
    const spellEntry = (D.spells || []).find(x => x.name === h.name);
    const spell = heroEdition === '799W' && spellEntry ? `<div class="spell-snippet">${decorateSpellHtml(spellEntry.html)}</div>` : `<p class="muted">No spell breakdown is included for this hero in the selected source set.</p>`;
    const cardLinks = [h.cardPath ? `<a class="source-link" href="${esc(h.cardPath)}" target="_blank" rel="noopener">Open recovered hero card ↗</a>` : '', h.wikiPath ? `<a class="source-link" href="${esc(h.wikiPath)}" target="_blank" rel="noopener">Open recovered wiki page ↗</a>` : ''].join('');
    const portrait = h.icon ? `<img class="hero-detail-icon" src="${esc(h.icon)}" alt="${esc(h.name)} portrait" title="${esc(h.iconSource)}">` : '';
    panel.innerHTML = `<div class="detail-top"><div class="hero-detail-title">${portrait}<div><div class="eyebrow">${esc(D.heroVariants[heroEdition].label)}</div><h3>${esc(h.name)}</h3></div></div><button class="close-detail" type="button">Close</button></div>${stats}${cardLinks}${spell}`;
    panel.classList.remove('hidden');
    panel.querySelector('.close-detail').addEventListener('click', () => panel.classList.add('hidden'));
    panel.scrollIntoView({behavior:'smooth', block:'nearest'});
  }
  $('#hero-search').addEventListener('input', renderHeroes);
  renderHeroes();

  const items = D.items || [], heroUsage = D.heroUsage || [];
  function renderItems() {
    const q = ($('#item-search').value || '').toLowerCase().trim();
    const rows = items.filter(x => `${x.item} ${x.price}`.toLowerCase().includes(q));
    $('#items-body').innerHTML = rows.map(x => `<tr><td class="hero-name">${esc(x.item)}</td><td>${esc(x.price)}</td><td>${esc(x.buyers)}</td><td>${esc(pct(x.share))}</td><td>${esc(pct(x['lvl 1-9']))}</td><td>${esc(pct(x['lvl 10-13']))}</td><td>${esc(pct(x['lvl 14-17']))}</td><td>${esc(pct(x['lvl 18 (max)']))}</td></tr>`).join('');
    $('#item-count').textContent = `${rows.length} of ${items.length} item rows`;
  }
  function renderHeroUsage() {
    const q = ($('#hero-usage-search').value || '').toLowerCase().trim();
    const rows = heroUsage.filter(x => `${x.hero} ${x.game} ${x.top}`.toLowerCase().includes(q));
    $('#hero-usage-body').innerHTML = rows.map(x => `<tr><td class="hero-name">${esc(x.hero)}</td><td>${esc(x.game)}</td><td>${esc(x.players)}</td><td>${esc(pct(x.bought_any))}</td><td style="white-space:normal;min-width:260px">${esc(x.top)}</td></tr>`).join('');
    $('#hero-usage-count').textContent = `${rows.length} rows`;
  }
  $('#item-search').addEventListener('input', renderItems); $('#hero-usage-search').addEventListener('input', renderHeroUsage);
  renderItems(); renderHeroUsage();

  const modelItems = (D.itemModel && D.itemModel.items) || [];
  function renderModelItems() {
    const q = ($('#model-item-search').value || '').toLowerCase().trim();
    const rows = modelItems.filter(x => `${x.name} ${x.id} ${x.category} ${x.summary}`.toLowerCase().includes(q));
    $('#model-items-body').innerHTML = rows.map(x => `<tr class="model-item-row" tabindex="0" role="button" aria-label="View ${esc(x.name)}" data-item-id="${esc(x.id)}"><td class="item-art">${x.icon ? `<img src="${esc(x.icon)}" alt="${esc(x.name)} icon" title="${esc(x.iconSource)}" loading="lazy">` : '<span class="muted">—</span>'}</td><td class="hero-name">${esc(x.name)}</td><td class="rawcode">${esc(x.id)}</td><td>${esc(x.category)}</td><td>${esc(num(x.cost))}</td><td>${esc(num(x.referenceGold))}</td><td>${x.coveragePercent == null ? '—' : `${esc(Number(x.coveragePercent).toFixed(1))}%`}</td></tr>`).join('');
    $('#model-item-count').textContent = `${rows.length} of ${modelItems.length} modeled items`;
    $('#model-items-body').querySelectorAll('.model-item-row').forEach(row => row.addEventListener('click', () => showModelItem(row.dataset.itemId)));
  }
  function showModelItem(id) {
    const x = modelItems.find(item => String(item.id) === id); if (!x) return;
    const panel = $('#model-item-detail');
    const terms = (x.terms || []).filter(t => t.label || t.gold != null);
    const termsHtml = terms.length ? `<h4>Modeled stat terms</h4><div class="table-wrap"><table><thead><tr><th>Effect</th><th>Quantity</th><th>Rate</th><th>Reference gold</th><th>Ability</th></tr></thead><tbody>${terms.map(t => `<tr><td>${esc(t.label)}</td><td>${esc(num(t.quantity))}</td><td>${esc(num(t.rate))}</td><td>${esc(num(t.gold))}</td><td class="rawcode">${esc(t.ability)}</td></tr>`).join('')}</tbody></table></div>` : '';
    const detail = (x.details || []).filter(Boolean).length ? `<ul>${x.details.filter(Boolean).map(v => `<li>${esc(v)}</li>`).join('')}</ul>` : '';
    const unpriced = (x.unpriced || []).filter(Boolean).length ? `<h4>Unpriced / interpretation notes</h4><ul>${x.unpriced.filter(Boolean).map(v => `<li>${esc(v)}</li>`).join('')}</ul>` : '';
    const icon = x.icon ? `<img class="item-detail-icon" src="${esc(x.icon)}" alt="${esc(x.name)} icon">` : '';
    const iconProvenance = x.iconSource ? `<p class="muted">Icon: ${esc(x.iconEdition)} · ${esc(x.iconSource)} · ${esc(x.iconEvidence)}</p>` : '';
    panel.innerHTML = `<div class="detail-top"><div class="item-detail-title">${icon}<div><div class="eyebrow">${esc(x.category)} · ${esc(x.id)} · ${esc(D.itemModel.source)}</div><h3>${esc(x.name)}</h3></div></div><button class="close-detail" type="button">Close</button></div><p>${esc(x.summary)}</p>${iconProvenance}<div class="hero-metrics"><span class="pill">COST <b>${esc(num(x.cost))}</b></span><span class="pill">CORE ESTIMATE <b>${esc(num(x.coreGold))}</b></span><span class="pill">REFERENCE ESTIMATE <b>${esc(num(x.referenceGold))}</b></span><span class="pill">COVERAGE <b>${x.coveragePercent == null ? '—' : `${esc(Number(x.coveragePercent).toFixed(1))}%`}</b></span></div>${termsHtml}${detail}${unpriced}`;
    panel.classList.remove('hidden');panel.querySelector('.close-detail').addEventListener('click',()=>panel.classList.add('hidden'));panel.scrollIntoView({behavior:'smooth',block:'nearest'});
  }
  $('#model-item-search').addEventListener('input', renderModelItems); renderModelItems();
  const shops = (D.shops && D.shops.shops) || [];
  if ($('#shop-method') && D.shops) $('#shop-method').textContent = `${D.shops.source}: ${D.shops.method}`;
  $('#shops-body').innerHTML = shops.map(x => `<tr><td class="hero-name">${esc(x.name)}</td><td class="rawcode">${esc(x.id)}</td><td>${x.reachable ? '<span class="good">Reachable</span>' : '<span class="bad">Not confirmed</span>'}</td><td>${esc(x.stockCount)}</td><td>${esc((x.invalidIds || []).join(', ') || '—')}</td></tr>`).join('');
  if ($('#recipe-audit-content') && D.recipeAuditHtml) $('#recipe-audit-content').innerHTML = D.recipeAuditHtml;

  const unitSelect = $('#unit-variant');
  if (unitSelect) {
    unitSelect.innerHTML = Object.keys(variants).map(k => `<option value="${esc(k)}">${esc(variants[k].label)}</option>`).join('');
    if (variants[unitEdition]) unitSelect.value = unitEdition;
    unitEdition = unitSelect.value;
    unitSelect.addEventListener('change', () => { unitEdition = unitSelect.value; renderUnits(); });
  }
  function renderUnits() {
    const data = variants[unitEdition] || {army:[]}, all = data.army || [];
    const q = ($('#unit-search').value || '').toLowerCase().trim();
    const rows = all.filter(x => `${x.name} ${x.id} ${x.base_name}`.toLowerCase().includes(q));
    const columns = [['index','#'],['name','Unit'],['id','Rawcode'],['HP','HP'],['armor','Armor'],['damage_min','Dmg min'],['damage_max','Dmg max'],['nominal_DPS','Nominal DPS'],['bounty_min','Bounty min'],['bounty_max','Bounty max'],['spawn_seconds','Spawn s'],['movement_speed','Move'],['abilities','Abilities']];
    $('#units-head').innerHTML = `<tr>${columns.map(c => `<th>${esc(c[1])}</th>`).join('')}</tr>`;
    $('#units-body').innerHTML = rows.map(x => `<tr>${columns.map(c => `<td class="${c[0]==='id'?'rawcode':''}">${esc(num(x[c[0]]))}</td>`).join('')}</tr>`).join('');
    $('#unit-count').textContent = `${rows.length} of ${all.length} configured spawns · ${esc(data.label)}`;
  }
  $('#unit-search').addEventListener('input', renderUnits); renderUnits();

  const spellRoot = $('#spell-articles');
  if (spellRoot) {
    spellRoot.innerHTML = (D.spells || []).map(x => `<details class="spell-article" data-search="${esc((x.name+' '+x.text).toLowerCase())}"><summary>${esc(x.name)}</summary><div class="spell-article-content">${decorateSpellHtml(x.html)}</div></details>`).join('');
    $('#spell-search').addEventListener('input', e => { const q=e.target.value.toLowerCase().trim(); $$('.spell-article', spellRoot).forEach(a => {a.hidden=!a.dataset.search.includes(q); if(q) a.open=!a.hidden;}); });
  }

  const guides = D.guides || [];
  $('#guide-list').innerHTML = guides.map(g => `<article class="guide-card"><a href="${esc(g.path)}" target="_blank" rel="noopener">${esc(g.title)} ↗</a><p>${esc(g.description)} · ${esc(g.edition)}</p><details><summary>Read in wiki</summary><div class="guide-content">${g.html}</div></details></article>`).join('');
  const sources = D.sources || [];
  $('#source-list').innerHTML = sources.map(s => `<article class="source-card"><span class="tag">${esc(s.edition)}</span><strong>${esc(s.title)}</strong><p>${esc(s.description)}</p><a href="${esc(s.path)}" target="_blank" rel="noopener">Open source ↗</a></article>`).join('');

  const dataCounts = [
    [currentHeroes().length,'heroes in selected roster'],[items.length,'item observation rows'],
    [variants['799x'] ? variants['799x'].army.length : 0,'799X configured spawn entries'],
    [(D.spells || []).length,'heroes with spell notes']
  ];
  $('#overview-stats').innerHTML = dataCounts.map(x => `<div class="stat-card"><b>${esc(x[0])}</b><span>${esc(x[1])}</span></div>`).join('');
  $('#build-stamp').textContent = D.generated ? `DATA BUILD ${D.generated}` : '';
  window.addEventListener('hashchange', () => go(location.hash.slice(1) || 'home'));
  go(location.hash.slice(1) || 'home');
}());
