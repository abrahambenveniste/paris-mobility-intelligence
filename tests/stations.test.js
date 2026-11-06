const {test} = require('node:test');
const assert = require('node:assert/strict');
const {stationGroups,stationLineStops} = require('../web/stations.js');
const stops = [
  {id:'1',name:'Châtelet',commune:'Paris',line_id:'A',live_supported:true},
  {id:'2',name:'Châtelet',commune:'Paris',line_id:'A',live_supported:false},
  {id:'3',name:'Châtelet',commune:'Paris',line_id:'B',live_supported:true},
  {id:'4',name:'Les Halles',commune:'Paris',line_id:'A'},
  {id:'5',name:'Châtelet',commune:'Elsewhere',line_id:'A'}
];
test('same name and commune group platforms without merging nearby names or communes',()=>{
  const groups=stationGroups(stops);
  assert.equal(groups.length,3);
  const paris=groups.find(g=>g.name==='Châtelet'&&g.commune==='Paris');
  assert.deepEqual(paris.stops.map(s=>s.id),['1','2','3']);
  assert.equal(stops.length,5);
});
test('line selection retains both covered and uncovered records without crossing lines',()=>{
  const group=stationGroups(stops).find(g=>g.name==='Châtelet'&&g.commune==='Paris');
  assert.deepEqual(stationLineStops(group,'A').map(s=>s.id),['1','2']);
  assert.deepEqual(stationLineStops(group,'unknown'),[]);
  assert.deepEqual(stationGroups([]),[]);
});
