'use strict';
const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const clean=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
let network,groups=[],map,activeLine='all',layers=[],markers=[],liveEnabled=false;
const route=id=>network.routes.find(r=>r.id===id);
function badge(r){const b=el('span',r.name,'badge');b.style.setProperty('--route-color',r.color);return b;}
function selectStation(group){
  const panel=$('station-info');panel.replaceChildren(el('h2',group.name),el('p',group.commune,'muted'));
  const list=el('div',undefined,'line-filters');
  for(const r of network.routes)if(group.stops.some(s=>s.line_id===r.id)){
    const button=el('button',undefined,'filter');button.append(badge(r));button.setAttribute('aria-label',`Choose métro ${r.name}`);
    button.addEventListener('click',()=>selectLine(group,r));list.append(button);
  }
  panel.append(list,el('p','Exact name and commune groups are for display; they do not verify transfers.','small muted'));
  panel.append(el('div',undefined,'public-live'));
  if(map)map.fitBounds(group.stops.map(s=>[s.lat,s.lon]),{padding:[35,35],maxZoom:15});
}
function selectLine(group,r){
  const panel=$('station-info').querySelector('.public-live');panel.replaceChildren(el('h3',`Métro ${r.name} · on-demand information`));
  if(!liveEnabled){panel.append(el('p','Live information is not enabled on this preview yet.','small muted'));return;}
  const stops=group.stops.filter(s=>s.line_id===r.id), select=el('select');select.setAttribute('aria-label','Choose boarding point');
  for(const stop of stops){const option=el('option',`Boarding point ${stop.id.replace('IDFM:','')}`);option.value=stop.id;select.append(option);}
  const departures=el('button','Get arrival estimates','filter'),traffic=el('button','Get line notices','filter'),out=el('div',undefined,'point-estimates');
  panel.append(el('p','Select one boarding point to request estimates. Coverage may vary.','small muted'),select,departures,traffic,out);
  async function request(kind){
    departures.disabled=traffic.disabled=true;out.replaceChildren(el('p','Requesting information…'));
    try{
      const params=new URLSearchParams({line:r.id});if(kind==='departures')params.set('stop','STIF:StopPoint:Q:'+select.value.replace('IDFM:','')+':');
      const response=await fetch('/api/'+kind+'?'+params),data=await response.json();if(!response.ok)throw Error(data.error||'Information unavailable.');
      out.replaceChildren(el('p',`${data.cached?'Cached':'Fetched'} ${new Date(data.fetched_at).toLocaleString('en-GB',{timeZone:'Europe/Paris'})} Paris time.`,'small muted'));
      if(kind==='traffic'){
        if(!data.reports.length)out.append(el('p','No directly linked notices returned. This does not confirm normal service.'));
        for(const item of data.reports)out.append(el('p',item.text));
        out.append(el('p','Notices refer to the line, not necessarily this station.','small muted'));
      }else{
        if(!data.departures.length)out.append(el('p','No usable estimates returned for this point. This does not establish that service has stopped.'));
        for(const item of data.departures){const time=item.expected_at?new Date(item.expected_at).toLocaleTimeString('en-GB',{timeZone:'Europe/Paris',hour:'2-digit',minute:'2-digit'}):'Time unavailable';out.append(el('p',`${item.destination} · ${item.cancelled?'reported cancelled':time+' estimated '+item.kind}`));}
        out.append(el('p','Times are predictions, not confirmed arrivals.','small muted'));
      }
    }catch(error){out.replaceChildren(el('p',error.message,'notice'));}finally{departures.disabled=traffic.disabled=false;}
  }
  departures.addEventListener('click',()=>request('departures'));traffic.addEventListener('click',()=>request('traffic'));
}
function filteredStops(){const q=clean($('search').value.trim());return network.stops.filter(s=>(activeLine==='all'||s.line_id===activeLine)&&(!q||clean(s.name+' '+s.commune).includes(q)));}
function fit(){if(map){const stops=filteredStops();if(stops.length)map.fitBounds(stops.map(s=>[s.lat,s.lon]),{padding:[30,30],maxZoom:14});}}
function render(){
  const stops=filteredStops(),visible=new Set(stops),matching=groups.filter(g=>g.stops.some(s=>visible.has(s)));
  $('stop-list').replaceChildren();$('result-count').textContent=`${matching.length} station name groups`;
  for(const group of matching){const b=el('button',undefined,'stop-row'),names=el('span',undefined,'names');names.append(el('strong',group.name),el('small',group.commune));b.append(names);const badges=el('span',undefined,'station-badges');for(const r of network.routes)if(group.stops.some(s=>s.line_id===r.id))badges.append(badge(r));b.append(badges);b.setAttribute('aria-label',`${group.name}, ${group.commune}`);b.addEventListener('click',()=>selectStation(group));$('stop-list').append(b);}
  for(const marker of markers){if(visible.has(marker.stop))marker.addTo(map);else marker.remove();}
  for(const layer of layers){if(activeLine==='all'||layer.routeId===activeLine)layer.addTo(map);else layer.remove();}
  for(const button of $('line-filters').querySelectorAll('button')){const selected=button.dataset.line===activeLine;button.classList.toggle('active',selected);button.setAttribute('aria-pressed',String(selected));}
}
async function init(){
  try{
    const response=await fetch('/api/network');if(!response.ok)throw Error('Reference data could not be loaded.');network=await response.json();groups=stationGroups(network.stops);
    try{const features=await fetch('/api/features');liveEnabled=features.ok&&(await features.json()).live===true;}catch(_){liveEnabled=false;}
    if(liveEnabled)$('preview-notice').textContent='Public preview. Arrival estimates and line notices are available on demand; historical analysis remains local. Reference routes do not represent live vehicle positions.';
    $('live-sources').hidden=!liveEnabled;
    $('point-count').textContent=network.stops.length;$('line-count').textContent=network.routes.length;
    $('snapshot-date').textContent=`Reference snapshot downloaded ${new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Paris',dateStyle:'medium',timeStyle:'short'}).format(new Date(network.prepared_at))} (Paris time). This is a download time, not a live update.`;
    for(const r of network.routes){const button=el('button',undefined,'filter');button.dataset.line=r.id;button.setAttribute('aria-label','Métro '+r.name);button.append(badge(r));$('line-filters').append(button);}
    $('line-filters').addEventListener('click',event=>{const button=event.target.closest('button');if(!button)return;activeLine=button.dataset.line;render();fit();});
    $('search').addEventListener('input',render);$('fit-map').addEventListener('click',fit);
    if(window.L){map=L.map('map',{zoomControl:false}).setView([48.8566,2.3522],12);L.control.zoom({position:'topright'}).addTo(map);new ResizeObserver(()=>map.invalidateSize({pan:false})).observe($('map'));
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · Routes/stops: Île-de-France Mobilités'}).on('tileerror',()=>{$('map-warning').hidden=false;$('map-warning').textContent='Street tiles are unavailable; station search remains available.';}).addTo(map);
      for(const r of network.routes){const layer=L.geoJSON(r.geometry,{style:{color:r.color,weight:3,opacity:.7},interactive:false});layer.routeId=r.id;layers.push(layer);}
      for(const stop of network.stops){const r=route(stop.line_id),marker=L.circleMarker([stop.lat,stop.lon],{radius:4.5,color:r.color,fillColor:'#fff',fillOpacity:1,weight:2});marker.stop=stop;marker.bindTooltip(el('span',`Métro ${r.name} · ${stop.name}`));marker.on('click',()=>selectStation(groups.find(g=>g.stops.includes(stop))));markers.push(marker);}
    }else{$('map').textContent='Map library unavailable. Station search remains available.';}
    render();fit();
  }catch(error){$('app-error').hidden=false;$('app-error').textContent=error.message;$('result-count').textContent='Network unavailable';}
}
init();
