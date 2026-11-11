# Changelog

The dataset follows semantic versioning: problems never change within a
major version (a major version changes any byte of a problem file or
matrix); a minor version adds instances or adds or improves solutions; a
patch version changes documentation only.

## 1.1.0 (2026-11-10)

- Solutions: 60 best known solutions, one per instance (solution id
  `rdo`, solver "RDO day planner", fixed iteration budget and clock),
  with `solutions/index.csv` and the best-known columns of
  `instances.csv`. Each is validated and scored by `tools/validate.py`;
  the solver's invocation is kept by the owner and published only as its
  SHA-256.
- Documents updated for the solutions (README, DATASHEET, FORMAT,
  PROBLEM, REPRODUCE "How the solutions were produced", CITATION.cff,
  croissant.json).
- No file under `problems/`, `schemas/` or `tools/` changed.

## 1.0.0 (2026-11-10)

- First release: 60 problems (Budapest and Pécs; 5, 10, 50
  technicians; kinds `full`, `servable`; seeds 1, 2, 3, 4, 5) with upper bounds,
  problem definition, formats, datasheet, JSON Schemas, Croissant
  metadata, validator and scorer with an illustrative example
  solution.
- Solutions: none in this version; best known solutions follow in a
  later minor version, without changes to the problems.
