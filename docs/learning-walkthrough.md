# From transport data to a map

> Scope update, 6 November 2026: the app now covers all 16 published métro lines and excludes buses. See [current selection, coverage and tests](metro-expansion.md). The two-line counts and examples below document the earlier implementation; they are historical, not current coverage. Traffic uses a line selector; the original two-line query has been replaced by mode-based discovery.


New to transport APIs? You’re in the right place. Follow along with the source code as we turn a small data sample into a map. Some examples describe our earlier pilot; the scope note above points to the current version. Development is AI-assisted, and the exercises are here to try at your own pace.

## 1. Begin with a useful question

“Where are the boarding points for métro 4 and bus 38, and what are their next reported departures?”

These two lines were selected by the owner after a small data audit. This keeps the first version understandable and cheap to inspect. It does not make the sample representative of Paris. We started with a map because coordinates and published predictions were usable; actual arrival evidence was insufficient for a defensible reliability ranking.

## 2. Understand the ingredients

An **API** is a service that accepts a request and returns data. **JSON** is a text format containing named values, lists and objects. An **identifier** is a source's stable reference to an object; names alone can be ambiguous.

We combine three reference datasets: stop/line associations, route shapes, and real-time coverage. A separate PRIM request returns predictions when a user selects a point. Reference data describes the network; prediction data changes frequently.

The current local reference snapshot, downloaded on 5 November 2026, contains two routes, 118 mapped boarding points and one unmatched coverage point. A boarding point can be one platform or direction; it is not necessarily a whole station. These are inspected counts, not fabricated teaching examples.

An API key permits access. It is stored in `.env`, excluded from Git, and used by Python rather than sent to the browser. Publicly accessible data can still require registration and have conditions on reuse. “Open data” and “open-source software” describe different things.

## 3. Why these tools?

| Choice | Reason in this project | Tradeoff |
| --- | --- | --- |
| Python | Readable data transformations; built-in JSON, HTTP and testing tools cover this small pilot | The simple local HTTP server is not a production hosting design |
| JavaScript | Runs in the browser and handles clicks, searches and map updates | We maintain a small second language alongside Python |
| HTML / CSS | HTML describes page content; CSS controls appearance and layout | We manage layout and accessibility directly |
| Leaflet | Existing map library draws tiles, lines and markers | External dependency; pinned version and attribution required |
| Local JSON file | Enough for a small reference snapshot; easy to inspect | Not suitable for querying a growing historical archive |
| Git and GitHub | Git records changes; GitHub shares the code and explanations | A public repository alone does not grant an open-source licence |

Python is a practical choice here, not a proven winner over every language. JavaScript could also run the server; R would suit many statistical analyses. No comparative performance benchmark was conducted. We avoided a database, machine learning and a large web framework because this first question does not need them.

## 4. Download a bounded subset

In [prepare_data.py](../prepare_data.py), this actual query selects the two line IDs:

```python
'arrets-lignes': 'id in ("IDFM:C01374","IDFM:C01083")',
```

The script requests pages of at most 100 records, checks response size, and refuses an unexpectedly large pilot. **Pagination** means downloading results in manageable pages. Five catalogue requests were needed for the inspected snapshot. We record counts, retrieval times and hashes; a hash is a fingerprint of received bytes, not proof that the source is correct. Downloading pages is not an atomic snapshot: source changes between pages remain a limitation.

Run once from the repository folder:

```powershell
python prepare_data.py
```

Observed output for our snapshot:

```text
Prepared 2 routes and 118 boarding points; 1 coverage points remain unmapped.
```

The generated file is `data/pilot-network.json`. Inspect it in your editor. It contains `routes`, `stops`, `unmapped` and `sources`, plus the preparation time. It stays outside Git while data redistribution terms remain under review.

## 5. Check and connect the records

Actual code from `build_network`:

```python
lat, lon = float(row['stop_lat']), float(row['stop_lon'])
if not (48 <= lat <= 49.5 and 1.5 <= lon <= 3.5):
    raise ValueError('Coordinate outside the expected regional bounds')
```

`float` converts a numeric value to a decimal number. The condition rejects coordinates far outside our study region, including mistakenly supplied projected coordinates. It cannot prove that a point is on the correct platform.

