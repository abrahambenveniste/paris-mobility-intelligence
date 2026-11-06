const {test} = require('node:test');
const assert = require('node:assert/strict');
const {coverageSummary} = require('../web/quality.js');

const fixture = {
  stops: [
    {id:'same-point',line_id:'A',live_supported:true},
    {id:'same-point',line_id:'B',live_supported:true},
    {id:'other',line_id:'A',live_supported:false}
  ],
  unmapped: [{line_id:'A',monitoring_ref:'unmatched'}]
};

test('counts line-point associations and keeps the two mismatch directions separate', () => {
  const result = coverageSummary(fixture);
  assert.equal(result.mapped, 3);
  assert.equal(result.matched, 2);
  assert.equal(result.missingCoverage[0].id, 'other');
  assert.equal(result.missingMap[0].monitoring_ref, 'unmatched');
  assert.equal(fixture.stops.length, 3);
});

test('line selection excludes other lines and handles an empty subset', () => {
  const result = coverageSummary(fixture, 'B');
  assert.equal(result.mapped, 1);
  assert.equal(result.matched, 1);
  assert.deepEqual(result.missingCoverage, []);
  assert.deepEqual(result.missingMap, []);
  assert.equal(coverageSummary(fixture, 'unknown').mapped, 0);
});
