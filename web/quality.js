'use strict';

// Count line/boarding-point records, not stations or successful live requests.
function coverageSummary(network, line = 'all') {
  const inScope = row => line === 'all' || row.line_id === line;
  const mapped = network.stops.filter(inScope);
  const missingCoverage = mapped.filter(stop => !stop.live_supported);
  const missingMap = network.unmapped.filter(inScope);
  return {
    mapped: mapped.length,
    matched: mapped.length - missingCoverage.length,
    missingCoverage,
    missingMap
  };
}

// Also expose this small pure function to offline Node tests.
if (typeof module !== 'undefined') module.exports = {coverageSummary};
