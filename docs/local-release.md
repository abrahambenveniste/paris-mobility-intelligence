# Local explorer v0.1

## What is ready

A local first version of project 2: explore all 16 published metro lines, search stations, choose a line, read destination-grouped departure estimates, check line notices, and inspect reference-data gaps. This is a network explorer, not a completed operational simulation or the other three research modules.

## Start and use it

On the owner's configured computer, double-click **Start Explorer.cmd** in the project’s `launchers` folder. It starts Python and opens the default browser. Keep the terminal open; Ctrl+C stops the server. Alternatively, run `python src/app.py --open` from the repository.

For a fresh installation: install Python 3.10+, copy `.env.example` to `.env`, fill in your own credentials, run `python src/prepare_data.py` once, then start the app. No Python packages, database or JavaScript build step is required. Internet access supplies live data, the map library and street tiles. Refresh reference data deliberately by rerunning preparation, then restart.

1. Search **Châtelet**, select the station, then choose **4**.
2. Compare the two reported destinations and inspect each estimate's source age.
3. Click **Check notices for this line**. Read its scope and fetch time.
4. Use **Reference coverage** to understand which records lack a match.

## Small code example

Actual startup code:

```python
address = f'http://127.0.0.1:{server.server_port}'
```

`127.0.0.1` means this computer. **Input:** default port `8765`. **Output:** `http://127.0.0.1:8765`. Starting the tool does not publish it online or enable background collection. Estimates and notices are requested only through their existing on-demand actions.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Python not found | Install Python 3.10+ and make its `python` command available |
| Reference snapshot missing | Run `python src/prepare_data.py` |
| Port already in use | Close the other running copy, or run `python src/app.py --port 8766 --open` |
| Live request fails | Check the private `.env`, internet connection and PRIM account quota; retry later |
| No estimates or notices | Read the availability warning; missing data does not prove stopped or normal service |
| Browser does not open | Copy the printed local address into your browser |

## Evidence and limits

Previous browser checks verified populated metro estimates, destination grouping, inline notice lookup, empty-report warnings and cache reuse. Those observations are documented in the station and notice guides. The offline suite contains 22 Python and six JavaScript tests; it does not prove complete publisher coverage or prediction accuracy.

Predictions are not confirmed arrivals. Name groups are not verified transfers. Notices are line-level and may concern another location or time. Countdown labels update on refresh. The software licence and data redistribution terms remain separate unresolved decisions; public GitHub visibility alone does not establish an open-source licence.

## Later, not required for this local version

Visual polish, broader accessibility/browser checks, verified transfers, closure simulation, hosting, continuous history and the other research modules remain follow-up work. The owner requested a usable version now and fine-tuning later. Code and validation are AI-assisted.

Understanding checkpoint: what is the difference between running this tool locally and hosting it for other people?

Release checks: all 28 offline tests and JavaScript syntax passed. Local HTTP checks returned the page, JavaScript and the 16-line/803-record snapshot. Browser-opening dispatch was checked with a mocked browser; the Windows double-click interaction was not separately exercised. These checks made no upstream PRIM requests.

Small-screen update: the map stays compact and visible while scrolling, result lists shrink to their contents, and controls are larger. Checked at 754 CSS pixels in a desktop browser; real-phone verification remains outstanding.
