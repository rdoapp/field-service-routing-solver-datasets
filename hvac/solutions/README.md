# Solutions

The owner's best known solutions, version 1.1.0: 60
solution files, one directory per instance, `<solution>.json` each
(FORMAT.md). `index.csv` lists every solution with its three objective
values (PROBLEM.md section 6), solver and date, and marks the best known
one per instance (`best_known`); `../instances.csv` names it too. A
better solution found later is added under a new solution id; earlier
solutions stay.

Solvers:

- RDO day planner, version `git-70ad5f72ac92`

Every solution here was checked with `../tools/validate.py` and scored
with `../tools/score.py` when the release was built; the scores in each
file and in `index.csv` are those of `score.py`. Solutions are not claimed
to be optimal. How they were produced: `../REPRODUCE.md`.
