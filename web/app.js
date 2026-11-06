'use strict';
const $ = id => document.getElementById(id);
let network, map, routeLayers = [], markers = new Map(), activeLine = 'all', selected = null, requestId = 0;
const clock = new Intl.DateTimeFormat('en-GB', {timeZone:'Europe/Paris', hour:'2-digit', minute:'2-digit'});
const dateLabel = new Intl.DateTimeFormat('en-GB', {timeZone:'Europe/Paris', day:'numeric', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit'});
function el(tag, text, cls) { const node = document.createElement(tag); if(text !== undefined) node.textContent = text; if(cls) node.className = cls; return node; }
function route(id) { return network.routes.find(r => r.id === id); }
function key(stop) { return stop.line_id + stop.id; }
function badge(r) { const b = el('span', r.name, 'badge'); b.style.setProperty('--route-color', r.color); const rgb=r.color.slice(1).match(/../g).map(v=>parseInt(v,16)); b.style.color=(rgb[0]*.299+rgb[1]*.587+rgb[2]*.114)>150?'#172d30':'#fff'; return b; }
function clean(text) { return text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase(); }
function visibleStops() { const query = clean($('search').value.trim()); return network.stops.filter(s => (activeLine === 'all' || s.line_id === activeLine) && clean(s.name+' '+s.commune+' '+s.id).includes(query)); }
function updateFilters() {
  for(const button of $('line-filters').children) { const yes = button.dataset.line === activeLine; button.classList.toggle('active',yes); button.setAttribute('aria-pressed',String(yes)); }
}
function renderQuality() {
  const data = coverageSummary(network, activeLine);
  $('quality-scope').textContent = (activeLine === 'all' ? 'All métro lines' : 'Métro '+route(activeLine).name) + ' · follows the line filter above; stop searches do not change these totals.';
  const counts = $('quality-counts'); counts.replaceChildren();
  for(const [label, count] of [['Mapped records', data.mapped], ['Listed for live predictions', data.matched], ['Mapped, no coverage match', data.missingCoverage.length], ['Coverage-listed, not mapped', data.missingMap.length]]) {
    const card = el('div'); card.append(el('strong',String(count)),el('span',label));counts.append(card);
  }
  const gaps = $('quality-gaps'); gaps.replaceChildren();
  if(!data.missingCoverage.length && !data.missingMap.length) gaps.append(el('p','No identifier mismatches in this subset. This does not establish source accuracy.'));
  for(const stop of data.missingCoverage)gaps.append(el('p',`Métro ${route(stop.line_id).name} · ${stop.name} · ${stop.id}: mapped, but absent from the live-coverage reference. Predictions are unavailable through this app.`));
  for(const stop of data.missingMap)gaps.append(el('p',`Métro ${route(stop.line_id).name} · ${stop.name} · ${stop.monitoring_ref}: listed for live coverage, but no exact map-record match. No position is guessed.`));
  $('quality-date').textContent = 'Reference snapshot downloaded '+dateLabel.format(new Date(network.prepared_at))+' (Paris). This is a download time, not the publisher’s update time.';
}
function renderList() {
  renderQuality();
  const stops = visibleStops(); $('stop-list').replaceChildren(); $('result-count').textContent = `${stops.length} points`;
  for(const stop of stops) {
    const button = el('button',undefined,'stop-row'); button.classList.toggle('selected',selected && key(selected)===key(stop));
    button.setAttribute('aria-label',`${route(stop.line_id).mode} ${route(stop.line_id).name}, ${stop.name}, boarding point ${stop.id}`);
    button.setAttribute('aria-pressed',String(Boolean(selected && key(selected)===key(stop))));
    button.append(badge(route(stop.line_id))); const names = el('span',undefined,'names'); names.append(el('strong',stop.name),el('small',`${stop.commune} · ${stop.id.replace('IDFM:','Point ')}`)); button.append(names,el('span','↗','arrow')); button.addEventListener('click',()=>selectStop(stop)); $('stop-list').append(button);
  }
  if(!stops.length) $('stop-list').append(el('p','No boarding points match your search.','notice'));
  const shown = new Set(stops.map(key));
  if(map) for(const [id, marker] of markers) { if(shown.has(id)) marker.addTo(map); else marker.remove(); }
  if(map) for(const layer of routeLayers) { if(activeLine==='all'||layer.routeId===activeLine) layer.addTo(map); else layer.remove(); }
}
function fit() { if(!map)return; const stops=visibleStops(); if(stops.length) map.fitBounds(stops.map(s=>[s.lat,s.lon]),{padding:[35,35],maxZoom:14}); }
function selectStop(stop) {
  selected=stop; $('empty-detail').hidden=true; $('selected-detail').hidden=false;
  const r=route(stop.line_id); $('selected-line').textContent=`${r.mode} ${r.name} · NEXT REPORTED PASSAGES`; $('selected-name').textContent=stop.name; $('selected-platform').textContent=`${stop.id.replace('IDFM:','Boarding point ')} · ${stop.commune}`;
  if(map) { map.setView([stop.lat,stop.lon],Math.max(map.getZoom(),14),{animate:false}); for(const [id,m] of markers) m.setStyle({radius:id===key(stop)?9:4.5,weight:id===key(stop)?3:2,fillColor:id===key(stop)?route(stop.line_id).color:'#fff'}); }
  renderList(); loadDepartures();
}
async function loadDepartures() {
  if(!selected)return; const stop=selected, sequence=++requestId;
  $('departures').replaceChildren(); $('fetch-info').textContent=''; $('refresh').disabled=true;
  if(!stop.live_supported) { $('live-status').textContent='This point is not listed in the real-time coverage reference.'; $('refresh').disabled=false; return; }
  $('live-status').textContent='Requesting provider estimates…';
  try {
    const response=await fetch('/api/departures?'+new URLSearchParams({line:stop.line_id,stop:stop.monitoring_ref})); const data=await response.json(); if(sequence!==requestId)return; if(!response.ok)throw new Error(data.error||'Could not retrieve estimates.');
    $('live-status').textContent=data.cached?'CACHED RESPONSE · NO NEW API CALL':'LATEST REQUEST COMPLETE';
    if(!data.departures.length)$('departures').append(el('p','No future estimates were returned for this line.','notice'));
    for(const departure of data.departures.slice(0,6)) {
      const row=el('div',undefined,'departure'), info=el('div'); info.append(el('span',departure.destination,'destination'));
      const age=departure.recorded_at?Math.max(0,Math.floor((Date.now()-Date.parse(departure.recorded_at))/1000)):null;
      const ageText=age===null?'Source-record time unavailable':`Source record: ${age<60?age+'s':Math.floor(age/60)+'m'} ago${age>120?' · older record':''}`;
      info.append(el('span',ageText,'age'+(age>120?' older':'')));
      let label='Reported cancelled'; if(!departure.cancelled) { const seconds=(Date.parse(departure.expected_at)-Date.now())/1000; label=seconds<0?'Time passed':seconds<60?'<1 min':Math.ceil(seconds/60)+' min'; }
      const due=el('span',label,'due'); if(departure.expected_at)due.append(el('small',`${clock.format(new Date(departure.expected_at))} · estimated ${departure.kind}`)); row.append(info,due); $('departures').append(row);
    }
    let note=`Fetched ${clock.format(new Date(data.fetched_at))} Paris time. Cached for up to 2 minutes. Refresh to update countdowns.`;
    if(data.excluded_past||data.excluded_invalid)note+=` ${data.excluded_past} past and ${data.excluded_invalid} invalid-time entries omitted.`;
    $('fetch-info').textContent=note;
  } catch(error) { if(sequence===requestId) { $('live-status').textContent='ESTIMATES UNAVAILABLE'; $('departures').append(el('p',error.message,'notice')); } }
  finally { if(sequence===requestId)$('refresh').disabled=false; }
}
let trafficSequence = 0;
function providerDate(value) { return value ? value.replace('T',' ') + ' (Paris)' : 'not supplied'; }
async function loadTraffic(line) {
  const sequence = ++trafficSequence, panel = $('traffic-result');
  panel.replaceChildren(el('p', 'Checking published notices…'));
  for(const layer of routeLayers) layer.setStyle({dashArray:null,weight:3});
  try {
    const response = await fetch('/api/traffic?' + new URLSearchParams({line}));
    const data = await response.json();
    if(sequence !== trafficSequence)return;
    if(!response.ok)throw new Error(data.error || 'Traffic reports unavailable.');
    panel.replaceChildren();
    const r = route(line);
    panel.append(el('h3', `${r.mode} ${r.name} · ${data.reports.length} explicitly linked report(s)`));
    panel.append(el('p', `${data.cached?'Cached response':'New request'} · Fetched ${dateLabel.format(new Date(data.fetched_at))} Paris time · Cached up to 5 minutes.`, 'muted small'));
    if(!data.reports.length)panel.append(el('p', 'No directly linked reports returned. This is not confirmation of normal service.', 'notice'));
    for(const report of data.reports) {
      const card = el('article', undefined, 'traffic-card');
      card.append(el('p', `Provider status: ${report.status} · Effect: ${report.effect}`, 'eyebrow'));
      card.append(el('p', report.text));
      card.append(el('p', `Provider update: ${providerDate(report.updated_at_local)}`, 'muted small'));
      for(const period of report.periods_local)card.append(el('p', `Reported application period: ${providerDate(period.begin)} → ${providerDate(period.end)}`, 'muted small'));
      if(!report.periods_local.length)card.append(el('p','Application period not supplied.','muted small'));
      card.append(el('small', 'Report ID: '+report.id));panel.append(card);
    }
    panel.append(el('p', `${data.excluded_unlinked} other returned records excluded because no direct line link was found. Station/accessibility notices can be omitted by this conservative filter. Report periods are not measured incident durations.`, 'muted small'));
    if(data.reports.some(report=>report.status==='active'))for(const layer of routeLayers)if(layer.routeId===line)layer.setStyle({dashArray:'8 6',weight:5});
  } catch(error) { if(sequence===trafficSequence)panel.replaceChildren(el('p',error.message,'notice error')); }
}
async function init() {
  try {
    const response=await fetch('/api/network'); if(!response.ok)throw new Error('Network data could not be loaded.'); network=await response.json();
    $('point-count').textContent=network.stops.length;
    $('line-count').textContent=network.routes.length;
    for(const r of network.routes) { const option=el('option',r.name); option.value=r.id; $('traffic-line').append(option); }
    $('traffic-check').addEventListener('click',()=>loadTraffic($('traffic-line').value));
    for(const r of network.routes) { const button=el('button',undefined,'filter'); button.dataset.line=r.id;button.setAttribute('aria-pressed','false');button.setAttribute('aria-label','Métro '+r.name);button.append(badge(r));$('line-filters').append(button); }
    $('line-filters').addEventListener('click',event=>{const button=event.target.closest('button');if(!button)return;activeLine=button.dataset.line;if(activeLine!=='all')$('traffic-line').value=activeLine;selected=null;++requestId;$('empty-detail').hidden=false;$('selected-detail').hidden=true;for(const marker of markers.values())marker.setStyle({radius:4.5,weight:2,fillColor:'#fff'});updateFilters();renderList();fit();});
    $('search').addEventListener('input',renderList);$('refresh').addEventListener('click',loadDepartures);$('fit-map').addEventListener('click',fit);
    $('mapping-note').textContent=`${network.unmapped.length} coverage-listed boarding point${network.unmapped.length===1?' is':'s are'} not mapped because no exact coordinate-reference match was found.${network.unmapped.length?' '+network.unmapped.map(s=>s.name).join('; ')+'.':''} No substitute location is guessed. ${network.stops.filter(s=>!s.live_supported).length} mapped points are absent from the real-time coverage reference.`;
    $('snapshot-date').textContent=`Reference snapshot downloaded ${dateLabel.format(new Date(network.prepared_at))} (Paris). Download time is not the publisher’s update time. Run prepare_data.py to refresh it.`;
    for(const source of network.sources) { const link=el('a',source.dataset.replaceAll('-',' ')+' ↗');link.href=source.url;link.target='_blank';link.rel='noreferrer';$('source-links').append(link); }
    if(window.L) {
      map=L.map('map',{zoomControl:false}).setView([48.8566,2.3522],12); L.control.zoom({position:'topright'}).addTo(map);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · Routes/stops: Île-de-France Mobilités'}).on('tileerror',()=>{$('map-warning').hidden=false;$('map-warning').textContent='Street tiles are unavailable. Route geometries and boarding points remain usable.';}).addTo(map);
      for(const r of network.routes) {const layer=L.geoJSON(r.geometry,{style:{color:r.color,weight:3,opacity:.7},interactive:false});layer.routeId=r.id;routeLayers.push(layer);}
      for(const stop of network.stops) { const r=route(stop.line_id), marker=L.circleMarker([stop.lat,stop.lon],{radius:4.5,color:r.color,fillColor:'#fff',fillOpacity:1,weight:2});const label=el('span',`${r.mode} ${r.name} · ${stop.name} · ${stop.id}`);marker.bindTooltip(label);marker.on('click',()=>selectStop(stop));markers.set(key(stop),marker); }
    } else { $('map').textContent='Map library unavailable. You can still use the boarding-point list and estimates.'; }
    renderList();fit();
  } catch(error) { $('app-error').hidden=false;$('app-error').textContent=error.message;$('result-count').textContent='Network unavailable'; }
}
init();
