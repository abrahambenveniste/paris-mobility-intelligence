'use strict';

// Display groups only: names and communes do not establish physical transfers.
function stationGroups(stops) {
  const groups = new Map();
  for (const stop of stops) {
    const id = JSON.stringify([stop.name, stop.commune]);
    if (!groups.has(id)) groups.set(id, {id, name: stop.name, commune: stop.commune, stops: []});
    groups.get(id).stops.push(stop);
  }
  return [...groups.values()].sort((a,b) => a.name.localeCompare(b.name,'fr') || a.commune.localeCompare(b.commune,'fr'));
}
function stationLineStops(group, line) {
  return group.stops.filter(stop => stop.line_id === line);
}
if (typeof module !== 'undefined') module.exports = {stationGroups, stationLineStops};
