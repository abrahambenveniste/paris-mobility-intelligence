# Project brief

Updated: 2026-11-05. Agreed scope; detailed methods and implementation remain to be decided.

## Purpose

Create a tool researchers can use to inspect Paris transport, compare supported indicators, explore disruption scenarios, and reproduce findings. Each result should explain what was measured, where, when, from which sources, and with what uncertainty.

## Scope

- Public GitHub repository with concise documentation and version history.
- Research audience; local and hosted deployment are intended.
- Initial sample: selected metro and bus lines in Paris. Select lines using coverage, operational diversity, and a documented sampling rationale.
- Eventual expansion depends on data coverage, representativeness, operating cost, and validation.
- Build projects 1, 2, 8, and 10 in that order after the shared foundation.
- Arrival prediction analysis is a supporting method, not a replacement for project 2.

## One website, one shared map

A persistent map carries the chosen location, lines, direction, date, and time across four views:

| View | Map content | Supporting panel |
| --- | --- | --- |
| Reliability | Lines and stops coloured by a selected supported measure | Components, observation counts, coverage, uncertainty, history |
| Network twin | Stops, lines, transfers, current published information, closure scenarios | Connections affected and modeled accessibility changes |
| Disruptions | Affected lines/stops and incident periods | Message history, reporting times, cause, severity, source |
| Neighbourhoods | Accessibility polygons and destination opportunities | Reachable services, transport frequency, population context, assumptions |

Latest information, historical statistics, and scenario results must be visibly distinguishable. Show data age and missing coverage. Offer tables, readable legends, and exportable results so essential findings do not depend on interpreting a map.

A research export should include the query settings, source versions, indicator definition, and quality flags. The final API, export formats, interface language, and hosting service are open decisions.

## What each module must establish

1. **Reliability:** compare like service with like service; confirm whether exact schedules or frequency service apply. Rank only where coverage and uncertainty support comparison. A predicted delay is not measured operational delay; absence of a record is not a cancellation.
2. **Digital twin:** begin with a network model updated by published information. Closure experiments can estimate connectivity/accessibility changes. Vehicle trajectories, passenger loads, dispatch responses, and congestion dynamics need additional evidence and calibration.
3. **Disruptions:** monitor and archive reports first. Measure reported periods separately from our observation window and actual event duration. Early warning is a research objective with an explicit validation gate.
4. **Mobility:** define origins, destinations, travel times, and geographic units before scoring. Publish component indicators and sensitivity to assumptions. Fine-grained workplace job locations remain unresolved.

## Completion standard

A new researcher can understand the methods, identify limitations, install the released tool, reproduce an example, and trace its output back to versioned inputs. No release should imply network-wide evidence from a small pilot.

Application and collector development require the user's explicit green light. Repository creation and planning documentation are already authorised.
