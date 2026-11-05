# Research standards

Status: proposed methodological requirements; no indicators have been calculated.

## Define the measurement before the score

For every metric, record the question, target quantity, unit of analysis, formula, denominator, observation window, eligibility criteria, uncertainty, and known biases. Show components before aggregating them. Explain weights and check whether reasonable alternatives change conclusions.

## Keep time and evidence explicit

- Preserve source/event time, collection time, source timezone, and transport service date. Handle overnight service, daylight-saving transitions, and GTFS times beyond 24:00.
- Label scheduled, predicted, inferred, and independently observed times separately.
- Preserve raw responses and source versions where terms permit; record hashes, transformations, and rejected records.
- Track the age of the underlying source, not only when it was fetched.

## Reliability

Inspect exact schedules versus frequency service before defining delay; see the [GTFS frequencies reference](https://gtfs.org/documentation/schedule/reference/#frequenciestxt). Predicted delay and prediction variability can be reported with their actual meaning. Operational punctuality, headways, service counts, and cancellations require suitable observation evidence.

Do not count repeated forecasts as independent vehicle events. Audit event identity and matching errors. Treat missingness as a possible source/feed/collector failure; do not silently turn missing records into cancelled services or zero delays.

Stratify comparisons by route, direction, stop, service period, and day type where justified. Establish coverage and sample-size rules before publishing ranks. Respect temporal and within-trip dependence when estimating uncertainty. A pilot cannot support an unrestricted network-wide ranking.

## Network scenarios

Represent stops, transfers, walking links, and time-dependent service. Document assumptions about closed stops/edges, rerouting, waiting, and transfers. Compare scenarios against a fixed baseline. Graph vulnerability measures do not establish passenger crowding or operating capacity.

## Disruption warnings

Keep message application periods, source updates, first/last observation, and actual event onset/recovery distinct. Version incident reports and avoid duplicate counting.

Define the warning target and horizon before modeling. Use only information available at prediction time. Compare simple baselines using chronological holdouts, event-level evaluation, false-alarm rate, precision/recall, and useful warning lead time. Include uncertainty and enough independent events; do not use later message revisions as earlier knowledge.

## Neighbourhood access

Choose geographic units, distributed origins, service categories, departure times, travel-time thresholds, walking assumptions, and transfer rules explicitly. Match boundary/statistical vintages. Include surrounding network and destinations to assess edge effects.

Publish scheduled accessibility first where supported. Reliability-adjusted accessibility needs a justified historical model. Test sensitivity to origins, weights, routing assumptions, and coarse job allocations. Missing accessibility tags indicate unknown access.

## Validation and reproducibility

An eventual release must verify source parsing, timestamp handling, identity joins, missing-data behavior, and key analytical calculations. Preserve the environment, input versions, parameters, and expected outputs of a reproducible example. Record unresolved failures and negative findings.

No application tests or analytical experiments have been run in the planning stage.
