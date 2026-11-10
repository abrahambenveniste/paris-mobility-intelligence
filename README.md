# Paris Mobility Intelligence 🚇

A little experiment with Paris métro data: can we turn public transport APIs into a map that’s fun to explore and useful enough to answer a few everyday questions?

## 🗺️ [Open the live Paris métro map →](https://paris-mobility-intelligence.onrender.com/)

Explore journeys and compare locations in your browser. No installation needed.

[How it works](docs/learning-walkthrough.md)

## What can you do with it?

- **Plan a journey:** pick two stations to see suggested routes, map paths and reported line disruptions.
- **Compare two places:** click the map to see nearby métro stations and compare their Mobility Proximity Scores.
- **Explore the network:** see route shapes and boarding points for the 16 published métro lines.

The score is an experiment, not an official accessibility rating. It combines straight-line distance to the nearest mapped point and the number of métro lines within 500 metres. It doesn’t measure walking routes, service frequency or step-free access. [Here’s the formula and what it leaves out.](docs/public-release.md#point-based-métro-proximity)

The map and proximity scores use a saved reference-data snapshot. Live journey and line-notice queries run only when someone requests them; caching and a conservative request budget help respect PRIM API limits. A line notice may not affect your specific trip. Address lookup sends the selected coordinates to the French public Géoplateforme. Historical collectors run locally, only while the owner’s computer is on. [More about the sources, deployment and limits.](docs/public-release.md)

## What’s the bigger idea?

Explore métro reliability, the transport network, disruptions and neighbourhood mobility together—starting small and building as the data allows.

## Run the local explorer

Requires Python 3.10+ and PRIM credentials in a private `.env` file. See the [setup guide](docs/local-release.md).

```powershell
python src/prepare_data.py
python src/app.py
```

Open [localhost:8765](http://127.0.0.1:8765). Historical collection runs locally while your computer is on.

## Under the hood

Python fetches and prepares the reference data; JavaScript, HTML, CSS and Leaflet turn it into the interactive map. SQLite stores local history, GitHub tracks the code, and Render hosts the public preview. The app also uses Île-de-France Mobilités APIs and the Géoplateforme address service.

Curious about the details?

- [Beginner walkthrough: data → Python → map](docs/learning-walkthrough.md)
- [Data sources and open questions](docs/data-sources.md)
- [Reliability collection pilot](docs/reliability-pilot.md) · [Disruption history](docs/disruption-history.md)
- [Decisions](docs/decisions.md) · [Contributing](CONTRIBUTING.md)
