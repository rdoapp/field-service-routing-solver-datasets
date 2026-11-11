# Reproducing this release

Version 1.1.0. Every problem file records how it was made
(`provenance`). This file says what can
be checked by anyone and how the problems were generated and how the solutions were produced.

## Checking a copy

```sh
sha256sum -c SHA256SUMS
python tools/validate.py problems/<instance>/problem.json [SOLUTION.json ...]
```

`validate.py` re-checks each problem (structure, matrices) and each
solution given (every rule of PROBLEM.md) and prints the objective values.
`tools/score.py` ranks two solutions. Both need only Python 3.9 or later.
For each published solution the printed values must equal the `objective`
block of its file and its row in `solutions/index.csv`.

**This is the reproducibility claim of the release:** the problems are
fixed files, checksummed in `SHA256SUMS`, and every solution and score can
be checked with the published tools. Benchmark against the files as
published.

## How the problems were generated

The instances were produced by the owner's generator, which is not published at this time. This section describes the process and what each problem records; it is not a recipe that outsiders can run, and outsiders cannot regenerate the problems.

Each instance was drawn from one seed by that generator. In outline:

1. **Customers.** Customer locations are drawn in proportion to the
   population of the 1 km cells of Eurostat Census 2021 population grid, 1 km, version 3
   (https://gisco-services.ec.europa.eu/census/2021/Eurostat_Census-GRID_2021_V3.zip, SHA-256 `18a467e3d96b71dd89f0440cc184751bded45721cdff8ba778ece79d7a4f5843`) around Budapest
   or Pécs, with modelled shares of flats, houses and offices, devices per
   customer and customer types (DATASHEET.md lists every distribution).
2. **Jobs.** Each customer gets one job: type, service minutes, time
   windows from a preferred slot, priority, required skills and a
   descriptive value, drawn from the modelled distributions.
3. **Fleet.** Technicians, depots, end locations, shifts, breaks, skills
   and two-person installation crews.
4. **Matrices.** Every point is snapped to the nearest road and the travel
   times and distances are computed by OSRM 5.27.1, profile
   `car`, on the OpenStreetMap extract `hungary-latest.osm.pbf` of
   2023-05-01 (SHA-256 `2ea918d3686735a39b755349da2c3a3f88a31219f896858cb87860e30d250b4c`); times are rounded up to
   whole minutes. A point that cannot be snapped within 250 m is redrawn.
5. **Reference plan.** For each team the generator builds one feasible
   route (a start job, its nearest eligible jobs, walked in the order in
   which their service can start earliest, filling about 92 % of the
   shift). A `servable` instance consists of exactly those jobs; a `full`
   instance adds further jobs from the same distributions. The reference
   plan is checked by an independent checker and is not published.
6. **Conversion.** The day is written in the published format; internal
   construction data is dropped and job ids are renumbered in queue order;
   the bounds of PROBLEM.md section 7 are computed.

Every problem records what it was generated from:
`provenance.generator` (generator name, version label and source commit;
`repository`: generator source: not published), `provenance.instance_spec` (region, fleet
size, kind, seed, date, feature set) and `provenance.parameters` (every
generator setting that defines the distribution the instance is drawn
from, under descriptive names), `provenance.population` and
`provenance.routing`. The release set was generated with the settings
`value.model=every_job, objective.model=public` on top of the public feature set, nominal date
2026-06-16, at source commit `8642717998becc3991736c40a96c576b3f54a24e`. With these
records the owner can regenerate every instance byte for byte.

## How the solutions were produced

The solutions come from the owner's own solver, whose source is not part
of this release. Anyone can **verify** them (`validate.py`, `score.py`,
`SHA256SUMS`), but only the owner can **re-run** the solver that produced
them.

Each solution's `provenance` records the solver (`name`, `version` label,
`commit`), the fixed iteration budget, the random seed and the fixed
clock value it was run with, the date, the wall time (informational: the
runs are bounded by iterations, not time, so the wall time does not change
the result) and `invocation_sha256`, the SHA-256 of the full recorded
invocation. The owner keeps that record unpublished; its canonical JSON
(keys sorted, no spaces) hashes to `invocation_sha256`, so it can be shown
to be the one used.

A run is a pure function of the problem, the solver commit and the
recorded invocation: it stops after a fixed number of iterations (never
on time), runs one search thread, takes its random seed from the instance
and the date, and reads the fixed clock value instead of the computer's
clock. Re-running the recorded invocation at the recorded commit gives the
same solution byte for byte; the owner checked this by re-solving. A
better solution found later is added under a new solution id; the earlier
ones stay, and `solutions/index.csv` marks the best known one per
instance.

The record a solution is built from has these fields (a plan in the
generator's own job ids plus this record; the release build maps it to
the published ids, validates it and scores it):

| field | meaning |
|---|---|
| `instance` | the instance id the plan solves (must equal its directory) |
| `solution` | the solution id: lowercase letters, digits, '.', '_', '-' |
| `day_sha256` | SHA-256 of the day.json the solver was run on (guards against a plan of another day) |
| `solver` | {name, version, commit}: the solver and its recorded version label and commit |
| `iteration_budget` | the fixed iteration budget of the run (integer) or null |
| `random_seed` | the solver's random seed or null |
| `fixed_clock` | the fixed clock value the solver ran with (ISO 8601) or null |
| `date` | the date the solution was produced, YYYY-MM-DD |
| `wall_time_s` | wall time in seconds (informational) or null |
| `note` | one line published with the solution, or null |
| `private` | anything else of the invocation (argv, objective configuration, ...): never published, only hashed into invocation_sha256 |

All fields except `private` and `day_sha256` are published in the
solution's `provenance`.

