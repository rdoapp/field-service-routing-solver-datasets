# Tools

Two standalone programs, Python 3.9 or later, standard library only. Keep
them in the same directory (`score.py` loads `validate.py` from beside
itself).

## Try them

`example/example-solution.json` is a small illustrative solution of
`budapest-t05-servable-s4` (a few jobs on one route). It is valid, and it is
not a good or best-known result: it is there to try the tools on.

```sh
python validate.py ../problems/budapest-t05-servable-s4/problem.json example/example-solution.json
python score.py ../problems/budapest-t05-servable-s4/problem.json \
    ../problems/budapest-t05-servable-s4/durations_s.csv.gz ../problems/budapest-t05-servable-s4/distances_m.csv.gz \
    example/example-solution.json
```

To compare a solution of your own with it, pass both files to
`score.py`; it prints which one is better and which tier decides.

## validate.py

```sh
python validate.py PROBLEM.json [SOLUTION.json ...]
python validate.py PROBLEM.json --durations D.csv.gz --distances M.csv.gz [SOLUTION.json ...]
```

Checks the problem (structure; matrices square, non-negative, zero
diagonal, durations in whole minutes; ids, teams, locations consistent)
and then each solution against every rule of `../PROBLEM.md`. Each
violation is one line `<file>: <rule code>: <detail>`, the rule codes of
PROBLEM.md section 4. A valid solution prints its three objective values.
The matrices are found next to `PROBLEM.json` under the names its
`matrices` block gives, unless `--durations` and `--distances` are passed.
Exit status: 0 all valid, 1 a rule is broken, 2 a file cannot be read.

`validate.py` is the reference implementation of PROBLEM.md. Its functions
can be imported (`load`, `check_solution`, `objective`, `compare`).

## score.py

```sh
python score.py PROBLEM.json DURATIONS.csv.gz DISTANCES.csv.gz SOLUTION.json [OTHER.json]
```

Prints the three objective values of a solution (and, for information,
its travel distance and number of jobs served); with a second solution,
also which one is better and which tier decides. A solution that breaks a
rule is not scored (exit status 1). Every tier is an exact integer; job
values are not scored.