We match a line and a stop reference together. Matching two tables using shared identifiers is a **join**. We translate the inspected numeric stop-ID format into the monitoring-reference format, then check that exact pair against published coverage. We do not match similar names or invent a location for the unmatched point.

A **synthetic** example of the output structure, not a real stop:

```json
{
  "id": "IDFM:999001",
  "line_id": "STIF:Line::DEMO:",
  "monitoring_ref": "STIF:StopPoint:Q:999001:",
  "name": "Example boarding point",
  "lat": 48.85,
  "lon": 2.35,
  "commune": "Paris",
  "live_supported": true
}
```

`live_supported` means the pair appears in the coverage reference. It does not guarantee a fresh prediction on every request.

## 6. Build the map

The browser asks our local Python server for `/api/network`. In [web/app.js](../web/app.js), the key map operations are:

```javascript
map = L.map('map', {zoomControl: false}).setView([48.8566, 2.3522], 12);
```

`L` is Leaflet. This creates a map inside the page element named `map`, centred on Paris. OpenStreetMap tiles supply the street background. Official IDFM geometries supply the transport routes: we do not draw a route by connecting alphabetically sorted stops.

These shortened excerpts retain the actual drawing operations:

```javascript
L.geoJSON(r.geometry, {style: {color: r.color, weight: 3, opacity: .7}, interactive: false});
L.circleMarker([stop.lat, stop.lon], {radius: 4.5, color: r.color});
```

**GeoJSON** is a standard JSON format for geographic shapes. Its coordinates use longitude then latitude. Leaflet's marker arguments use latitude then longitude. Reversing these is a common map bug.

HTML creates the search box and detail panel; CSS arranges them; JavaScript filters the list, updates markers and reacts to selections. A line on a map is not yet a routing graph with verified transfers or a simulation of passenger behaviour.

## 7. Turn a live response into readable estimates

Selecting a point calls the local `/api/departures` route. Python requests PRIM, checks its delivery status, and filters the response to the selected line. The actual filter in [app.py](../app.py) is:

```python
if journey.get('LineRef', {}).get('value') != line:
    continue
```

`continue` skips that record and moves to the next one. This matters because a stop response can contain multiple lines.

The code prefers expected departure time, otherwise labels expected arrival time as arrival. It removes invalid timestamps and past non-cancelled predictions. Only explicit cancellation status is treated as cancellation. No record is not evidence of no service.

Run the [offline teaching example](../examples/explain_prediction.py):

```powershell
python examples/explain_prediction.py
```

It passes a fabricated response through our real transformation function. It makes no API request, reads no credentials and does not describe an actual journey. Inspect both input and output in the terminal. The five-minute difference is a predicted wait from the chosen reference time, not measured punctuality.

Selected **synthetic input** fields:

```json
{"LineRef": {"value": "STIF:Line::DEMO:"}, "MonitoredCall": {"ExpectedDepartureTime": "2026-01-01T12:05:00Z"}}
```

Selected **derived output**, verified by running the example at its fixed 12:00 UTC reference time:

```json
{"expected_at": "2026-01-01T12:05:00+00:00", "kind": "departure", "destination": "Example terminus"}
```

`Z` and `+00:00` both mean UTC. The function makes the nested source response easier for the interface to use; it does not turn the estimate into a confirmed event.

The app caches results for two minutes. A **cache** reuses a recent result to save requests. It also displays source-record age: a newly fetched response can still contain an old prediction.

## 8. Run, inspect and explain

```powershell
python app.py
```

Open http://127.0.0.1:8765. Search Cité, select a boarding point, read its identifier and estimate labels, then refresh. Close the server with Ctrl+C. A successful response today does not guarantee that the source is always available.

```powershell
python -m unittest discover -s tests -v
```

Eleven automated tests use controlled inputs to check filtering, dates, matching, caching and HTTP isolation. Tests help detect programming mistakes; they do not establish the accuracy or completeness of IDFM's data. See [methods and limits](network-explorer.md) for the fuller account.

Before expanding the project, explain the journey of one record: source → identifier matching → validation → local JSON → browser marker → selected-point prediction. Being able to reproduce and critique that chain demonstrates more than an attractive screenshot alone.
