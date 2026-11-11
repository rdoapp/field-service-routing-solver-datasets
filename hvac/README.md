# HVAC field-service planning days

Version 1.1.0 (2026-11-10). DOI: *pending, to be assigned by the owner*.

60 synthetic one-day planning problems of a company that
cleans, washes, installs and repairs air-conditioning units in
Budapest and Pécs (Hungary). The owner's best known solutions are included (60 in this version). Each problem: technicians who work
alone or in two-person teams, with shifts, lunch breaks and skills; a
queue of jobs with service times, time windows, priorities and skills;
road travel times and distances between all locations. The question each
problem asks: **which jobs does each team serve, in which order and
when**, to serve as many service minutes as possible, then as many
minutes of urgent jobs, then with the least travel.

The data is **synthetic**: no real customer, address or company is in it
(DATASHEET.md). It is meant for research on vehicle routing and
scheduling, in particular the team orienteering problem with time
windows, skills and breaks under heavy over-demand.

The instances were produced by the owner's generator, which is not published at this time; REPRODUCE.md describes how it works, and every problem records the seed and the settings it was drawn with. Outsiders cannot regenerate the problems: they are fixed files, checksummed and verifiable with the published validator.

## Quick start

```sh
sha256sum -c SHA256SUMS                                     # integrity
python tools/validate.py problems/budapest-t05-servable-s4/problem.json \
    tools/example/example-solution.json                     # check a solution
python tools/score.py problems/budapest-t05-servable-s4/problem.json \
    problems/budapest-t05-servable-s4/durations_s.csv.gz \
    problems/budapest-t05-servable-s4/distances_m.csv.gz \
    my-solution.json tools/example/example-solution.json   # score and compare
```

The tools need Python 3.9 or later and nothing else.
`tools/example/example-solution.json` is a small illustrative solution of
`budapest-t05-servable-s4` (a few jobs on one route), there to try the tools
on; it is not a good or best-known result. Write your own solution in the
solution format of FORMAT.md (only `format`, `format_version`, `instance`
and `routes` are needed), check it with `validate.py`, compare it with
`score.py`.

## The problem in brief

- Each **team** (one technician, or a crew of two) drives one route from
  its start location to its end location within the lead's shift and
  serves jobs on the way. No travel and no service may overlap a member's
  break; a leg that would leaves when the break ends.
- A **job** is optional, served at most once and whole, inside one of its
  time windows (if it has any), by a team holding the skills it needs
  (with counts: an installation needs two installers, so a crew).
- **Objective**, lexicographic: (1) maximise served service minutes;
  (2) maximise served service minutes of priority-3 jobs; (3) minimise
  total travel time.
- Each job also states a value in euro (`value_eur`). It is descriptive
  only: no rule and no objective tier of this release uses it; it lets
  others define value-based variants.

PROBLEM.md defines every rule and objective exactly; `tools/validate.py`
implements PROBLEM.md, rule by rule.

## Instances

Instance ids are `<region>-t<technicians>-<kind>-s<seed>`, for example
`pecs-t10-full-s3`. This version: regions Budapest and Pécs; fleets of
5, 10, 50 technicians; kinds `full`, `servable`; seeds 1, 2, 3, 4, 5.

- **full**: the queue holds several times more work than one day of the
  fleet can serve (compare the queue's service minutes with the fleet's
  team-minutes in the table), as a real backlog does. Choosing what to
  serve is most of the problem.
- **servable**: a smaller queue (a few jobs per technician) that one
  known plan serves completely. Its tier-1 optimum is therefore the
  queue's total service minutes; it is meant for testing and debugging a
  solver, not for ranking.

Columns: jobs in the queue; service minutes of the whole queue; the
fleet's team-minutes (per team, the lead's shift less the members'
breaks, summed: what the fleet could serve with no travel at all); the
upper bounds on served minutes and on served priority-3 minutes (PROBLEM.md
section 7; not attainable in general); and the best known solution's three objective values. The same
table is in `instances.csv`.

