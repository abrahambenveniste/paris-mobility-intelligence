'use strict';
const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const clean=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
let network,groups,map,revision=0,journeyLayer=null,baseLayer=null,mobilityLayer=null,activeView='journey',journeyView=null;
const parisTime=value=>new Date(value).toLocaleString('en-GB',{timeZone:'Europe/Paris',dateStyle:'medium',timeStyle:'short'});
const minutes=value=>Math.ceil((value||0)/60);
function stationKey(g){const p=g.stops[0];return p.id+'|'+p.line_id;}
function clearJourney(){if(journeyLayer){journeyLayer.remove();journeyLayer=null;}$('map-selection').textContent='Reference routes, not live train positions';}
function drawJourney(journey,index){
  clearJourney();
  for(const button of document.querySelectorAll('.show-on-map'))button.setAttribute('aria-pressed',String(button.dataset.index===String(index)));
  if(!map||!window.L)return;
  journeyLayer=L.layerGroup();if(activeView==='journey')journeyLayer.addTo(map);const bounds=L.latLngBounds([]);let drawn=0,missing=0;
  for(const section of journey.sections){
    const geometry=section.geometry;
    if(!geometry){if(['public_transport','street_network','crow_fly'].includes(section.kind))missing++;continue;}
    const points=geometry.coordinates.map(([lon,lat])=>[lat,lon]);
    if(points.length<2)continue;
    const route=network.routes.find(r=>section.line_id==='line:IDFM:'+r.id.split('::')[1].replace(':',''));
    const colour=section.kind==='public_transport'?(route?.color||'#17584c'):'#455a54';
    L.polyline(points,{color:'#fff',weight:10,opacity:.95,interactive:false}).addTo(journeyLayer);
    L.polyline(points,{color:colour,weight:6,opacity:1,dashArray:section.kind==='public_transport'?null:'6 7',interactive:false}).addTo(journeyLayer);
    for(const point of points)bounds.extend(point);drawn++;
  }
  if(drawn){if(activeView==='journey')map.fitBounds(bounds,{padding:[35,35],maxZoom:15});$('map-selection').textContent=`Option ${index+1} · ${missing?'some path data unavailable':'publisher-supplied route'}`;}
  else $('map-selection').textContent=`Option ${index+1} · path data unavailable`;
}

function fillNotice(panel,data){
  panel.replaceChildren();
  panel.append(el('p',`${data.cached?'Cached':'Checked'} ${parisTime(data.fetched_at)} · line-level reports`, 'notice-meta'));
  if(!data.reports.length){panel.append(el('p','No directly linked notices returned. This does not confirm normal service.','notice-empty'));return;}
  for(const report of data.reports){
    const card=el('div',undefined,'route-alert');
    const status=report.status==='active'?'Reported active':report.status==='future'?'Reported upcoming':`Status: ${report.status||'not supplied'}`;
    card.append(el('strong',status),el('p',report.text));
    for(const period of report.periods_local||[]){
      if(!period.begin&&!period.end)continue;
      const duration=Date.parse(period.end)-Date.parse(period.begin);
      if(Number.isFinite(duration)&&duration>=0&&duration<60000)card.append(el('p','Source timing is unusually short; check official updates.','notice-meta'));
      else card.append(el('p',`Reported: ${(period.begin||'unknown').replace('T',' ')} – ${(period.end||'unknown').replace('T',' ')} (Paris time)`, 'notice-meta'));
    }
    panel.append(card);
  }
  panel.append(el('p','A line notice may not affect this particular journey.', 'notice-meta'));
}

async function loadNotices(linePanels,requestRevision){
  for(const [lineId,panels] of linePanels){
    // Share the existing one-per-second quota guard with the journey request.
    await new Promise(resolve=>setTimeout(resolve,1200));
    if(requestRevision!==revision)return;
    try{
      const response=await fetch('/api/traffic?'+new URLSearchParams({line:lineId}));
      const data=await response.json();if(!response.ok)throw Error('Notices unavailable.');
      if(requestRevision!==revision)return;
      for(const panel of panels)fillNotice(panel,data);
    }catch(_){if(requestRevision!==revision)return;for(const panel of panels)panel.replaceChildren(el('p','Line notices unavailable. Check official updates.','notice-unavailable'));}
  }
}

