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
if(typeof module!=='undefined')module.exports={pointInRing,pointInPolygon,areaIndicators};
