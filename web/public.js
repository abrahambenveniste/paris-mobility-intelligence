'use strict';
const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const clean=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
let network,groups=[],map,activeLine='all',layers=[],markers=[],liveEnabled=false;
const route=id=>network.routes.find(r=>r.id===id);
function badge(r){const b=el('span',r.name,'badge');b.style.setProperty('--route-color',r.color);return b;}
function setupJourneys(){
  const labels=new Map(),names=new Map();let revision=0;
  for(const g of groups){const point=g.stops[0],key=point.id+'|'+point.line_id,label=`${g.name} · ${g.commune}`;labels.set(clean(label),key);const name=clean(g.name);names.set(name,names.has(name)?null:key);const option=el('option');option.value=label;$('journey-stations').append(option);}
  for(const r of network.routes){const option=el('option',`Métro ${r.name}`);option.value=r.id;$('journey-avoid').append(option);}
  $('journey-submit').disabled=!liveEnabled;
  function changed(){revision++;$('journey-results').replaceChildren();}
  for(const id of ['journey-from','journey-to','journey-avoid'])$(id).addEventListener('input',changed);
  $('journey-swap').addEventListener('click',()=>{const from=$('journey-from');const to=$('journey-to');[from.value,to.value]=[to.value,from.value];changed();});
  $('journey-form').addEventListener('submit',async event=>{
    event.preventDefault();const out=$('journey-results'),button=$('journey-submit');
    const start=clean($('journey-from').value.trim()),end=clean($('journey-to').value.trim());
    const from=labels.get(start)||names.get(start),to=labels.get(end)||names.get(end),current=++revision;
    if(!from||!to){out.replaceChildren(el('p','Choose a station from the suggestions for both fields.','notice'));return;}
    if(from===to){out.replaceChildren(el('p','Choose two different stations.','notice'));return;}
    button.disabled=true;out.replaceChildren(el('p','Finding routes…'));
    try{
      const params=new URLSearchParams({from,to,avoid:$('journey-avoid').value}),response=await fetch('/api/journeys?'+params),data=await response.json();
      if(current!==revision)return;
      if(!response.ok)throw Error(data.error||'Routes are unavailable.');out.replaceChildren();
      out.append(el('p',`${data.cached?'Cached':'Fetched'} ${new Date(data.fetched_at).toLocaleString('en-GB',{timeZone:'Europe/Paris'})} Paris time.`, 'small muted'));
      if(!data.journeys.length)out.append(el('p',data.message||'No route was returned.'));
      for(const [index,j] of data.journeys.entries()){
        const card=el('section',undefined,'journey-result');card.append(el('h3',`Option ${index+1} · approximately ${Math.ceil(j.duration/60)} min`));
        for(const s of j.sections){let label;
          if(s.kind==='public_transport')label=`Métro ${s.line||'?'} towards ${s.direction||'destination not provided'} · ${s.from||'?'} → ${s.to||'?'} · ${s.freshness==='realtime'?'real-time data':s.freshness==='base_schedule'?'scheduled data':`data freshness: ${s.freshness||'unknown'}`}`;
          else if(s.kind==='waiting')label=`Wait · ${Math.ceil((s.duration||0)/60)} min`;
          else label=`${s.kind==='transfer'?'Transfer':'Walk'} · ${s.from||'start'} → ${s.to||'end'} · ${Math.ceil((s.duration||0)/60)} min`;
          card.append(el('p',label));
        }out.append(card);
      }
    }catch(error){if(current===revision)out.replaceChildren(el('p',error.message,'notice'));}finally{button.disabled=false;}
  });
}
function selectStation(group){
  const panel=$('station-info');panel.replaceChildren(el('h2',group.name),el('p',group.commune,'muted'));
  const list=el('div',undefined,'line-filters');
  for(const r of network.routes)if(group.stops.some(s=>s.line_id===r.id)){
    const button=el('button',undefined,'filter');button.append(badge(r));button.setAttribute('aria-label',`Choose métro ${r.name}`);
    button.addEventListener('click',()=>selectLine(group,r));list.append(button);
  }
  panel.append(list,el('p','Exact name and commune groups are for display; they do not verify transfers.','small muted'));
  const actions=el('div',undefined,'station-actions');
  for(const [id,label] of [['journey-from','Set as start'],['journey-to','Set as destination']]){const button=el('button',label,'filter');button.addEventListener('click',()=>{const input=$(id);input.value=`${group.name} · ${group.commune}`;input.dispatchEvent(new Event('input',{bubbles:true}));input.focus();});actions.append(button);}
  panel.append(actions);
  panel.append(el('div',undefined,'public-live'));
  if(map)map.fitBounds(group.stops.map(s=>[s.lat,s.lon]),{padding:[35,35],maxZoom:15});
}
function selectLine(group,r){
  const panel=$('station-info').querySelector('.public-live');panel.replaceChildren(el('h3',`Métro ${r.name} · on-demand information`));
  if(!liveEnabled){panel.append(el('p','Live information is not enabled on this preview yet.','small muted'));return;}
  const stops=group.stops.filter(s=>s.line_id===r.id);
  const departures=el('button','Get arrival estimates','filter'),traffic=el('button','Get line notices','filter');
  const arrivalOut=el('div',undefined,'point-estimates'),trafficOut=el('div',undefined,'point-estimates');
  panel.append(el('p',`Request estimates for ${group.name}, grouped by the destinations reported by the provider. Coverage may vary.`,'small muted'),departures,traffic,arrivalOut,trafficOut);
  async function request(kind){
    const out=kind==='departures'?arrivalOut:trafficOut;
    departures.disabled=traffic.disabled=true;out.replaceChildren(el('p','Requesting information…'));
    try{
      if(kind==='departures'){
        const results=[],details=el('details'),messages=[];
        details.append(el('summary','Source details'));
        for(let i=0;i<stops.length;i++){
          if(i)await new Promise(resolve=>setTimeout(resolve,1200));
          const stop=stops[i],params=new URLSearchParams({line:r.id,stop:'STIF:StopPoint:Q:'+stop.id.replace('IDFM:','')+':'});
          try{
            const response=await fetch('/api/departures?'+params),data=await response.json();if(!response.ok)throw Error(data.error||'Information unavailable.');
            results.push(...data.departures);details.append(el('p',`${stop.id} · ${data.cached?'cached':'fetched'} ${new Date(data.fetched_at).toLocaleString('en-GB',{timeZone:'Europe/Paris'})} Paris time · ${data.departures.length} estimate(s)`));
          }catch(error){messages.push(`One source point could not be loaded: ${error.message}`);details.append(el('p',`${stop.id} · unavailable`));}
        }
        out.replaceChildren();
        const grouped=new Map();for(const item of results){if(!grouped.has(item.destination))grouped.set(item.destination,[]);grouped.get(item.destination).push(item);}
        for(const [destination,items] of grouped){
          out.append(el('h3',`Towards ${destination}`));
          items.sort((a,b)=>(a.expected_at||'9999').localeCompare(b.expected_at||'9999'));
          for(const item of items){const time=item.expected_at?new Date(item.expected_at).toLocaleTimeString('en-GB',{timeZone:'Europe/Paris',hour:'2-digit',minute:'2-digit'}):'Time unavailable';out.append(el('p',item.cancelled?'Reported cancelled':`${time} · estimated ${item.kind}`));}
        }
        if(!results.length)out.append(el('p','No usable estimates returned. This does not establish that service has stopped.'));
        for(const message of messages)out.append(el('p',message,'notice'));
        out.append(el('p',`Checked ${stops.length} source point(s). Times are predictions, not confirmed arrivals; repeated records may refer to the same train.`, 'small muted'),details);
        return;
      }
      const params=new URLSearchParams({line:r.id});
      const response=await fetch('/api/'+kind+'?'+params),data=await response.json();if(!response.ok)throw Error(data.error||'Information unavailable.');
      out.replaceChildren(el('p',`${data.cached?'Cached':'Fetched'} ${new Date(data.fetched_at).toLocaleString('en-GB',{timeZone:'Europe/Paris'})} Paris time.`,'small muted'));
      if(kind==='traffic'){
        if(!data.reports.length)out.append(el('p','No directly linked notices returned. This does not confirm normal service.'));
        for(const item of data.reports){
          const card=el('article',undefined,'traffic-card');
          const status=item.status==='active'?'Reported active':item.status==='future'?'Reported upcoming':`Status: ${item.status||'not supplied'}`;
          card.append(el('strong',status),el('p',item.text));
          for(const period of item.periods_local||[]){
            if(!period.begin&&!period.end)continue;
            const duration=Date.parse(period.end)-Date.parse(period.begin);
            if(Number.isFinite(duration)&&duration>=0&&duration<60000)card.append(el('p','The source supplied an unusually short time period; check the notice text and official updates for timing.','small muted'));
            else card.append(el('p',`Reported period: ${(period.begin||'not supplied').replace('T',' ')} – ${(period.end||'not supplied').replace('T',' ')} (Paris time)`,'small muted'));
          }
          out.append(card);
        }
        out.append(el('p','Notices refer to the line, not necessarily this station.','small muted'));
        if(data.reports.length){
          const avoid=el('button',`Find a route avoiding métro ${r.name}`,'filter avoid-notice');
          avoid.addEventListener('click',()=>{
            const line=$('journey-avoid');line.value=r.id;line.dispatchEvent(new Event('input',{bubbles:true}));
            const start=$('journey-from'),destination=$('journey-to');
            if(!start.value.trim()){start.value=`${group.name} · ${group.commune}`;start.dispatchEvent(new Event('input',{bubbles:true}));}
            const target=destination.value.trim()?$('journey-submit'):destination;target.focus();
          });
          out.append(avoid,el('p',`This excludes the whole métro ${r.name} line. Review your stations and press Find routes.`, 'small muted'));
        }
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
    setupJourneys();
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