| instance | technicians | teams | jobs | queue service min | fleet team-min | bound min | bound priority-3 min | best known: min / p3 min / travel s |
|---|---|---|---|---|---|---|---|---|
| `budapest-t05-full-s1` | 5 | 4 | 462 | 37560 | 1920 | 1912 | 1406 | 1620 / 780 / 14280 |
| `budapest-t05-full-s2` | 5 | 4 | 462 | 37980 | 1920 | 1914 | 1406 | 1560 / 780 / 18000 |
| `budapest-t05-full-s3` | 5 | 4 | 462 | 38010 | 1920 | 1912 | 1413 | 1500 / 720 / 19860 |
| `budapest-t05-full-s4` | 5 | 4 | 462 | 37170 | 1920 | 1912 | 1412 | 1500 / 780 / 19080 |
| `budapest-t05-full-s5` | 5 | 4 | 462 | 38640 | 1920 | 1914 | 1412 | 1530 / 720 / 16440 |
| `budapest-t05-servable-s1` | 5 | 4 | 30 | 1620 | 1920 | 1620 | 0 | 1620 / 0 / 9360 |
| `budapest-t05-servable-s2` | 5 | 4 | 31 | 1530 | 1920 | 1530 | 0 | 1530 / 0 / 12480 |
| `budapest-t05-servable-s3` | 5 | 4 | 29 | 1560 | 1920 | 1560 | 0 | 1560 / 0 / 13320 |
| `budapest-t05-servable-s4` | 5 | 4 | 25 | 1560 | 1920 | 1560 | 60 | 1560 / 60 / 11760 |
| `budapest-t05-servable-s5` | 5 | 4 | 26 | 1530 | 1920 | 1530 | 0 | 1530 / 0 / 13140 |
| `budapest-t10-full-s1` | 10 | 9 | 720 | 59700 | 4320 | 4302 | 1888 | 3540 / 1140 / 36900 |
| `budapest-t10-full-s2` | 10 | 9 | 720 | 60270 | 4320 | 4303 | 1880 | 3660 / 1080 / 29520 |
| `budapest-t10-full-s3` | 10 | 9 | 720 | 58740 | 4320 | 4305 | 1885 | 3630 / 1080 / 30660 |
| `budapest-t10-full-s4` | 10 | 9 | 720 | 59580 | 4320 | 4302 | 1885 | 3510 / 1140 / 33300 |
| `budapest-t10-full-s5` | 10 | 9 | 720 | 60930 | 4320 | 4302 | 1888 | 3450 / 1140 / 39600 |
| `budapest-t10-servable-s1` | 10 | 9 | 61 | 3540 | 4320 | 3540 | 240 | 3540 / 240 / 22740 |
| `budapest-t10-servable-s2` | 10 | 9 | 62 | 3390 | 4320 | 3390 | 120 | 3390 / 120 / 26460 |
| `budapest-t10-servable-s3` | 10 | 9 | 72 | 3420 | 4320 | 3420 | 180 | 3420 / 180 / 31020 |
| `budapest-t10-servable-s4` | 10 | 9 | 68 | 3480 | 4320 | 3480 | 60 | 3480 / 60 / 24960 |
| `budapest-t10-servable-s5` | 10 | 9 | 61 | 3540 | 4320 | 3540 | 120 | 3540 / 120 / 22500 |
| `budapest-t50-full-s1` | 50 | 45 | 1350 | 105660 | 21600 | 21512 | 7740 | 18090 / 6540 / 142500 |
| `budapest-t50-full-s2` | 50 | 45 | 1350 | 112890 | 21600 | 21514 | 6360 | 17880 / 6300 / 159960 |
| `budapest-t50-full-s3` | 50 | 45 | 1350 | 109200 | 21600 | 21513 | 7800 | 17760 / 6360 / 163440 |
| `budapest-t50-full-s4` | 50 | 45 | 1350 | 107490 | 21600 | 21513 | 8400 | 18030 / 6540 / 147180 |
| `budapest-t50-full-s5` | 50 | 45 | 1350 | 116250 | 21600 | 21516 | 8160 | 17580 / 6420 / 172920 |
| `budapest-t50-servable-s1` | 50 | 45 | 335 | 17850 | 21600 | 17850 | 960 | 17850 / 960 / 94080 |
| `budapest-t50-servable-s2` | 50 | 45 | 320 | 17820 | 21600 | 17820 | 660 | 17820 / 660 / 96780 |
| `budapest-t50-servable-s3` | 50 | 45 | 329 | 17340 | 21600 | 17340 | 1140 | 17340 / 1140 / 107160 |
| `budapest-t50-servable-s4` | 50 | 45 | 337 | 17910 | 21600 | 17910 | 1320 | 17910 / 1320 / 91680 |
| `budapest-t50-servable-s5` | 50 | 45 | 321 | 17520 | 21600 | 17520 | 900 | 17520 / 900 / 100740 |
| `pecs-t05-full-s1` | 5 | 4 | 462 | 39480 | 1920 | 1914 | 1417 | 1650 / 780 / 11940 |
| `pecs-t05-full-s2` | 5 | 4 | 462 | 39870 | 1920 | 1915 | 1412 | 1560 / 780 / 12900 |
| `pecs-t05-full-s3` | 5 | 4 | 462 | 39090 | 1920 | 1914 | 1416 | 1530 / 660 / 17520 |
| `pecs-t05-full-s4` | 5 | 4 | 462 | 38370 | 1920 | 1917 | 1418 | 1500 / 660 / 18120 |
| `pecs-t05-full-s5` | 5 | 4 | 462 | 39420 | 1920 | 1913 | 1416 | 1560 / 780 / 14640 |
| `pecs-t05-servable-s1` | 5 | 4 | 28 | 1620 | 1920 | 1620 | 60 | 1620 / 60 / 8460 |
| `pecs-t05-servable-s2` | 5 | 4 | 29 | 1650 | 1920 | 1650 | 120 | 1650 / 120 / 7380 |
| `pecs-t05-servable-s3` | 5 | 4 | 30 | 1500 | 1920 | 1500 | 0 | 1500 / 0 / 14160 |
| `pecs-t05-servable-s4` | 5 | 4 | 26 | 1530 | 1920 | 1530 | 240 | 1530 / 240 / 16920 |
| `pecs-t05-servable-s5` | 5 | 4 | 26 | 1530 | 1920 | 1530 | 0 | 1530 / 0 / 12420 |
| `pecs-t10-full-s1` | 10 | 9 | 720 | 59910 | 4320 | 4303 | 1888 | 3600 / 1140 / 29160 |
| `pecs-t10-full-s2` | 10 | 9 | 720 | 62970 | 4320 | 4307 | 1889 | 3600 / 1140 / 33180 |
| `pecs-t10-full-s3` | 10 | 9 | 720 | 61830 | 4320 | 4305 | 1888 | 3660 / 900 / 28980 |
| `pecs-t10-full-s4` | 10 | 9 | 720 | 59040 | 4320 | 4307 | 1892 | 3600 / 1020 / 26700 |
| `pecs-t10-full-s5` | 10 | 9 | 720 | 61890 | 4320 | 4305 | 1890 | 3570 / 1140 / 29400 |
| `pecs-t10-servable-s1` | 10 | 9 | 73 | 3540 | 4320 | 3540 | 60 | 3540 / 60 / 23520 |
| `pecs-t10-servable-s2` | 10 | 9 | 64 | 3570 | 4320 | 3570 | 60 | 3570 / 60 / 22620 |
| `pecs-t10-servable-s3` | 10 | 9 | 71 | 3570 | 4320 | 3570 | 180 | 3570 / 180 / 24900 |
| `pecs-t10-servable-s4` | 10 | 9 | 64 | 3570 | 4320 | 3570 | 180 | 3570 / 180 / 23160 |
| `pecs-t10-servable-s5` | 10 | 9 | 66 | 3660 | 4320 | 3660 | 60 | 3660 / 60 / 16380 |
| `pecs-t50-full-s1` | 50 | 45 | 1350 | 111000 | 21600 | 21521 | 7680 | 17670 / 6240 / 153420 |
| `pecs-t50-full-s2` | 50 | 45 | 1350 | 114690 | 21600 | 21523 | 6300 | 17340 / 6000 / 177600 |
| `pecs-t50-full-s3` | 50 | 45 | 1350 | 114540 | 21600 | 21518 | 7920 | 17460 / 6300 / 164880 |
| `pecs-t50-full-s4` | 50 | 45 | 1350 | 111420 | 21600 | 21519 | 8400 | 17640 / 6300 / 151380 |
| `pecs-t50-full-s5` | 50 | 45 | 1350 | 117840 | 21600 | 21525 | 8040 | 17820 / 6420 / 143820 |
| `pecs-t50-servable-s1` | 50 | 45 | 324 | 17730 | 21600 | 17730 | 840 | 17730 / 840 / 93000 |
| `pecs-t50-servable-s2` | 50 | 45 | 321 | 17730 | 21600 | 17730 | 540 | 17730 / 540 / 99000 |
| `pecs-t50-servable-s3` | 50 | 45 | 312 | 17460 | 21600 | 17460 | 780 | 17460 / 780 / 104100 |
| `pecs-t50-servable-s4` | 50 | 45 | 316 | 17670 | 21600 | 17670 | 960 | 17670 / 960 / 95880 |
| `pecs-t50-servable-s5` | 50 | 45 | 320 | 17940 | 21600 | 17940 | 1140 | 17940 / 1140 / 76320 |

