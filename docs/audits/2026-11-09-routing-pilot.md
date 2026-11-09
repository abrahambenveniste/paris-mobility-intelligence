# Routing feasibility pilot — 9 November 2026

**Purpose:** test whether PRIM can suggest an alternative métro journey, and whether a published disruption is reflected in its calculation. This is a bounded investigation, not a public routing feature.

**Publisher documentation:** [PRIM's generic Navitia API](https://prim.iledefrance-mobilites.fr/fr/apis/idfm-navitia-general-v2) offers journey calculations. [Navitia](https://doc.navitia.io/) documents `data_freshness=realtime` to account for supported disruptions and `forbidden_uris[]` to exclude a public-transport object. Publisher documentation does not establish how completely IDFM supplies real-time disruption effects.

**Method:** use `PRIM_API_KEY` locally, the published map coordinates, métro-only public-transport filtering and walking, and no saved raw API responses. Request `GET /marketplace/v2/navitia/journeys` with origin, destination, `data_freshness`, and optionally a forbidden line. At most three results were inspected per query. Time zone in the response was Europe/Paris. Six journey API calls and two traffic API calls were made during this investigation.

**Observed example 1:** for Châtelet → Bastille on 9 November, the realtime request returned a line 1 option (about 9 minutes) and walking. Excluding `line:IDFM:C01371` returned options using line 7 or lines 4 and 5, plus walking. Public-transport sections in the sampled responses were marked `base_schedule`: a realtime request does not ensure every section has realtime data.

**Observed example 2:** the line 6 notice feed described a future interruption between Kléber and Charles de Gaulle–Étoile for 11 November. For Charles de Gaulle–Étoile → Cambronne at 12:00 on that date, both `base_schedule` and `realtime` requests returned walking to Kléber followed by line 6. Explicitly excluding line 6 returned routes using other lines. The same baseline and realtime routes do not demonstrate that the published interruption was used; walking to Kléber might have been selected independently. No actual journey was taken.

**Decision and limits:** an on-demand route pilot appears technically feasible. A manually selected avoided line is a deliberate whole-line exclusion, not automatic identification of a closed segment; alternatives may include walking and still contain scheduled legs. We cannot claim that every disruption is accounted for, that an option is available in reality, or that the sampled notice is in effect at other times. Origin/destination stop matching, coverage, response freshness, public data-use conditions and shared quota controls require validation before publishing a route planner.

**Next:** choose a small station-to-station interface and test it against more known disruption cases, including a case where the provider demonstrably changes a route. Show route source, query time, affected line, legs and uncertainty. Do not infer closures from empty responses.
