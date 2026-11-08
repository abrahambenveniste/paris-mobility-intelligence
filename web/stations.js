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
// Keep each source observation: identical estimates do not prove the same train.
function destinationGroups(observations) {
  const groups = new Map();
  for (const observation of observations) {
    const destination = observation.destination || 'Unknown destination';
    if (!groups.has(destination)) groups.set(destination, []);
    groups.get(destination).push(observation);
  }
  const time = item => Number.isFinite(Date.parse(item.expected_at)) ? Date.parse(item.expected_at) : Infinity;
  return [...groups].sort(([a],[b]) => a.localeCompare(b,'fr')).map(([destination, estimates]) => ({
    destination, estimates: estimates.sort((a,b) => time(a)-time(b))
  }));
}
if (typeof module !== 'undefined') module.exports = {stationGroups, stationLineStops, destinationGroups};
