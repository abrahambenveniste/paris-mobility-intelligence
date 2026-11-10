"""Bounded on-demand lookups for the public demo; no polling or history."""
import re
from app import fetch_departures
from traffic import fetch_reports
from journey import fetch_journeys


class PublicLive:
    def __init__(self, network, key, budget):
        self.key, self.budget = key, budget
        self.lines = {r['id'] for r in network['routes']}
        self.stops = {(s['id'] + '|' + s['line_id']): s for s in network['stops']}
        # Public references contain stop IDs, not the restricted coverage dataset.
        self.points = {(s['line_id'], 'STIF:StopPoint:Q:' + s['id'][5:] + ':')
                       for s in network['stops'] if re.fullmatch(r'IDFM:\d+', s['id'])}

    def lookup(self, kind, line, stop=''):
        if not self.key or self.budget is None:
            raise RuntimeError('Live information is not configured yet.')
        if kind == 'traffic' and line in self.lines:
            return self.budget.get(('traffic', line), lambda: fetch_reports(line, self.key))
        if kind == 'departures' and (line, stop) in self.points:
            return self.budget.get(('departures', line, stop), lambda: fetch_departures(stop, line, self.key))
        raise ValueError('Select a published métro line and boarding point.')

    def journeys(self, start, end, avoid):
        if not self.key or self.budget is None:
            raise RuntimeError('Journey planner is not configured.')
        if start not in self.stops or end not in self.stops or start == end or (avoid and avoid not in self.lines):
            raise ValueError('Select different published stations and a valid line.')
        # Share a conservative 100/day budget with traffic, even though PRIM has a separate quota.
        return self.budget.get(('traffic', 'journey', start, end, avoid),
                               lambda: fetch_journeys(self.stops[start], self.stops[end], avoid, self.key))
