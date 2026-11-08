# Notices beside departures

## Purpose and decision

The owner chose to bring disruption information into the station view. After choosing a station and line, click **Check notices for this line** to read reports without leaving the departures. This is presentation of published information, not incident prediction.

## How we built it

Actual code from `web/app.js`:

```javascript
loadTraffic(selected.line_id, $('station-traffic-result'));
```

The line identifier says what to request; the page element says where to show it. The existing renderer serves both this panel and the independent lookup below the map. We reuse the existing API, filtering and five-minute cache rather than introduce another data source or dependency.

The panel has a limited height and scrolls for longer reports, keeping departures accessible. It labels reports as line-level, preserves provider status, dates and IDs, and shows errors or empty responses explicitly. Changing station or choosing a line clears the inline result. Each panel tracks its current request so a late response cannot overwrite a newer selection. Only the latest traffic query can update the dashed route styling.

## Input, output and validation — 8 November 2026

**Empirically inspected input:** the Châtelet / métro-4 query returned zero directly linked reports and 21 records excluded by the existing direct-line-link filter.

**Displayed output:** “Métro 4 · 0 explicitly linked report(s)” beside departures, followed by “This is not confirmation of normal service”, fetch time, cache duration and the excluded-record count. No provider message text or raw payload is committed.

**Checks:** 22 Python tests and six JavaScript tests pass; JavaScript syntax passes. Browser checks confirmed the inline empty-result warning, intact departure results reset on reselecting the line and cached reuse. A resize observer redraws map tiles when the expanded panel changes map height. The existing tests validate backend report filtering; they do not simulate every browser race or prove upstream completeness.

## Limits and next action

A report linked to a line may concern another station or a future period. Conversely, the conservative filter may exclude station-only or accessibility notices. Empty results do not establish normal service. No station-specific disruption inference, continuous polling or hosting was added.

Next: owner review of the combined station view. Understanding question: why does a line notice not prove that the selected station is disrupted? Implementation and validation are AI-assisted; the owner selected the feature.
