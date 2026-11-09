'use strict';
const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const clean=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
let network,groups=[],map,activeLine='all',layers=[],markers=[];
const route=id=>network.routes.find(r=>r.id===id);
function badge(r){const b=el('span',r.name,'badge');b.style.setProperty('--route-color',r.color);return b;}
function selectStation(group){
  const panel=$('station-info');panel.replaceChildren(el('h2',group.name),el('p',group.commune,'muted'));
  const list=el('div',undefined,'line-filters');
  for(const r of network.routes)if(group.stops.some(s=>s.line_id===r.id))list.append(badge(r));
  panel.append(list,el('p','Exact name and commune groups are for display; they do not verify transfers.','small muted'));
  if(map)map.fitBounds(group.stops.map(s=>[s.lat,s.lon]),{padding:[35,35],maxZoom:15});
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
