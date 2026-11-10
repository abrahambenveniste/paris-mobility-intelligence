'use strict';
// Counts source points inside each polygon, grouping station names for display.
function pointInRing(point,ring){
  const [x,y]=point;let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const [xi,yi]=ring[i],[xj,yj]=ring[j];
    const cross=(x-xi)*(yj-yi)-(y-yi)*(xj-xi);
    if(Math.abs(cross)<1e-12&&x>=Math.min(xi,xj)-1e-10&&x<=Math.max(xi,xj)+1e-10&&y>=Math.min(yi,yj)-1e-10&&y<=Math.max(yi,yj)+1e-10)return true;
    if((yi>y)!==(yj>y)&&x<(xj-xi)*(y-yi)/(yj-yi)+xi)inside=!inside;
  }
  return inside;
}
function pointInPolygon(point,geometry){const rings=geometry.coordinates;return pointInRing(point,rings[0])&&!rings.slice(1).some(r=>pointInRing(point,r));}
function areaIndicators(area,stops){
  const names=new Set(),lines=new Set();let points=0;
  for(const s of stops){if(pointInPolygon([s.lon,s.lat],area.geometry)){points++;names.add(JSON.stringify([s.name,s.commune]));lines.add(s.line_id);}}
  return {stations:names.size,lines:lines.size,points};
}
// Great-circle distance: a geographical approximation, not a walking route.
function distanceMetres(lat1,lon1,lat2,lon2){
  const rad=Math.PI/180, dLat=(lat2-lat1)*rad,dLon=(lon2-lon1)*rad;
  const a=Math.sin(dLat/2)**2+Math.cos(lat1*rad)*Math.cos(lat2*rad)*Math.sin(dLon/2)**2;
  return 6371000*2*Math.atan2(Math.sqrt(a),Math.sqrt(Math.max(0,1-a)));
}
function nearbyMobility(lat,lon,stops,radius=500){
  const groups=new Map(),lines=new Set();
  for(const s of stops){const distance=distanceMetres(lat,lon,s.lat,s.lon);if(distance>radius)continue;
    const key=JSON.stringify([s.name,s.commune]);if(!groups.has(key))groups.set(key,{name:s.name,commune:s.commune,distance,lines:new Set()});
    const g=groups.get(key);if(distance<g.distance){g.distance=distance;g.lat=s.lat;g.lon=s.lon;}else if(g.lat===undefined){g.lat=s.lat;g.lon=s.lon;}
    g.lines.add(s.line_id);lines.add(s.line_id);
  }
  const stations=[...groups.values()].sort((a,b)=>a.distance-b.distance);
  const nearest=stations.length?stations[0].distance:null;
  // Illustrative 50/50 weighting; four distinct lines saturate the line component.
  const score=nearest===null?0:Math.round(50*(1-nearest/radius)+50*Math.min(lines.size/4,1));
  return {stations,lines,nearest,score};
}
if(typeof module!=='undefined')module.exports={pointInRing,pointInPolygon,areaIndicators,distanceMetres,nearbyMobility};
