#!/usr/bin/env python3
"""Reference validator of the HVAC field-service planning problems (PROBLEM.md).

Usage:
    python validate.py PROBLEM.json [SOLUTION.json ...]
    python validate.py PROBLEM.json --durations D.csv.gz --distances M.csv.gz [SOLUTION.json ...]

Checks the problem (its structure and its matrices), then each solution
against every rule of PROBLEM.md, and prints each solution's objective
values. The matrices are read from the files named in the problem's
``matrices`` block, next to PROBLEM.json, unless --durations and
--distances are given.

Exit status: 0 when the problem and every solution are valid, 1 when any
rule is violated, 2 when a file cannot be read or parsed.

This file is the reference implementation of PROBLEM.md: every rule there
is implemented here, under the rule code printed with each violation. It
uses the Python standard library only (Python 3.9 or later).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sys
from pathlib import Path

PROBLEM_FORMAT = "hvac-field-service-problem"
SOLUTION_FORMAT = "hvac-field-service-solution"
FORMAT_VERSION = "1.0"

# Objective tiers in comparison order: (name, +1 maximise / -1 minimise).
TIERS = (("service_minutes", 1), ("priority3_service_minutes", 1), ("travel_time_s", -1))

# Rule codes of PROBLEM.md section "Constraints" (solutions) and "Problem data" (problems).
SOLUTION_RULES = ("format", "instance", "unknown_team", "team_twice", "unknown_job", "job_twice",
                  "early_start", "outside_window", "in_break", "late_return", "missing_skill",
                  "route_duration", "route_distance")


class InputError(Exception):
    """A file that cannot be read or parsed at all (exit status 2)."""


# ---------------------------------------------------------------------------------------------
# Reading


def read_json(path: str | Path) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise InputError(f"{path}: {e.strerror or e}") from None
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise InputError(f"{path}: not JSON: {e}") from None
    if not isinstance(data, dict):
        raise InputError(f"{path}: the top level must be a JSON object")
    return data


def read_matrix(path: str | Path) -> list[list[int]]:
    """A gzipped CSV matrix: one row per line, comma-separated integers, no header."""
    try:
        with open(path, "rb") as f:
            text = gzip.decompress(f.read()).decode("ascii")
    except OSError as e:
        raise InputError(f"{path}: {getattr(e, 'strerror', None) or e}") from None
    except (UnicodeDecodeError, EOFError) as e:
        raise InputError(f"{path}: not a gzipped ASCII CSV: {e}") from None
    rows: list[list[int]] = []
    for k, row in enumerate(csv.reader(io.StringIO(text))):
        try:
            rows.append([int(cell) for cell in row])
        except ValueError:
            raise InputError(f"{path}: row {k} holds a cell that is not an integer") from None
    return rows


def matrix_paths(problem_path: str | Path, problem: dict) -> tuple[Path, Path]:
    block = problem.get("matrices")
    if not isinstance(block, dict) or not isinstance(block.get("durations"), str) \
            or not isinstance(block.get("distances"), str):
        raise InputError(f"{problem_path}: no matrices block naming the durations and distances files")
    base = Path(problem_path).parent
    return base / block["durations"], base / block["distances"]


# ---------------------------------------------------------------------------------------------
# Problem checks


def _is_int(v: object) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _interval(v: object) -> bool:
    return isinstance(v, list) and len(v) == 2 and all(map(_is_int, v)) and v[0] < v[1]


def check_problem(problem: dict, dur: list[list[int]], dist: list[list[int]]) -> list[str]:
    """Every inconsistency of the problem data and its matrices; empty when it is well formed."""
    out: list[str] = []

    def bad(msg: str) -> None:
        out.append(f"problem: {msg}")

    if problem.get("format") != PROBLEM_FORMAT:
        bad(f"format must be {PROBLEM_FORMAT!r}")
    if problem.get("format_version") != FORMAT_VERSION:
        bad(f"format_version must be {FORMAT_VERSION!r}, got {problem.get('format_version')!r}")
    for key in ("instance", "locations", "technicians", "teams", "jobs", "objective"):
        if key not in problem:
            bad(f"missing {key}")
    if out:
        return out

    locations = problem["locations"]
    n = len(locations)
    for k, loc in enumerate(locations):
        if not isinstance(loc, dict) or loc.get("index") != k:
            bad(f"locations[{k}] must have index {k}")
        elif not all(isinstance(loc.get(c), (int, float)) and not isinstance(loc.get(c), bool)
                     for c in ("lat", "lon")):
            bad(f"locations[{k}] needs numeric lat and lon")
    if problem.get("matrices", {}).get("n") != n:
        bad(f"matrices.n must equal the number of locations ({n})")
    for name, m in (("durations", dur), ("distances", dist)):
        if len(m) != n or any(len(row) != n for row in m):
            bad(f"the {name} matrix must be {n} x {n}")
            continue
        for i, row in enumerate(m):
            if row[i] != 0:
                bad(f"{name}[{i}][{i}] must be 0")
            for j, v in enumerate(row):
                if v < 0:
                    bad(f"{name}[{i}][{j}] is negative")
                elif name == "durations" and v % 60:
                    bad(f"durations[{i}][{j}] = {v} is not a multiple of 60 seconds")

    def loc_ok(v: object) -> bool:
        return _is_int(v) and 0 <= v < n

    techs: dict[str, dict] = {}
    for t in problem["technicians"]:
        tid = t.get("id")
        if not isinstance(tid, str) or tid in techs:
            bad(f"technician id {tid!r} is missing or not unique")
            continue
        techs[tid] = t
        if not (loc_ok(t.get("start_location")) and loc_ok(t.get("end_location"))):
            bad(f"technician {tid}: start_location and end_location must be location indices")
        if not _interval(t.get("shift")):
            bad(f"technician {tid}: shift must be [start, end] with start < end")
        if not isinstance(t.get("breaks"), list) or not all(map(_interval, t["breaks"])):
            bad(f"technician {tid}: breaks must be a list of [start, end] with start < end")
        if not isinstance(t.get("skills"), list) or not all(isinstance(s, str) for s in t["skills"]):
            bad(f"technician {tid}: skills must be a list of strings")
        for key in ("max_route_duration_min", "max_route_distance_m"):
            v = t.get(key)
            if v is not None and not (_is_int(v) and v >= 0):
                bad(f"technician {tid}: {key} must be null or a non-negative integer")
    if out:
        return out

    seen_members: dict[str, str] = {}
    team_ids: set[str] = set()
    for team in problem["teams"]:
        tid = team.get("id")
        if not isinstance(tid, str) or tid in team_ids:
            bad(f"team id {tid!r} is missing or not unique")
            continue
        team_ids.add(tid)
        members = team.get("members")
        if not isinstance(members, list) or not members:
            bad(f"team {tid}: members must be a non-empty list")
            continue
        for m in members:
            if m not in techs:
                bad(f"team {tid}: member {m!r} is not a technician")
            elif m in seen_members:
                bad(f"team {tid}: technician {m} is already in team {seen_members[m]}")
            else:
                seen_members[m] = tid
        known = [techs[m] for m in members if m in techs]
        for key in ("shift", "start_location", "end_location"):
            if len({json.dumps(t[key]) for t in known}) > 1:
                bad(f"team {tid}: members must share {key}")
    for t in techs:
        if t not in seen_members:
            bad(f"technician {t} is in no team")

    job_ids: set[str] = set()
    for job in problem["jobs"]:
        jid = job.get("id")
        if not isinstance(jid, str) or jid in job_ids:
            bad(f"job id {jid!r} is missing or not unique")
            continue
        job_ids.add(jid)
        if not loc_ok(job.get("location")):
            bad(f"job {jid}: location must be a location index")
        if not (_is_int(job.get("service_minutes")) and job["service_minutes"] > 0):
            bad(f"job {jid}: service_minutes must be a positive integer")
        if not isinstance(job.get("windows"), list) or not all(map(_interval, job["windows"])):
            bad(f"job {jid}: windows must be a list of [start, end] with start < end")
        if job.get("priority") not in (1, 2, 3):
            bad(f"job {jid}: priority must be 1, 2 or 3")
        if not (_is_int(job.get("value_eur")) and job["value_eur"] >= 0):
            bad(f"job {jid}: value_eur must be a non-negative integer")
        skills = job.get("skills")
        if not isinstance(skills, list) or not all(
                isinstance(s, dict) and isinstance(s.get("skill"), str) and _is_int(s.get("count"))
                and s["count"] >= 1 for s in skills):
            bad(f"job {jid}: skills must be a list of {{skill, count >= 1}}")
        elif len({s["skill"] for s in skills}) != len(skills):
            bad(f"job {jid}: a skill is listed twice")

    tiers = problem["objective"].get("tiers") if isinstance(problem["objective"], dict) else None
    names = [t.get("name") for t in tiers] if isinstance(tiers, list) and all(isinstance(t, dict) for t in tiers) \
        else None
    if names != [name for name, _ in TIERS]:
        bad(f"objective.tiers must name {', '.join(name for name, _ in TIERS)} in this order, got {names}")
    return out


# ---------------------------------------------------------------------------------------------
# Timing (PROBLEM.md "Timing")


def _overlaps(a0: int, a1: int, b0: int, b1: int) -> bool:
    """Whether the open intervals (a0, a1) and (b0, b1) share a moment."""
    return a0 < b1 and b0 < a1


def depart_time(ready: int, leg: int, breaks: list[tuple[int, int]]) -> int:
    """The earliest moment t >= ready at which a leg of ``leg`` minutes overlaps no break.

    A leg of 0 minutes leaves at ``ready``. Moving to the end of a break the
    leg would overlap never skips a moment that overlaps none, so the loop
    ends at the earliest such moment.
    """
    t = ready
    moved = leg > 0
    while moved:
        moved = False
        for b0, b1 in breaks:
            if _overlaps(t, t + leg, b0, b1):
                t, moved = b1, True
    return t


def merged(breaks: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """The union of the breaks as sorted disjoint intervals (touching ones joined)."""
    out: list[list[int]] = []
    for b0, b1 in sorted(breaks):
        if out and b0 <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b1)
        else:
            out.append([b0, b1])
    return [(a, b) for a, b in out]


class Instance:
    """A problem with its matrices, indexed for checking solutions."""

    def __init__(self, problem: dict, dur: list[list[int]], dist: list[list[int]]) -> None:
        self.problem, self.dur, self.dist = problem, dur, dist
        self.tech = {t["id"]: t for t in problem["technicians"]}
        self.team = {t["id"]: t for t in problem["teams"]}
        self.job = {j["id"]: j for j in problem["jobs"]}

    def leg(self, a: int, b: int) -> int:
        """Travel minutes from location a to b (the matrix's seconds / 60)."""
        return -(-self.dur[a][b] // 60)

    def crew(self, team_id: str) -> list[dict]:
        return [self.tech[m] for m in self.team[team_id]["members"]]

    def timing(self, team_id: str, stops: list[dict]) -> dict:
        """The route's legs (leave, arrive) to each stop and back, as PROBLEM.md "Timing" defines them."""
        crew = self.crew(team_id)
        lead = crew[0]
        breaks = [(b[0], b[1]) for t in crew for b in t["breaks"]]
        here, ready = lead["start_location"], lead["shift"][0]
        legs: list[tuple[int, int]] = []
        for target, stop in [*((self.job[s["job"]]["location"], s) for s in stops), (lead["end_location"], None)]:
            leg = self.leg(here, target)
            leave = depart_time(ready, leg, breaks)
            legs.append((leave, leave + leg))
            if stop is not None:
                here, ready = target, stop["start"] + self.job[stop["job"]]["service_minutes"]
        return {"legs": legs, "back": legs[-1][1], "breaks": breaks, "lead": lead}

    def duration(self, team_id: str, stops: list[dict]) -> int:
        """The route duration of PROBLEM.md "Route duration": the span less the wait that leaving later absorbs."""
        t = self.timing(team_id, stops)
        legs, lead = t["legs"], t["lead"]
        shift_end = lead["shift"][1]
        union = merged(t["breaks"])
        waited, slack = 0, None
        for s, (_, arrive) in zip(stops, legs):
            job, start = self.job[s["job"]], s["start"]
            service = job["service_minutes"]
            waited += max(0, start - arrive) - sum(max(0, min(b1, start) - max(b0, arrive)) for b0, b1 in union)
            holding = [b for a, b in job["windows"] if a <= start and start + service <= b]
            latest = (min(max(holding), shift_end) if holding else shift_end) - service
            here = waited + latest - start
            slack = here if slack is None else min(slack, here)
        return t["back"] - legs[0][0] - max(0, min(slack, waited))

    def path(self, team_id: str, stops: list[dict]) -> list[int]:
        lead = self.crew(team_id)[0]
        return [lead["start_location"], *(self.job[s["job"]]["location"] for s in stops), lead["end_location"]]


# ---------------------------------------------------------------------------------------------
# Solution checks and objective


def _structure(sol: dict) -> list[str]:
    """Format violations of the solution's shape; empty when routes/stops are well formed."""
    out = []
    if sol.get("format") != SOLUTION_FORMAT:
        out.append(f"format: format must be {SOLUTION_FORMAT!r}")
    if sol.get("format_version") != FORMAT_VERSION:
        out.append(f"format: format_version must be {FORMAT_VERSION!r}")
    routes = sol.get("routes")
    if not isinstance(routes, list):
        return out + ["format: routes must be a list"]
    for k, r in enumerate(routes):
        if not isinstance(r, dict) or not isinstance(r.get("team"), str) or not isinstance(r.get("stops"), list):
            out.append(f"format: routes[{k}] must be {{team: string, stops: list}}")
            continue
        for i, s in enumerate(r["stops"]):
            if not isinstance(s, dict) or not isinstance(s.get("job"), str) or not _is_int(s.get("start")):
                out.append(f"format: routes[{k}].stops[{i}] must be {{job: string, start: integer}}")
    return out


def check_solution(inst: Instance, sol: dict) -> list[str]:
    """One ``"<rule code>: <detail>"`` line per violation; empty when the solution is feasible."""
    out = _structure(sol)
    if any(v.startswith("format: routes") for v in out):
        return out
    if sol.get("instance") != inst.problem["instance"]:
        out.append(f"instance: the solution is for {sol.get('instance')!r}, "
                   f"the problem is {inst.problem['instance']!r}")

    placed: dict[str, str] = {}
    teams_seen: set[str] = set()
    for r in sol["routes"]:
        tid = r["team"]
        if tid not in inst.team:
            out.append(f"unknown_team: team {tid} is not a team of the problem")
        elif tid in teams_seen:
            out.append(f"team_twice: team {tid} has more than one route")
        teams_seen.add(tid)
        for s in r["stops"]:
            jid = s["job"]
            if jid not in inst.job:
                out.append(f"unknown_job: team {tid} job {jid} is not a job of the problem")
            elif jid in placed:
                out.append(f"job_twice: team {tid} job {jid} is already on team {placed[jid]}")
            else:
                placed[jid] = tid

    timed: set[str] = set()
    for r in sol["routes"]:
        tid, stops = r["team"], r["stops"]
        if tid not in inst.team or tid in timed or not stops or any(s["job"] not in inst.job for s in stops):
            continue
        timed.add(tid)
        out += _route(inst, tid, stops)
    return out


def _route(inst: Instance, tid: str, stops: list[dict]) -> list[str]:
    out = []
    crew = inst.crew(tid)
    t = inst.timing(tid, stops)
    legs, lead = t["legs"], t["lead"]
    for s in stops:
        job = inst.job[s["job"]]
        for need in job["skills"]:
            held = sum(need["skill"] in m["skills"] for m in crew)
            if held < need["count"]:
                out.append(f"missing_skill: team {tid} job {job['id']} needs {need['count']} x "
                           f"{need['skill']}, the team holds {held}")
    for s, (_, arrive) in zip(stops, legs):
        job, start = inst.job[s["job"]], s["start"]
        end = start + job["service_minutes"]
        if start < arrive:
            out.append(f"early_start: team {tid} job {job['id']} starts at {start}, before its arrival at {arrive}")
        if job["windows"] and not any(a <= start and end <= b for a, b in job["windows"]):
            out.append(f"outside_window: team {tid} job {job['id']} serves {start}-{end}, "
                       f"outside {job['windows']}")
        for m in crew:
            for b0, b1 in m["breaks"]:
                if _overlaps(start, end, b0, b1):
                    out.append(f"in_break: team {tid} job {job['id']} serves {start}-{end}, "
                               f"overlapping {m['id']}'s break {b0}-{b1}")
    if t["back"] > lead["shift"][1]:
        out.append(f"late_return: team {tid} returns at {t['back']}, after the shift end {lead['shift'][1]}")
    minutes = inst.duration(tid, stops)
    path = inst.path(tid, stops)
    metres = sum(inst.dist[a][b] for a, b in zip(path, path[1:]))
    for m in crew:
        limit = m.get("max_route_duration_min")
        if limit is not None and minutes > limit:
            out.append(f"route_duration: team {tid} route lasts {minutes} min, more than {m['id']}'s {limit}")
        limit = m.get("max_route_distance_m")
        if limit is not None and metres > limit:
            out.append(f"route_distance: team {tid} route is {metres} m, more than {m['id']}'s {limit}")
    return out


def objective(inst: Instance, sol: dict) -> dict:
    """The objective values of PROBLEM.md "Objective" (the solution must be well formed)."""
    served = [inst.job[s["job"]] for r in sol["routes"] for s in r["stops"]]
    travel_s = distance_m = 0
    for r in sol["routes"]:
        if not r["stops"]:
            continue
        path = inst.path(r["team"], r["stops"])
        travel_s += sum(inst.dur[a][b] for a, b in zip(path, path[1:]))
        distance_m += sum(inst.dist[a][b] for a, b in zip(path, path[1:]))
    return {
        "service_minutes": sum(j["service_minutes"] for j in served),
        "priority3_service_minutes": sum(j["service_minutes"] for j in served if j["priority"] == 3),
        "travel_time_s": travel_s,
        "travel_distance_m": distance_m,
        "jobs_served": len(served),
    }


def compare(a: dict, b: dict) -> int:
    """1 when objective values ``a`` are better than ``b``, -1 when worse, 0 when equal on every tier."""
    for name, sense in TIERS:
        if a[name] != b[name]:
            return 1 if (a[name] - b[name]) * sense > 0 else -1
    return 0


# ---------------------------------------------------------------------------------------------
# Command line


def load(problem_path: str | Path, durations: str | Path | None = None,
         distances: str | Path | None = None) -> tuple[Instance, list[str]]:
    """The instance and its problem violations (empty when well formed)."""
    problem = read_json(problem_path)
    if durations is None or distances is None:
        d0, d1 = matrix_paths(problem_path, problem)
        durations, distances = durations or d0, distances or d1
    dur, dist = read_matrix(durations), read_matrix(distances)
    violations = check_problem(problem, dur, dist)
    return Instance(problem, dur, dist), violations


def format_objective(values: dict) -> str:
    return (f"service_minutes={values['service_minutes']} "
            f"priority3_service_minutes={values['priority3_service_minutes']} "
            f"travel_time_s={values['travel_time_s']}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate an HVAC field-service problem and its solutions.")
    p.add_argument("problem")
    p.add_argument("solutions", nargs="*")
    p.add_argument("--durations", help="durations matrix (default: as named in the problem, next to it)")
    p.add_argument("--distances", help="distances matrix (default: as named in the problem, next to it)")
    args = p.parse_args(argv)
    try:
        inst, problems = load(args.problem, args.durations, args.distances)
        failed = bool(problems)
        for line in problems:
            print(f"{args.problem}: {line}")
        if failed:
            return 1
        print(f"{args.problem}: problem valid ({len(inst.job)} jobs, {len(inst.team)} teams)")
        for path in args.solutions:
            sol = read_json(path)
            violations = check_solution(inst, sol)
            for line in violations:
                print(f"{path}: {line}")
            if violations:
                failed = True
            else:
                print(f"{path}: valid; {format_objective(objective(inst, sol))}")
        return 1 if failed else 0
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
