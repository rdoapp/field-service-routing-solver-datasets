# File formats

Version 1.1.0 of the dataset. All JSON files are UTF-8; the JSON
Schemas (draft 2020-12) in `schemas/` describe `problem.json` and the
solution files formally. PROBLEM.md gives the meaning of every field that
enters the problem. Times are whole minutes after local midnight of the
instance's date; 08:00 is 480, 16:30 is 990.

## problems/&lt;instance&gt;/problem.json

| field | type | content |
|---|---|---|
| `format` | string | always `hvac-field-service-problem` |
| `format_version` | string | `1.0`; changes when a field is added, removed or changes meaning |
| `dataset_major_version` | integer | the major version of the dataset (`VERSION`): problems never change within a major version, so a problem file is the same in every minor version |
| `instance` | string | the instance id `<region>-t<technicians, 2 digits>-<kind>-s<seed>`, e.g. `budapest-t05-full-s1` |
| `description` | string | one sentence |
| `region` | object | `name` (city) and `country` (ISO 3166-1 alpha-2) |
| `kind` | string | `full`: the queue holds far more work than the fleet can serve. `servable`: a smaller queue that one known plan serves completely (useful for debugging: its tier-1 optimum is the queue's total service minutes) |
| `date`, `timezone` | string | the planning day (YYYY-MM-DD) and its IANA time zone |
| `time_unit` | string | always `minutes after local midnight of date` |
| `matrices` | object | `n` (number of locations), `durations` and `distances` (file names, next to `problem.json`), `sha256` (`durations`, `distances`: SHA-256 of each matrix's **decompressed** CSV) |
| `locations` | array | `{index, lat, lon}` per matrix row, `index` = position; WGS 84 degrees |
| `technicians` | array | see below |
| `teams` | array | `{id, members}`; `members` lists technician ids, the first is the lead |
| `jobs` | array | see below |
| `objective` | object | `tiers`: the three tiers of PROBLEM.md section 6, in order, each `{rank, name, sense, unit}` |
| `bounds` | object | `service_minutes_max`, `priority3_service_minutes_max` (integers), `statement` (what they bound, PROBLEM.md section 7) |
| `provenance` | object | how the instance was made: `generator` (`name`, `version`, `commit`, `repository`), `instance_spec` (`region`, `technicians`, `kind`, `seed`, `date`, `features`: what the generator was asked for), `parameters` (the generator's settings that define the distribution the instance is drawn from, DATASHEET.md), `population` (source data of customer locations), `routing` (the road network and router used for the matrices) |

A technician:

| field | type | content |
|---|---|---|
| `id` | string | e.g. `t01` |
| `start_location`, `end_location` | integer | location indices |
| `shift` | `[start, end]` | minutes |
| `breaks` | array of `[start, end]` | minutes; may be empty |
| `skills` | array of strings | e.g. `["service", "fgas"]` |
| `max_route_duration_min` | integer or null | route duration limit (PROBLEM.md section 5); null: none. Null in this release |
| `max_route_distance_m` | integer or null | route distance limit in metres; null: none. Null in this release |

A job:

| field | type | content |
|---|---|---|
| `id` | string | `j0001`, `j0002`, … in queue order |
| `location` | integer | location index |
| `service_minutes` | integer | ≥ 1 |
| `windows` | array of `[start, end]` | the whole service must lie inside one; empty: any time |
| `priority` | 1, 2 or 3 | 3 is the most urgent; only priority 3 has its own objective tier |
| `value_eur` | integer | the job's value in euro, ≥ 0. **Descriptive only**: no constraint and no objective of this release uses it (PROBLEM.md section 1); it is there for value-based variants |
| `skills` | array of `{skill, count}` | the team must hold `count` members with `skill` |
| `attributes` | object | descriptive only, no constraint: `type` (`cleaning`, `washing`, `installation`, `repair`), `customer_type` (`working`, `home`, `business`), `dwelling` (`flat`, `house`, `office`), `devices` (air-conditioning units at the customer) |

Several locations may share coordinates (two customers whose addresses
snapped to one road position); they are still separate rows.

## problems/&lt;instance&gt;/durations_s.csv.gz, distances_m.csv.gz

Gzipped CSV, ASCII, no header: `n` lines of `n` comma-separated integers,
each line ending in `\n`. Row `a`, column `b` is the value from location
`a` to location `b`, in the order of `problem.json`'s `locations`.
`durations_s`: travel time in whole seconds, every value a multiple of 60
(road travel times rounded up to whole minutes). `distances_m`: road
distance in whole metres. The diagonal is 0. The matrices are not
symmetric in general. To read one in Python: `[[int(c) for c in line.split(",")]
for line in gzip.open(path, "rt")]`.

## Solutions: solutions/&lt;instance&gt;/&lt;solution&gt;.json

A solution file, whether published here or written by you:

| field | type | content |
|---|---|---|
| `format` | string | always `hvac-field-service-solution` |
| `format_version` | string | `1.0` |
| `instance` | string | the instance id |
| `solution` | string | the solution id (the file name without `.json`) |
| `routes` | array | `{team, stops}`; `stops` in visiting order, each `{job, start}`, `start` the service start in minutes. Teams that stay home are left out |
| `objective` | object | the values of PROBLEM.md section 6 as scored by `tools/score.py`: `service_minutes`, `priority3_service_minutes`, `travel_time_s`, and for information `travel_distance_m` and `jobs_served` (in no tier) |
| `provenance` | object | how the solution was produced: `solver` (`name`, `version`, `commit`), `iteration_budget`, `random_seed`, `fixed_clock` (the clock value the solver was run with, ISO 8601), `date`, `wall_time_s` (informational), `invocation_sha256` (SHA-256 of the full recorded invocation, which the owner keeps; REPRODUCE.md), `note` |

To check a solution of your own you need only `format`, `format_version`,
`instance` and `routes` (`objective` and `provenance` are filled in for
published solutions). `tools/example/example-solution.json` is such a
minimal file: an illustrative solution of one small instance, valid and
not a best-known result, there to try the tools on.

A release without solutions (as version 1.0.0) has a `solutions/`
directory holding only `README.md`, which says that solutions follow;
`solutions/index.csv` and the best-known columns of `instances.csv`
appear with the first solutions. Adding solutions never changes a file
under `problems/`, `schemas/` or `tools/`.

## solutions/index.csv, instances.csv

`solutions/index.csv` (present when the release holds solutions): one row
per published solution: `instance`,
`solution`, the three objective values, `solver`, `solver_version`, `date`,
`best_known` (`true` for the instance's best known solution under the
objective order of PROBLEM.md; among solutions equal on every tier, the
first solution id in sorted order; `false` for the others). An instance
can have several solutions: a better one found later is added under a new
solution id and the earlier ones stay.

`instances.csv`: one row per instance: `instance`, `region`, `kind`,
`technicians`, `teams`, `jobs`, `locations`, `queue_service_minutes` (all
jobs), `fleet_team_minutes` (per team, the lead's shift less the union of
the members' breaks, summed: the most service minutes the fleet could
serve with no travel) and the two bounds; when the release holds
solutions, also the best known solution's id and three objective values
(`best_solution`, `best_service_minutes`, `best_priority3_service_minutes`,
`best_travel_time_s`; empty for an instance without a solution).

## SHA256SUMS

One line per file of the release except itself, sorted by path, in the
format of `sha256sum`: the hex digest, two spaces, the path relative to the
release root. Check with `sha256sum -c SHA256SUMS`.

## A worked example

A tiny instance (not part of the release): three locations, one
technician, two jobs.

<!-- example:problem -->
```json
{
  "format": "hvac-field-service-problem",
  "format_version": "1.0",
  "dataset_major_version": 1,
  "instance": "example-t01-full-s1",
  "description": "A two-job example.",
  "region": {"name": "Budapest", "country": "HU"},
  "kind": "full",
  "date": "2026-06-16",
  "timezone": "Europe/Budapest",
  "time_unit": "minutes after local midnight of date",
  "matrices": {
    "n": 3, "durations": "durations_s.csv.gz", "distances": "distances_m.csv.gz",
    "sha256": {
      "durations": "5d97389ecff24392730ace2be406e277233db473f682bf1d32cf888fd3e6b8dd",
      "distances": "670964755dffa2d37349e5b7760d0f383ad763fd96c0fe76ec9c37b397d7f6d5"
    }
  },
  "locations": [
    {"index": 0, "lat": 47.5, "lon": 19.04},
    {"index": 1, "lat": 47.51, "lon": 19.05},
    {"index": 2, "lat": 47.49, "lon": 19.06}
  ],
  "technicians": [
    {"id": "t01", "start_location": 0, "end_location": 0, "shift": [480, 990], "breaks": [[720, 750]],
     "skills": ["service", "fgas"], "max_route_duration_min": null, "max_route_distance_m": null}
  ],
  "teams": [{"id": "team01", "members": ["t01"]}],
  "jobs": [
    {"id": "j0001", "location": 1, "service_minutes": 60, "windows": [[480, 600]], "priority": 1,
     "value_eur": 75, "skills": [{"skill": "service", "count": 1}],
     "attributes": {"type": "washing", "customer_type": "home", "dwelling": "flat", "devices": 1}},
    {"id": "j0002", "location": 2, "service_minutes": 60, "windows": [[690, 840]], "priority": 3,
     "value_eur": 110, "skills": [{"skill": "fgas", "count": 1}],
     "attributes": {"type": "repair", "customer_type": "working", "dwelling": "house", "devices": 2}}
  ],
  "objective": {
    "tiers": [
      {"rank": 1, "name": "service_minutes", "sense": "maximize", "unit": "min"},
      {"rank": 2, "name": "priority3_service_minutes", "sense": "maximize", "unit": "min"},
      {"rank": 3, "name": "travel_time_s", "sense": "minimize", "unit": "s"}
    ]
  },
  "bounds": {"service_minutes_max": 120, "priority3_service_minutes_max": 60,
             "statement": "No feasible solution serves more service minutes than service_minutes_max."},
  "provenance": {
    "generator": {"name": "by hand", "version": "1", "commit": "none", "repository": null},
    "instance_spec": {"region": "budapest", "technicians": 1, "kind": "full", "seed": 1,
                      "date": "2026-06-16", "features": ["time_windows", "skills", "breaks"]},
    "parameters": {},
    "population": {"name": "none", "url": "none",
                   "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
                   "use": "none"},
    "routing": {"engine": "none: made-up travel times"}
  }
}
```

`durations_s.csv.gz` decompressed (10, 15 and 8 minutes; 9 minutes back from 2
to 1, so the matrix is asymmetric):

<!-- example:durations -->
```
0,600,900
600,0,480
900,540,0
```

`distances_m.csv.gz` decompressed:

<!-- example:distances -->
```
0,4000,6000
4100,0,3000
6200,3100,0
```

A solution: the technician serves `j0001` at 490 (08:10) and `j0002` at
750 (12:30). `j0002`'s window opens at 690, but a service from 690 would
overlap the break (720-750), so the earliest feasible start is 750.

<!-- example:solution -->
```json
{
  "format": "hvac-field-service-solution",
  "format_version": "1.0",
  "instance": "example-t01-full-s1",
  "routes": [{"team": "team01", "stops": [{"job": "j0001", "start": 490}, {"job": "j0002", "start": 750}]}]
}
```

Its score (`python tools/score.py problem.json durations_s.csv.gz distances_m.csv.gz solution.json`):

| tier | value | how |
|---|---|---|
| `service_minutes` | 120 | 60 + 60 |
| `priority3_service_minutes` | 60 | `j0002` |
| `travel_time_s` | 1980 | 600 + 480 + 900 (depot → 1 → 2 → depot) |

`score.py` also prints, for information, the travel distance (4000 + 3000
+ 6200 = 13200 m) and the jobs served (2); the job values (75 + 110 euro)
are in no tier.

The route's duration (PROBLEM.md section 5) is 295 minutes. Starting
`j0002` at 700 instead would be reported as `in_break`; starting `j0001` at
485 as `early_start` (the technician arrives at 490).
