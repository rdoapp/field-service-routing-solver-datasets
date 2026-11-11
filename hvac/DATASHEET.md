# Datasheet

For version 1.1.0 of the HVAC field-service planning days, following
the questions of *Datasheets for Datasets* (Gebru et al., Communications of
the ACM 64(12), 2021). Items marked **owner** are to be completed by the
dataset's owner before publication.

## Motivation

**For what purpose was the dataset created?** To give routing and
scheduling research a set of realistic, openly usable one-day field-service
problems: a fleet of technicians and two-person teams with shifts, breaks
and skills facing a backlog much larger than one day's capacity, with time
windows and priorities, on real road travel times. Public
benchmarks of this kind usually lack one or more of: skills with counts
(teams), breaks that interrupt travel, multiple time windows, heavy
over-demand, and road matrices of a real region.

**Who created it, on behalf of whom, and who funded it?** **Owner**: names,
organisation and funding to be filled in.

## Composition

**What do the instances represent?** Each instance is one working day of a
fictitious company that cleans, washes, installs and repairs
air-conditioning units: its technicians, teams, the queue of waiting jobs,
and travel times and distances between all locations. There are
60 instances: regions Budapest and Pécs, fleets of 5, 10, 50
technicians, kinds `full`, `servable`, seeds 1, 2, 3, 4, 5.

**What does an instance consist of?** Locations (depots, technicians' end
locations, customer locations), technicians (shift 08:00-16:30, a
30-minute lunch break, skills), teams (single technicians, and two-person
installation crews), jobs (service minutes, time windows, priority 1-3,
required skills, and a descriptive value in euro), two n × n matrices
(travel seconds, metres), the objective, and upper bounds. FORMAT.md lists
every field.

**Is there a label or target?** No. Each instance is an optimisation
problem. The owner's best known solutions are given as references, not as
ground truth; they are not proven optimal.

**Is anything missing?** No field is withheld. The generator also builds,
for each day, one feasible reference plan (below); it is deliberately not
published, because it would mark which jobs were "meant" to be served.

**Are there errors, sources of variation or redundancies?** Two customer locations can
snap to the same road position and then share coordinates (they remain
separate locations). Travel times are rounded up to whole minutes.

**Is the dataset self-contained?** Yes. The release contains every file
needed to read, solve, check and score the problems. The instances were produced by the owner's generator, which is not published at this time; REPRODUCE.md describes how it works, and every problem records the seed and the settings it was drawn with. Outsiders cannot regenerate the problems: they are fixed files, checksummed and verifiable with the published validator.

**Does it contain personal or confidential data?** No. There are no real
customers, addresses, names or companies. Customer locations are random
points inside populated 1 km grid cells, drawn in proportion to the
cells' population, then moved to the nearest road; a point may by chance
lie near a real address but is not linked to any person or household. The
population grid itself is not redistributed.

## Collection and generation process

The data is **synthetic**: the owner's generator (provenance in each
problem) draws every instance from a seed. What comes from real data and
what is a modelling assumption:

| element | source |
|---|---|
| where customers live | **data**: Eurostat Census 2021 population grid, 1 km cells (version 3), cells within 15 km of Budapest's centre or 31 km of Pécs' (Budapest: all within 14 km; Pécs: 65 % within 6 km, the rest 6-30 km out) |
| road network, travel times, distances | **data**: OpenStreetMap, routed with OSRM (car profile); points are snapped to the nearest road (within 250 m, else redrawn) |
| share of customers per density class, dwellings, devices per customer, business customers | **assumption** (configurable; values in `provenance.parameters.customers`) |
| job mix: cleaning 55 %, washing 25 %, installation 10 %, repair 10 % (installation twice as likely at houses and offices) | **assumption** |
| service minutes: cleaning 30 and washing 60 per device (at most 240), installation 240, repair 60 | **assumption** |
| time windows: 60 % of jobs with a preferred slot get one (two-hour slots 08-10, 10-12, 12-14, 14-16; offices 08-16; installations half days), 10 % of windowed jobs a second slot | **assumption** |
| priority: repair 3; installation and overdue maintenance 2; otherwise 1 | **assumption** |
| value (`value_eur`, descriptive only, in no constraint or objective): per job type a rate in euro per hour of service (cleaning 90, washing 75, installation 75, repair 110) × service hours × a uniform factor 0.75-1.25, rounded to 5 euro (at least 5) | **assumption**: round figures of a plausible order for labour charges of HVAC service in Hungary; not market data |
| fleet: 5, 10 or 50 technicians; 1, 2 or 4 depots in suburban cells; 20 % installers in two-person crews returning to their depot; service technicians ending at a home location; skills `install`, `fgas`, `service` | **assumption** |
| shift 08:00-16:30, breaks 12:00-12:30 (service) and 12:30-13:00 (installers) | **assumption** |
| dependencies between attributes (offices book office hours, working customers early or late slots, ...) | **assumption**, all switched on |

