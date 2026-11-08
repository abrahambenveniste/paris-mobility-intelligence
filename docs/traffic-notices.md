# Adding reported conditions to the map

> Scope update, 6 November 2026: the app now covers all 16 published métro lines and excludes buses. See [current selection, coverage and tests](metro-expansion.md). The two-line counts and examples below document the earlier implementation; they are historical, not current coverage. Traffic uses a line selector; the original two-line query has been replaced by mode-based discovery.


## Purpose

Answer a small question: “Has the provider published a report explicitly linked to this pilot line?” This project-2 increment adds on-demand notices beside the map. It does not implement project 8's history or early-warning research.

## Source choice

Use [PRIM Messages Info Trafic v2, line reports](https://prim.iledefrance-mobilites.fr/fr/aide-et-contact/documentation/prise-en-main-des-api/api-information-trafic-travaux/api-calculateur-ile-de-france-mobilites-messages-info-trafic-v2). Its documented line filter lets us request one pilot line rather than download the regional bulk feed. The route is `/marketplace/v2/navitia/line_reports/lines/{line_id}/line_reports?count=100`.

The app explicitly maps `STIF:Line::C01083:` to `line:IDFM:C01083` (bus 38), and C01374 likewise for métro 4. A shared code connects the identifiers; we do not match names or message wording.

## The data-quality trap

**Observed input, 6 November 2026 around 00:07 Paris time:** two bounded requests each returned 21 disruption records. The response for a line also contained station notices and messages about other services at shared stops. Therefore “returned by the line endpoint” does not mean “the entire line is disrupted.”

**Derived output from those saved samples:** métro 4 had zero directly linked reports; bus 38 had one, with provider effect `MODIFIED_SERVICE`. The filter excluded 21 and 20 other records respectively. These are snapshot counts, not permanent facts or incident rates. Zero matching reports does not establish normal service.

## Actual code and explanation

In [traffic.py](../traffic.py):

```python
if identity not in linked and not direct:
    continue
```

`linked` contains disruption IDs explicitly attached to the requested line in the response. `direct` checks whether the report explicitly lists that line among its impacted objects. If neither condition holds, skip the record. This deliberately omits station-only accessibility reports until their scope can be represented properly.

**Synthetic teaching input:** a report named `demo` appears in the line's disruption links; a second report named `station-only` affects a station without a direct line link.

**Derived teaching output:** keep `demo`; exclude `station-only`. The test `test_related_station_report_is_not_line_interruption` checks exactly this case. The separate plain-text test turns `<p>Example <b>stop</b> closed.</p>` into `Example stop closed.`

Python converts provider HTML messages to text. Browser JavaScript inserts that text with `textContent`, never executes provider HTML, and draws the route dashed only when the selected response contains a provider-labelled `active` report. A dashed line means “read the notice”, not “every segment is closed”. Filtering the map to another line can hide that route; the notice remains clearly labelled with the queried line.

## Time, completeness and limits

- Display fetched time, provider update time and reported application periods separately. Provider dates without offsets remain explicitly labelled Europe/Paris; they are not relabelled UTC or used to calculate actual incident duration.
- Preserve the provider's status and effect; we do not infer severity or recompute active periods. Long periods and old updates can occur.
- Reject wrong-line responses, unexpected timezones, invalid dates, missing linked records and incomplete pagination. Show an error rather than implying no disruption.
- Cache each line for five minutes, only after a successful response. Requests happen on button clicks, with a separate persistent 900-request/24-hour local budget. Failed requests count. Other clients sharing the account are outside that budget.
- No background polling, historical archive, alerts, simulated closures or station-to-platform inference.
- Raw sample responses stay in ignored `artifacts/disruptions/`. Feed metadata includes upstream `private` labels; this is not a resolved redistribution licence. Do not publish raw messages or exports until terms are clarified.

## Validation and next action

Seven new synthetic tests plus eleven existing tests pass. JavaScript syntax is checked separately. Tests cover explicit linkage, unrelated station records, duplicate IDs, incomplete responses, missing records, date handling and empty successful responses. They do not establish the publisher's accuracy or coverage.

Browser checks confirmed the bus notice, cache reuse and métro empty-result warning. Four upstream calls in this increment: two bounded source-inspection requests and two browser-driven checks. The repeated bus check used the cache.

Next: owner review and one understanding check—why must a station lift notice not automatically mark an entire line as interrupted?

Current station-view integration: [notices beside departures](inline-notices.md).