function showRoutes(data,out,current){
  out.replaceChildren();
  out.append(el('p',`${data.cached?'Cached':'Requested'} ${parisTime(data.fetched_at)} · Paris time`,'result-time'));
  if(!data.journeys.length){out.append(el('p',data.message||'No routes were returned.','notice'));return;}
  const heading=el('div',undefined,'results-heading');heading.append(el('h3','Your route options'),el('span',`${data.journeys.length} found`));out.append(heading);
  const linePanels=new Map();
  for(const [index,j] of data.journeys.entries()){
    const card=el('article',undefined,'route-card');
    const top=el('div',undefined,'route-card-top');top.append(el('span',`OPTION ${index+1}`,'route-kicker'),el('strong',`${minutes(j.duration)} min`,'route-duration'));card.append(top);
    const show=el('button','Show on map','show-on-map');show.type='button';show.dataset.index=String(index);show.setAttribute('aria-pressed','false');show.addEventListener('click',()=>{drawJourney(j,index);if(window.matchMedia('(max-width: 850px)').matches)$('map').scrollIntoView({block:'center'});});card.append(show);
    if(j.sections.some(s=>['public_transport','street_network','crow_fly'].includes(s.kind)&&!s.geometry))card.append(el('p','Some path details are unavailable, so the map may be incomplete.','notice-unavailable'));
    const strip=el('div',undefined,'route-strip');
    for(const s of j.sections){
      if(s.kind==='public_transport'){
        const route=network.routes.find(r=>s.line_id==='line:IDFM:'+r.id.split('::')[1].replace(':',''));
        const chip=el('span',s.line||'?','route-chip');if(route)chip.style.setProperty('--route-color',route.color);strip.append(chip);
      }else if(s.kind==='street_network'||s.kind==='crow_fly')strip.append(el('span','Walk','walk-chip'));
    }
    card.append(strip);
    const steps=el('div',undefined,'route-steps');
    for(const s of j.sections){
      const step=el('div',undefined,'route-step');
      if(s.kind==='public_transport'){
        step.append(el('strong',`Métro ${s.line||'?'} · towards ${s.direction||'destination unavailable'}`));
        step.append(el('p',`${s.from||'Start unavailable'} → ${s.to||'End unavailable'}`));
        step.append(el('p',s.freshness==='realtime'?'Real-time data':s.freshness==='base_schedule'?'Scheduled data':`Data freshness: ${s.freshness||'unknown'}`,'step-meta'));
        const lineId=(s.line_id||'').replace(/^line:IDFM:(C\d+)$/,'STIF:Line::$1:');
        const notice=el('div',undefined,'route-notices');notice.append(el('p','Checking line notices…','notice-meta'));step.append(notice);
        if(network.routes.some(r=>r.id===lineId)){if(!linePanels.has(lineId))linePanels.set(lineId,[]);linePanels.get(lineId).push(notice);}
        else notice.replaceChildren(el('p','Line notices unavailable for this route.','notice-unavailable'));
      }else if(s.kind==='waiting')step.append(el('strong',`Wait · ${minutes(s.duration)} min`));
      else{step.append(el('strong',`${s.kind==='transfer'?'Transfer':'Walk'} · ${minutes(s.duration)} min`));step.append(el('p',`${s.from||'Start unavailable'} → ${s.to||'End unavailable'}`));}
      steps.append(step);
    }
    card.append(steps);out.append(card);
  }
  if(data.journeys.length)drawJourney(data.journeys[0],0);
  loadNotices(linePanels,current);
}

function setupJourneys(){
  const labels=new Map(),names=new Map();
  for(const g of groups){const key=stationKey(g),label=`${g.name} · ${g.commune}`;labels.set(clean(label),key);const name=clean(g.name);names.set(name,names.has(name)?null:key);const option=el('option');option.value=label;$('journey-stations').append(option);}
  function changed(){revision++;$('journey-results').replaceChildren();clearJourney();}
  for(const id of ['journey-from','journey-to'])$(id).addEventListener('input',changed);
  $('journey-swap').addEventListener('click',()=>{const from=$('journey-from'),to=$('journey-to');[from.value,to.value]=[to.value,from.value];changed();});
  $('journey-form').addEventListener('submit',async event=>{
    event.preventDefault();const out=$('journey-results'),button=$('journey-submit');
    const start=clean($('journey-from').value.trim()),end=clean($('journey-to').value.trim());
    const from=labels.get(start)||names.get(start),to=labels.get(end)||names.get(end),current=++revision;
    if(!from||!to){out.replaceChildren(el('p','Choose a station from the suggestions for both fields.','notice'));return;}
    if(from===to){out.replaceChildren(el('p','Choose two different stations.','notice'));return;}
    button.disabled=true;clearJourney();out.replaceChildren(el('p','Finding routes…','result-loading'));
    try{
      const response=await fetch('/api/journeys?'+new URLSearchParams({from,to})),data=await response.json();
      if(current!==revision)return;if(!response.ok)throw Error(data.error||'Routes are unavailable.');showRoutes(data,out,current);
    }catch(error){if(current===revision)out.replaceChildren(el('p',error.message,'notice'));}finally{button.disabled=false;}
  });
}