**The reference plan and the queue.** For each day the generator first
builds one feasible route per team: it picks a job the team can serve
(an installation near the depot for an installation crew), takes its
nearest eligible jobs, and walks them in the order in which their service
can start earliest, until the route fills about 92 % of the shift. The jobs
on these routes are a *servable* queue: a `servable` instance consists of
exactly those jobs, so one feasible plan serves all of them. A `full`
instance adds further jobs drawn from the same distribution (customer and
job model, correlations included) until the queue reaches about 4.5 jobs
per technician times 21 (5 technicians), 16 (10) or 6 (50), at least 40
(5, 10) or 25 (50) jobs per technician. Implications:

- a `full` instance is known to admit a plan serving the reference jobs,
  which is a lower bound on what is achievable; it is a weak one (a
  nearest-neighbour walk); good solvers serve far more;
- the reference jobs are not marked, but they are not a uniform sample of
  the queue: they are spatially clustered around each team's start job
  and time-compatible with each other. In `servable` instances the queue
  consists only of them (for example, early-morning slots are rarer there
  than in the full queue on small fleets);
- the queue is far larger than a day's capacity by design: most jobs stay
  unserved in every solution.

**Who was involved?** No people were involved in producing the data; there
was no crowdwork and no data subjects.

**Over what time frame?** The data describes no real period. Each
instance has a nominal date (2026-06-16), used only to state the
time zone; no rule depends on it.

## Preprocessing

The population grid was cut to the two regions and reduced to cell
centres (the generator's input; the grid is not redistributed). Travel
times are rounded up to whole minutes (multiples of 60 s) so that every
leg is a whole number of minutes, as the problem's clock is. Generated
days were converted to the published format: internal construction data
(the reference plan, the generator's bookkeeping) was dropped and job ids
renumbered in queue order. Nothing else was filtered or edited.

## Uses

**Intended**: benchmarking and comparing algorithms for vehicle routing
and scheduling (team orienteering with time windows, skills with counts,
breaks and multiple windows; prize-collecting VRPTW variants), teaching,
and testing solvers and checkers (the `servable` instances have a known
tier-1 optimum).

**Not suitable**: estimating real demand, prices, market shares or travel
times in Budapest or Pécs; drawing conclusions about real customers,
neighbourhoods or companies; training models meant to predict real
customer or technician behaviour. Every distribution except the
population grid and the road network is an assumption.

**Could the composition harm anyone?** We are not aware of a way: the data
has no link to people. The two regions are named; their road networks are
public.

## Distribution

**How is it distributed?** **Owner**: hosting (e.g. Zenodo with a DOI) to
be decided. The release is a directory tree with checksums
(`SHA256SUMS`), JSON Schemas and Croissant metadata (`croissant.json`).

**Licence**: data under the Open Database License 1.0, contents under
the Database Contents License 1.0, with the attributions in `LICENSE`
(the matrices and coordinates derive from OpenStreetMap; customer
locations are drawn with Eurostat population weights). Code
(`tools/`, `schemas/`): MIT (`LICENSE-CODE`). Eurostat's reuse terms specific
to the Census 2021 population grid were not found on its download page;
the release follows Eurostat's general copyright notice (source
acknowledged, changes indicated, disclaimer) and redistributes no grid values.

**Export controls or other restrictions**: none known.

## Maintenance

**Who maintains it, and how can they be contacted?** **Owner**: contact to
be filled in.

**Will it be updated?** Solutions are added or improved in minor
versions; problems are never changed within a major version. Errors are corrected
in a new version recorded in `CHANGELOG.md`; earlier versions stay
available under their DOI.

**Can others contribute?** Better solutions can be submitted as solution
files (FORMAT.md); they are accepted when `tools/validate.py` accepts them
and `tools/score.py` ranks them above the best known one.

## Known limitations and biases

- **Synthetic, assumption-driven.** Job mix, service times, windows,
  priorities, values and fleet structure are modelling
  assumptions of one HVAC business type, not measurements. Service times
  are deterministic multiples of 30 minutes.
- **Two regions of one country.** Budapest (dense, all urban) and Pécs (a
  smaller city with villages around it). Other road networks, densities
  and city shapes are not represented.
- **Static travel times.** One travel time per pair of locations,
  regardless of the time of day: no traffic, no congestion, no parking or
  walking time. Times are rounded up to whole minutes.
- **One day.** No multi-day planning, carry-over, cancellations, emergency
  arrivals or re-planning.
- **Uniform shifts.** Every technician works the same shift; every
  service technician takes the same break.
- **Reference-plan bias** (above): `servable` instances are a spatially
  and temporally selected subset, not a random sample.
- **Bounds are loose.** The bounds come from a capacity relaxation that
  ignores waiting, return legs and routing; on full instances they are
  close to the fleet's capacity and usually far from attainable.
- **Values are descriptive.** Job values are an assumption (euro rates
  above) and enter no objective; a value-based variant defined by others
  inherits that assumption.
- **Snapping.** Customer points are moved to the nearest road (at most
  250 m); two customers may share a road position, and points less than a
  few metres apart on one road have zero travel time and distance between
  them.
