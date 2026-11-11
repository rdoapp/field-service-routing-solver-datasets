<p align="center">
  <a href="https://rdo-app.com">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/rdo-logo-dark.svg">
      <img src="assets/rdo-logo-light.svg" alt="RDO" width="225">
    </picture>
  </a>
</p>

<h1 align="center">Field-service routing solver datasets</h1>

<p align="center">
  Open benchmark problems for the <a href="https://rdo-app.com"><b>RDO</b></a> field-service day planner
</p>

<p align="center">
  <a href="https://rdo-app.com"><img alt="rdo-app.com" src="https://img.shields.io/badge/rdo--app.com-E85D2A?style=flat-square"></a>
  <a href="hvac/"><img alt="hvac dataset v1.1.0" src="https://img.shields.io/badge/hvac-v1.1.0-16130F?style=flat-square"></a>
  <a href="hvac/LICENSE"><img alt="Data licence: ODbL 1.0" src="https://img.shields.io/badge/data-ODbL%201.0-16130F?style=flat-square"></a>
  <a href="hvac/LICENSE-CODE"><img alt="Code licence: MIT" src="https://img.shields.io/badge/code-MIT-16130F?style=flat-square"></a>
</p>

---

Open benchmark datasets for field-service routing and scheduling,
published by the team behind the [RDO](https://rdo-app.com) day planner.

RDO plans the working day of field-service companies: which technician or
crew visits which customer, in which order and when. This repository holds
the problem sets we use to measure that solver. We publish them so that
anyone can test their own solvers on the same problems, compare results
against ours, and check every number we report.

Each dataset is a fixed, versioned release. It contains synthetic problem
instances on real road networks, a formal problem definition, file formats,
best known solutions, and a validator and scorer that need only the Python
standard library.

## Datasets

| dataset | version | instances | what it models |
|---|---|---|---|
| [`hvac/`](hvac/) | 1.1.0 | 60 | One planning day of an air-conditioning service company in Budapest and Pécs (Hungary) |

Browse the datasets on the [project page](https://rdoapp.github.io/field-service-routing-solver-datasets/),
or see the best known solutions on a map in the
[solutions demo](https://rdoapp.github.io/field-service-routing-solver-solutions-demo/).

More datasets (other trades, regions and problem variants) will be added as
sibling directories. Each one is self-contained and has its own README,
licence, changelog and version.

## Why these datasets exist

Public vehicle-routing benchmarks such as Solomon, Gehring–Homberger and
the VRPTW libraries are clean and well studied. They also leave out much of
what makes a real field-service day hard. The problems here keep those
parts:

- **Heavy over-demand.** The backlog holds several times more work than the
  fleet can serve in one day, so deciding *what to serve* is most of the
  problem (a team orienteering problem, not a "visit everyone" VRP).
- **Skills with counts.** Some jobs need two qualified installers, so they
  can only be served by a two-person crew.
- **Breaks that interrupt travel.** No driving or service may overlap a
  technician's lunch break.
- **Multiple time windows, priorities and shifts.**
- **Real road travel times and distances** from OpenStreetMap, routed with
  OSRM, instead of Euclidean distances.
- **A lexicographic objective**: serve as many service minutes as possible,
  then as many urgent minutes as possible, then travel as little as
  possible.

We use these instances to track the RDO solver's quality and speed from
release to release. The published best known solutions are its results,
so you can measure any other solver against them on the same terms.

## The HVAC dataset at a glance

60 one-day problems: 2 regions (Budapest, Pécs) × 3 fleet sizes (5, 10 and
50 technicians) × 2 kinds × 5 seeds. The instance id spells this out:
`<region>-t<technicians>-<kind>-s<seed>`, for example `pecs-t10-full-s3`.

- **`full`**: a realistic backlog of 460 to 1,350 jobs, far more than the
  fleet can serve. Use these for ranking solvers.
- **`servable`**: a smaller queue that one known plan serves completely, so
  the tier-1 optimum is known. Use these for testing and debugging a solver.

Each instance directory holds `problem.json` (locations, technicians, teams,
jobs, objective and upper bounds) and two gzipped n × n CSV matrices:
`durations_s.csv.gz` (travel seconds) and `distances_m.csv.gz` (metres).

Start with these documents:

| document | read it for |
|---|---|
| [`hvac/README.md`](hvac/README.md) | overview, the full instance table with bounds and best known results |
| [`hvac/PROBLEM.md`](hvac/PROBLEM.md) | the exact rules and objective |
| [`hvac/FORMAT.md`](hvac/FORMAT.md) | every field of the problem and solution files, with a worked example |
| [`hvac/DATASHEET.md`](hvac/DATASHEET.md) | how the data was made, which parts are real data and which are assumptions, intended uses and limits |
| [`hvac/REPRODUCE.md`](hvac/REPRODUCE.md) | how to verify a copy, how the problems were generated and how the solutions were produced |
| [`hvac/instances.csv`](hvac/instances.csv) | the instance table as CSV |
| [`hvac/croissant.json`](hvac/croissant.json) | machine-readable metadata (ML Commons Croissant 1.0) |

## Quick start

```sh
git clone https://github.com/rdoapp/field-service-routing-solver-datasets.git
cd field-service-routing-solver-datasets/hvac

sha256sum -c SHA256SUMS                       # verify every file

# check a solution against every rule of PROBLEM.md
python tools/validate.py problems/budapest-t05-servable-s4/problem.json \
    tools/example/example-solution.json

# score your solution and compare it with another one
python tools/score.py problems/budapest-t05-servable-s4/problem.json \
    problems/budapest-t05-servable-s4/durations_s.csv.gz \
    problems/budapest-t05-servable-s4/distances_m.csv.gz \
    my-solution.json solutions/budapest-t05-servable-s4/rdo.json
```

The tools need Python 3.9 or later and no other packages. A solution needs
only four fields: `format`, `format_version`, `instance` and `routes` (see
FORMAT.md).

## How the data is made

The instances are **synthetic**. They contain no real customer, address,
person or company. They are built to look like a real working day:

1. **Customers** are placed at random in populated 1 km cells of the
   Eurostat Census 2021 population grid, in proportion to population, then
   snapped to the nearest road.
2. **Jobs** (cleaning, washing, installation, repair) get service times,
   time windows, priorities, required skills and a descriptive euro value
   from modelled distributions.
3. **The fleet** gets depots, shifts, lunch breaks, skills, and two-person
   installation crews.
4. **Travel matrices** come from OSRM 5.27.1 (car profile) on a fixed
   OpenStreetMap extract of Hungary.
5. **Upper bounds** on the first two objective tiers are computed for every
   instance, so you can see how far any solution can be from optimal.

Every problem file records its seed and all the generator settings it was
drawn with (`provenance`). The generator itself is not published at this
time, so the problems are distributed as fixed, checksummed files. Always
benchmark against the files as published. DATASHEET.md lists, element by
element, which inputs come from real data and which are modelling
assumptions.

## Best known solutions and submitting yours

`hvac/solutions/` contains one best known solution per instance, produced
by the RDO day planner with a fixed iteration budget. They are not claimed
to be optimal. The bounds in `instances.csv` show how much room is left.

Found a better solution? Open an issue or a pull request with the solution
file. We check it with `tools/validate.py`, rank it with `tools/score.py`,
and add it under its own solution id in the next minor version, credited
to you. Earlier solutions are kept.

## Repository layout

```
.
├── index.html       landing page (GitHub Pages)
├── README.md        this file
├── assets/          RDO logo
└── hvac/            HVAC field-service planning days (v1.1.0)
    ├── problems/    60 instances: problem.json + travel matrices
    ├── solutions/   best known solutions, index.csv
    ├── schemas/     JSON Schemas (draft 2020-12) for problems and solutions
    ├── tools/       validate.py, score.py, an example solution
    └── *.md, *.csv, *.json, LICENSE*, SHA256SUMS, VERSION
```

## Versioning

Each dataset uses semantic versioning of its data:

- **major**: any byte of a problem or matrix changes;
- **minor**: instances are added, or solutions are added or improved;
- **patch**: documentation only.

Problems never change within a major version, so results reported against
`hvac` 1.x remain comparable. Each problem file carries its major version.
Please state the version you used.

## Licence

- **Data**: [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/),
  contents under the [Database Contents License (DbCL) 1.0](https://opendatacommons.org/licenses/dbcl/1-0/),
  because the coordinates and travel matrices are derived from
  OpenStreetMap. The required attributions are
  © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)
  and Eurostat; see each dataset's `LICENSE`.
- **Code** (`tools/`, `schemas/`): MIT, see each dataset's `LICENSE-CODE`.

## Citation

If you use a dataset in published work, please cite it using its
`CITATION.cff` (for example [`hvac/CITATION.cff`](hvac/CITATION.cff)) and
state the version. A DOI will be added when the dataset is deposited.

---

<p align="center">
  <a href="https://rdo-app.com">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/rdo-logo-dark.svg">
      <img src="assets/rdo-logo-light.svg" alt="RDO" width="90">
    </picture>
  </a><br>
  <sub>Made by the <a href="https://rdo-app.com">RDO</a> team. The RDO name and logo are not covered by the dataset or code licences.</sub>
</p>
