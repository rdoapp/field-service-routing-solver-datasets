#!/usr/bin/env python3
"""Score solutions of an HVAC field-service planning problem (PROBLEM.md "Objective").

Usage:
    python score.py PROBLEM.json DURATIONS.csv.gz DISTANCES.csv.gz SOLUTION.json [OTHER.json]

Prints the three objective values of SOLUTION (and, for information, the
travel distance and the number of jobs served). With a second solution, prints its values too and which of
the two is better under the lexicographic order of the objective, naming
the tier that decides. A solution that breaks a rule is not scored: its
violations are printed and the exit status is 1. Exit status 2: a file
cannot be read.

Every tier is an exact integer. Job values (value_eur) are not part of the
objective and are not scored.

Needs validate.py from the same directory; Python standard library only.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path


def _validator():
    """validate.py from beside this file, executed without writing a bytecode cache."""
    path = Path(__file__).resolve().parent / "validate.py"
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as e:
        raise SystemExit(f"error: cannot read {path}: {e}") from None
    module = types.ModuleType("hvac_validate")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def main(argv: list[str] | None = None) -> int:
    v = _validator()
    args = sys.argv[1:] if argv is None else argv
    if len(args) not in (4, 5) or any(a in ("-h", "--help") for a in args):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    problem_path, durations, distances, *solutions = args
    try:
        inst, problems = v.load(problem_path, durations, distances)
        if problems:
            for line in problems:
                print(f"{problem_path}: {line}")
            return 1
        scores = []
        for path in solutions:
            sol = v.read_json(path)
            violations = v.check_solution(inst, sol)
            if violations:
                for line in violations:
                    print(f"{path}: {line}")
                return 1
            values = v.objective(inst, sol)
            scores.append(values)
            print(f"{path}")
            for name, sense in v.TIERS:
                print(f"  {name:<26} {values[name]:>14}  ({'maximise' if sense > 0 else 'minimise'})")
            print(f"  {'travel_distance_m':<26} {values['travel_distance_m']:>14}")
            print(f"  {'jobs_served':<26} {values['jobs_served']:>14}")
    except v.InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if len(scores) == 2:
        a, b = scores
        order = v.compare(a, b)
        if order == 0:
            print("equal on every tier")
        else:
            tier = next(name for name, _ in v.TIERS if a[name] != b[name])
            better = solutions[0] if order > 0 else solutions[1]
            print(f"better: {better} (decided by {tier})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
