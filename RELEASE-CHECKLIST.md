# Release checklist (not part of the release)

Written by `python -m hvacgen release` next to the release directory. This
build: version 1.1.0, release date 2026-11-10, 60
problems, 60 solutions, generator source
not included, repository not set (generator source: not published).

Sources:
- ODbL 1.0: https://opendatacommons.org/licenses/odbl/1-0/
- DbCL 1.0: https://opendatacommons.org/licenses/dbcl/1-0/
- OSMF Attribution Guidelines: https://osmfoundation.org/wiki/Licence/Attribution_Guidelines
- OSMF Produced Work guideline: https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline
- OSM copyright page: https://www.openstreetmap.org/copyright
- Eurostat copyright notice: https://ec.europa.eu/eurostat/help/copyright-notice
- Eurostat population grids: https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution/population-grids

## 1. Before upload

- [ ] `python -m hvacgen release --verify <release>` passes (checksums,
      schemas, validity, scores, no private term in any file, no code but
      the two tools).
- [ ] Croissant: `mlcroissant validate --jsonld croissant.json`.
- [ ] Read `README.md`, `DATASHEET.md` and `REPRODUCE.md` once more as a
      newcomer.
