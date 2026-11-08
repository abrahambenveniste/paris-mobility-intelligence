const {test} = require('node:test');
const assert = require('node:assert/strict');
const {stationGroups,stationLineStops} = require('../web/stations.js');
const {destinationGroups} = require('../web/stations.js');

test('destination grouping preserves source observations and sorts timestamps across offsets',()=>{
  const input = [
    {destination:'Bagneux',point_id:'A',expected_at:'2026-11-08T09:08:00+01:00'},
    {destination:'Bagneux',point_id:'B',expected_at:'2026-11-08T08:03:00Z'},
    {destination:'Bagneux',point_id:'C',expected_at:'2026-11-08T08:03:00Z'},
    {destination:'Clignancourt',point_id:'D',expected_at:'2026-11-08T08:05:00Z'}
  ];
  const original=JSON.stringify(input), groups=destinationGroups(input);
  assert.deepEqual(groups.map(g=>g.destination),['Bagneux','Clignancourt']);
  assert.deepEqual(groups[0].estimates.map(e=>e.point_id),['B','C','A']);
  assert.equal(JSON.stringify(input),original);
});

test('unknown destinations and reported cancellations without a timestamp remain visible',()=>{
  const groups=destinationGroups([
    {destination:'Bagneux',expected_at:null,cancelled:true},
    {destination:'Bagneux',expected_at:'2026-11-08T08:03:00Z'},
    {destination:'',expected_at:'2026-11-08T08:04:00Z'}
  ]);
  assert.equal(groups[0].estimates[1].cancelled,true);
  assert.equal(groups[1].destination,'Unknown destination');
  assert.deepEqual(destinationGroups([]),[]);
});
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
