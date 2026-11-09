'use strict';
const byId=id=>document.getElementById(id);
const element=(tag,text,cls)=>{const node=document.createElement(tag);node.textContent=text;if(cls)node.className=cls;return node;};
let historyRequest=0, routes=[];
const lineName=id=>routes.find(r=>r.id===id)?.name||id;
async function loadHistory(){
  const request=++historyRequest;
  byId('history-status').textContent='Reading saved history…';
  byId('history-quality').textContent='';byId('versions').replaceChildren();
  try{
    const response=await fetch('/api/notice-history?'+new URLSearchParams({search:byId('query').value,line:byId('history-line').value}));
    const data=await response.json();if(request!==historyRequest)return;
    if(!response.ok)throw Error(data.error||'History unavailable.');
    byId('line-checks').replaceChildren();
    for(const route of routes){
      const check=(data.line_checks||[]).find(c=>c.line_id===route.id);
      const label=check?({ok:'notices returned',empty:'no notices returned',error:'check failed'}[check.status]||check.status):'not checked';
      const item=element('a',`Métro ${route.name}: ${label}`,'filter');
      item.href='/history?'+new URLSearchParams({line:route.id});
      item.title=check?`Last collected ${check.observed_at} (UTC)`:'No saved checks';
      byId('line-checks').append(item);
    }
    if(!data.available){byId('history-status').textContent='No archive yet. Start the notice collector to save your first check.';return;}
    const counts=data.summary.checks_by_status;
    byId('history-status').textContent=`${data.summary.notice_ids} notice IDs · ${data.summary.content_versions} distinct content versions · showing ${data.versions.length} of ${data.matched_versions} matching versions`;
    byId('history-quality').textContent=`Saved checks: ${counts.ok||0} with notices, ${counts.empty||0} empty, ${counts.error||0} failed. Excess time between checks: ${data.summary.excess_seconds_between_checks}s.${data.latest_check?` Last completed check: ${data.latest_check.observed_at} (UTC), ${data.latest_check.status}.`:''}`;
    if(!data.versions.length)byId('versions').append(element('p',data.summary.content_versions?'No saved versions match your search.':'No notice versions saved yet. Empty or failed checks do not establish normal service.','notice'));
    for(const version of data.versions){
      const report=version.report,card=element('article','','traffic-panel');
      card.append(element('h2',`Métro ${lineName(version.line_id)} · Notice ${version.notice_id}`));
      const mapLink=element('a','View this line on the map →');mapLink.href='/?'+new URLSearchParams({line:version.line_id});card.append(mapLink);
      card.append(element('p',`Reported status at collection: ${report.status} · Effect: ${report.effect}`,'eyebrow'));
      card.append(element('p',report.text||'No message text supplied.'));
      card.append(element('p',`First collected: ${version.first_collected_at} (UTC). Last collected: ${version.last_collected_at} (UTC). ${version.sample_count} sightings, potentially cached.`,'muted'));
      card.append(element('p',`Provider update: ${report.updated_at_local||'not supplied'} (Europe/Paris).`,'muted'));
      for(const period of report.periods_local||[])card.append(element('p',`Reported application: ${period.begin||'unspecified'} → ${period.end||'unspecified'} (Europe/Paris).`));
      const details=element('details','');details.append(element('summary','Version fingerprint'),element('p',version.version,'history-fingerprint'));card.append(details);byId('versions').append(card);
    }
  }catch(error){if(request===historyRequest)byId('history-status').textContent=error.message;}
}
byId('history-search').addEventListener('submit',event=>{event.preventDefault();loadHistory();});
byId('reload').addEventListener('click',loadHistory);
async function initHistory(){
  try{
    const response=await fetch('/api/network');if(!response.ok)throw Error('Network reference unavailable.');
    routes=(await response.json()).routes;
    for(const route of routes){const option=element('option',route.name);option.value=route.id;byId('history-line').append(option);}
    const requested=new URLSearchParams(location.search).get('line');
    if(routes.some(r=>r.id===requested))byId('history-line').value=requested;
    const select=()=>{const line=byId('history-line').value;byId('map-link').href=line?'/?'+new URLSearchParams({line}):'/';loadHistory();};
    byId('history-line').addEventListener('change',select);select();
  }catch(error){byId('history-status').textContent=error.message;}
}
initHistory();