Travel matrices: OSRM 5.27.1, profile `car`, on the OpenStreetMap extract `hungary-latest.osm.pbf` of 2023-05-01.

## Best known solutions

The solutions in `solutions/` are the owner's own best known solutions,
from the solvers listed below, recorded with their provenance
(REPRODUCE.md). They are not claimed to be optimal; the bounds show how
far from optimal they may at most be in tiers 1 and 2. No other solver's
results are included.

- RDO day planner, version `git-70ad5f72ac92`

New best solutions are welcome: send the solution file (FORMAT.md); it is
checked with `tools/validate.py` and ranked with `tools/score.py`.


## Files

| path | content |
|---|---|
| `PROBLEM.md` | the formal problem definition |
| `FORMAT.md` | every file format, field by field, with a worked example |
| `DATASHEET.md` | how the data was made, what it is for and its limits |
| `REPRODUCE.md` | how to check the release and how the problems were generated and how the solutions were produced |
| `problems/<instance>/` | `problem.json`, `durations_s.csv.gz`, `distances_m.csv.gz` |
| `solutions/<instance>/<solution>.json` | best known solutions; `solutions/index.csv` lists them |
| `instances.csv` | the instance table |
| `schemas/` | JSON Schemas (draft 2020-12) of problems and solutions |
| `tools/` | `validate.py`, `score.py` (Python standard library only); `example/example-solution.json`, an illustrative solution to try them on |
| `croissant.json` | machine-readable metadata (ML Commons Croissant 1.0) |
| `CITATION.cff`, `CHANGELOG.md`, `VERSION` | citation, changes, version |
| `LICENSE`, `LICENSE-CODE` | licences of the data and of the code |
| `SHA256SUMS` | checksums of every file |

## How to cite

See `CITATION.cff` (a DOI will be added when the dataset is deposited).
Please cite the version you used (`VERSION`); every problem file carries
the major version.

## Licence

Data: Open Database License (ODbL) 1.0, contents under the Database
Contents License (DbCL) 1.0, because the travel matrices and the location
coordinates are derived from OpenStreetMap; see `LICENSE` for the
required attributions (© OpenStreetMap contributors; Eurostat). Code
(`tools/`, `schemas/`): MIT, see `LICENSE-CODE`.

## Versions

Semantic versioning of the data: problems never change within a major
version (a new major version when any byte of a problem or matrix
changes); a minor version adds instances or adds or improves solutions,
and only adds or replaces solution files and documents; a patch version
changes documentation only. `CHANGELOG.md` lists the changes.