function setupMobility(){
  const places={A:null,B:null};let choosing=null,pointLayer=null;
  const colours={A:'#24584c',B:'#bb683e'};
  function render(){
    const out=$('point-results');out.replaceChildren();
    if(pointLayer)pointLayer.remove();if(map)pointLayer=L.layerGroup().addTo(map);
    for(const key of ['A','B']){
      const place=places[key];if(!place)continue;
      const result=place.result,card=el('section',undefined,'location-card');
      card.append(el('h3',`Location ${key}`),el('strong',`${result.score} / 100 · métro proximity`,'point-score'));
      card.append(el('p',`${result.nearest===null?'No mapped station within 500 m':`Nearest mapped point: ${Math.round(result.nearest)} m`} · ${result.lines.size} distinct métro lines`));
      if(result.stations.length){const list=el('ul',undefined,'nearby-list');for(const station of result.stations){const names=[...station.lines].map(id=>network.routes.find(r=>r.id===id)?.name||id);const item=el('li');item.append(el('strong',station.name),el('span',`${Math.round(station.distance)} m · line${names.length===1?'':'s'} ${names.join(', ')}`));list.append(item);}card.append(list);}
      out.append(card);
      if(pointLayer){L.circle(place.latlng,{radius:500,color:colours[key],weight:2,fillOpacity:.07,interactive:false}).addTo(pointLayer);L.marker(place.latlng,{interactive:false,icon:L.divIcon({className:`location-marker location-${key.toLowerCase()}`,html:key,iconSize:[30,30]})}).addTo(pointLayer);}
    }
  }
  function choose(key){choosing=key;for(const k of ['A','B'])$(`pick-${k.toLowerCase()}`).setAttribute('aria-pressed',String(k===key));$('pick-instruction').textContent=`Click the map to set location ${key}.`;if(window.innerWidth<=850)$('map').scrollIntoView({behavior:'smooth',block:'center'});}
  $('pick-a').addEventListener('click',()=>choose('A'));$('pick-b').addEventListener('click',()=>choose('B'));
  if(map)map.on('click',e=>{if(activeView!=='mobility'||!choosing)return;const key=choosing;places[key]={latlng:e.latlng,result:nearbyMobility(e.latlng.lat,e.latlng.lng,network.stops)};choosing=null;for(const k of ['A','B'])$(`pick-${k.toLowerCase()}`).setAttribute('aria-pressed','false');$('pick-instruction').textContent=`Location ${key} selected. Choose a location to change or compare.`;render();});
  function view(mode){
    if(mode===activeView)return;activeView=mode;const isMobility=mode==='mobility';$('journey-panel').hidden=isMobility;$('mobility-panel').hidden=!isMobility;
    $('view-journey').setAttribute('aria-pressed',String(!isMobility));$('view-mobility').setAttribute('aria-pressed',String(isMobility));
    $('map-legend').textContent=isMobility?'Compare locations · 500 m radius':'Métro network · dashed = walking';$('map-selection').textContent=isMobility?'Reference points, not walking routes':'Reference routes, not live train positions';
    if(!map)return;if(isMobility){journeyView={center:map.getCenter(),zoom:map.getZoom()};if(journeyLayer)journeyLayer.remove();if(pointLayer)pointLayer.addTo(map);}
    else{if(pointLayer)pointLayer.remove();if(journeyLayer)journeyLayer.addTo(map);if(journeyView)map.setView(journeyView.center,journeyView.zoom);}
  }
  $('view-journey').addEventListener('click',()=>view('journey'));$('view-mobility').addEventListener('click',()=>view('mobility'));
  $('fit-map').addEventListener('click',()=>{if(activeView==='mobility'&&map)map.fitBounds(network.stops.map(s=>[s.lat,s.lon]),{padding:[30,30],maxZoom:14});});
}

async function init(){
  try{
    const response=await fetch('/api/network');if(!response.ok)throw Error('Network data could not be loaded.');network=await response.json();groups=stationGroups(network.stops);
    let live=false;try{const features=await fetch('/api/features');live=features.ok&&(await features.json()).live===true;}catch(_){}
    $('journey-submit').disabled=!live;
    if(live)$('preview-notice').textContent='Public preview · Routes and line notices are requested when you search. Information can be incomplete; check official updates.';
    setupJourneys();$('point-count').textContent=network.stops.length;$('line-count').textContent=network.routes.length;
    $('snapshot-date').textContent=`Reference map downloaded ${parisTime(network.prepared_at)} (Paris time); it is not a live vehicle map.`;
    if(window.L){
      map=L.map('map',{zoomControl:false}).setView([48.8566,2.3522],12);L.control.zoom({position:'topright'}).addTo(map);new ResizeObserver(()=>map.invalidateSize({pan:false})).observe($('map'));
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · Routes/stops: Île-de-France Mobilités'}).on('tileerror',()=>{$('map-warning').hidden=false;$('map-warning').textContent='Street tiles are unavailable.';}).addTo(map);
      baseLayer=L.layerGroup().addTo(map);
      for(const r of network.routes)L.geoJSON(r.geometry,{style:{color:r.color,weight:3,opacity:.72},interactive:false}).addTo(baseLayer);
      for(const stop of network.stops){const r=network.routes.find(x=>x.id===stop.line_id);L.circleMarker([stop.lat,stop.lon],{radius:4,color:r.color,fillColor:'#fff',fillOpacity:1,weight:2}).bindTooltip(el('span',`Métro ${r.name} · ${stop.name}`)).addTo(baseLayer);}
      const points=network.stops.map(s=>[s.lat,s.lon]);const fit=()=>{if(activeView==='journey')map.fitBounds(points,{padding:[30,30],maxZoom:14});};$('fit-map').addEventListener('click',fit);fit();
    }else $('map').textContent='Map library unavailable; journey search remains available.';
    setupMobility();
  }catch(error){$('app-error').hidden=false;$('app-error').textContent=error.message;}
}
init();
