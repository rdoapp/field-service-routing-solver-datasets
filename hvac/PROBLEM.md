# Problem definition

Version 1.1.0 of the dataset. This document defines the problem every
instance poses, precisely enough to write a solver and a checker from it.
`tools/validate.py` is the reference implementation: every rule below has
the rule code the validator prints when a solution breaks it, and the
validator checks nothing that is not written here. FORMAT.md describes the
files field by field.

In one sentence: a company has more waiting jobs than its technicians can
serve in one day; choose which jobs each team serves, in what order and
starting when, so that as many service minutes as possible are served,
then as many minutes of urgent (priority-3) jobs, then with as little
travel time as possible.

## 1. Data

All times are whole minutes after local midnight of the instance's `date`
(time zone `timezone`). All intervals `[a, b]` have `a < b`.

**Locations** `0 … n−1`, each with a latitude and longitude (WGS 84). The
coordinates are informational; all travel comes from the matrices.

**Matrices.** `D[a][b]` is the travel time in seconds and `M[a][b]` the
road distance in metres from location `a` to location `b`. Both are
non-negative integers with a zero diagonal; every `D[a][b]` is a multiple
of 60. Neither matrix needs to be symmetric, and neither needs to satisfy
the triangle inequality (they come from a road router). The travel time of
a leg in minutes is `τ(a, b) = D[a][b] / 60`.

**Technicians** `t`, each with a start location `start(t)`, an end location
`end(t)`, a shift `[shift_start(t), shift_end(t)]`, a list of breaks (each
an interval), a set of skills, and two optional limits
`max_route_duration_min(t)` (minutes) and `max_route_distance_m(t)`
(metres); a limit that is `null` does not apply.

**Teams** `T`, each a non-empty list of technicians, `members(T)`. Every
technician is in exactly one team. The first member is the team's **lead**
`ℓ(T)`. All members of a team share the shift, the start location and the
end location; their breaks may differ. A team works as one vehicle: it has
at most one route, and every member is present for every job on it. Write
`B(T)` for the breaks of all members of `T` together.

**Jobs** `j`, each with a location `loc(j)`, a service time `s(j) ≥ 1`
minutes, a list of time windows `W(j)` (possibly empty: no time
restriction), a priority `p(j) ∈ {1, 2, 3}`, and a list of required
skills, each with a count `n ≥ 1`.

Each job also carries descriptive data that **impose nothing and enter no
objective** in this release: its attributes (`type`, `customer_type`,
`dwelling`, `devices`) and a value in euro (`value_eur`, a non-negative
integer; DATASHEET.md says how it is drawn). The value is published so that
others can define value-based variants of the problem (for example a
prize-collecting objective); such a variant is a different problem, and
its results are not comparable with this one's.

## 2. Decision

A solution gives, for some teams, a **route**: a sequence of distinct jobs
`j_1, …, j_k` (`k ≥ 1`) with a service start `S_i` (an integer minute) for
each. A team without a route stays home. Every job is optional: a job on
no route is simply not served.

## 3. Timing of a route

Take a route of team `T` with lead `ℓ = ℓ(T)`, jobs `j_1 … j_k` and starts
`S_1 … S_k`. Its locations are `x_0 = start(ℓ)`, `x_i = loc(j_i)` for
`i = 1 … k`, and `x_{k+1} = end(ℓ)`; leg `i` (for `i = 1 … k+1`) runs from
`x_{i−1}` to `x_i` and takes `τ_i = τ(x_{i−1}, x_i)` minutes.

Legs leave as early as possible and the team waits, if it must, at the
next job. Leg `i` is **ready** at `R_1 = shift_start(ℓ)` for the first leg
and `R_i = S_{i−1} + s(j_{i−1})` (the end of the previous service)
otherwise. **No travel may overlap a break of any team member**: the leg
**leaves** at

    L_i = the earliest t ≥ R_i such that no break [b0, b1] in B(T) has t < b1 and b0 < t + τ_i

(for `τ_i = 0`, `L_i = R_i`), so a leg that would overlap a break leaves
when that break ends (and, if it then overlaps another break, when that
one ends). The leg **arrives** at `A_i = L_i + τ_i`. `A_{k+1}` is the
route's **return** time. Waiting (between an arrival and a service start)
may overlap a break.

Two intervals `[a0, a1]` and `[b0, b1]` **overlap** when `a0 < b1` and
`b0 < a1`: touching ends do not overlap.

## 4. Constraints

A solution is **feasible** when it breaks none of these rules. Rule codes
are those the validator prints.

| code | rule |
|---|---|
| `format` | The solution has the format of FORMAT.md: `routes` is a list of `{team, stops}`, each stop `{job, start}` with an integer `start`. |
| `instance` | The solution names the instance it is checked against. |
| `unknown_team` | Every route's team is a team of the instance. |
| `team_twice` | No team has more than one route. |
| `unknown_job` | Every stop's job is a job of the instance. |
| `job_twice` | No job is on more than one stop, on the same route or another. |
| `missing_skill` | For every job `j` on a route of team `T` and every required skill `(σ, n)` of `j`: at least `n` members of `T` hold `σ`. |
| `early_start` | Every service starts at or after its arrival: `S_i ≥ A_i`. |
| `outside_window` | If `W(j_i)` is not empty, the whole service lies inside one window: some `[a, b]` in `W(j_i)` has `a ≤ S_i` and `S_i + s(j_i) ≤ b`. |
| `in_break` | No service overlaps a break of any member: no `[b0, b1]` in `B(T)` overlaps `[S_i, S_i + s(j_i)]`. |
| `late_return` | The team is back by the end of the shift: `A_{k+1} ≤ shift_end(ℓ)`. |
| `route_duration` | For every member `t` of `T` with a duration limit: `duration(route) ≤ max_route_duration_min(t)` (section 5). |
| `route_distance` | For every member `t` of `T` with a distance limit: `Σ_{i=1..k+1} M[x_{i−1}][x_i] ≤ max_route_distance_m(t)`. |

Nothing else is a constraint: a route may serve any number of jobs,
services may start at any minute that satisfies the rules (early
starts are not required), and teams are independent of each other.

In this release every technician's two limits are `null`, so the last two
rules never apply; they are part of the format so later versions can set
them, and the validator implements them.

## 5. Route duration

The duration of a route is its span from departure to return, measured as
if the team left as late as its stops allow, so that waiting at a stop is
absorbed by leaving later. With the timing of section 3:

- `U` is the union of the breaks `B(T)`, as disjoint intervals.
- The **wait** before stop `i` is `w_i = (S_i − A_i) − |[A_i, S_i] ∩ U|`,
  the time between arrival and service start that is not break time.
  `Wsum_i = w_1 + … + w_i`.
- The **latest start** of stop `i` is `λ_i = min(b*, shift_end(ℓ)) −
  s(j_i)`, where `b*` is the largest end of a window of `j_i` that holds the
  service as given (`a ≤ S_i` and `S_i + s(j_i) ≤ b`); when `j_i` has no
  window, `λ_i = shift_end(ℓ) − s(j_i)`.
- The **slack** is `σ = min over i of (Wsum_i + λ_i − S_i)`.

Then

    duration(route) = A_{k+1} − L_1 − max(0, min(σ, Wsum_k))

`L_1` is the earliest departure from section 3; `min(σ, Wsum_k)` is how
much later the team could leave without any stop starting after its
latest start, capped at the waiting there is to absorb.

**Example** (the instance of FORMAT.md): one technician, shift
`[480, 990]`, a break `[720, 750]`; job `j0001` (60 min, window
`[480, 600]`) 10 min from the depot, job `j0002` (60 min, window
`[690, 840]`) 8 min from `j0001`, the depot 15 min from `j0002`. The
solution serves `j0001` at 490 and `j0002` at 750.

| stop | ready `R` | leaves `L` | arrives `A` | start `S` | wait `w` | `Wsum` | latest `λ` | `Wsum + λ − S` |
|---|---|---|---|---|---|---|---|---|
| j0001 | 480 | 480 | 490 | 490 | 0 | 0 | 600 − 60 = 540 | 50 |
| j0002 | 550 | 550 | 558 | 750 | 192 − 30 = 162 | 162 | 840 − 60 = 780 | 192 |
| return | 810 | 810 | 825 | | | | | |

`j0002` cannot start at 690, when its window opens: 690-750 would overlap
the break. Slack `σ = 50`, so the team could leave 50 minutes later; the
duration is `825 − 480 − min(50, 162) = 295` minutes (leaving at 530,
serving `j0001` at 540-600). The return at 825 is before the shift end
990, so the route is feasible. Its travel time is 600 + 480 + 900 = 1980 s.

## 6. Objective

For a feasible solution `x`, with `J(x)` the served jobs and the sums over
legs running over every route that has at least one stop (start, stops,
end; a team without a route travels nothing):

| tier | name | definition | unit | sense |
|---|---|---|---|---|
| 1 | `service_minutes` | `Σ_{j ∈ J(x)} s(j)` | minutes | maximise |
| 2 | `priority3_service_minutes` | `Σ_{j ∈ J(x), p(j) = 3} s(j)` | minutes | maximise |
| 3 | `travel_time_s` | `TT(x) = Σ_legs D[a][b]` | seconds | minimise |

All three are exact integers. Travel time counts each route's legs once,
whatever the team size. Distances (`M`) and job values enter no tier;
`tools/score.py` prints the travel distance and the number of jobs served
for information only.

**Comparison.** Solutions are ranked **lexicographically**: `x` is better
than `y` when `x` has more service minutes; on equal service minutes, more
priority-3 service minutes; on equal values of both, less travel time. Two
solutions equal on all three tiers are equally good. No weighting of tiers
is implied: a solution that serves one more service minute is better than
any that serves fewer, however much less it travels. `tools/score.py`
prints the three values and, given two solutions, which is better and
which tier decides.

Priorities 1 and 2 enter only tier 1 (as service minutes); only priority 3
has its own tier.

## 7. Bounds

Each instance carries `bounds.service_minutes_max` and
`bounds.priority3_service_minutes_max`: no feasible solution serves more
service minutes, or more priority-3 service minutes, than these values.
They come from a relaxation, not from a solution, and are usually not
attainable; read them as "at most this much".

The relaxation (proof sketch): a team `T` with `k_T` members works within
its lead's shift less the union of its members' breaks, `W_T` minutes. On
any route, each stop's incoming leg and its service lie inside that time,
outside the breaks, and do not overlap each other, so the services plus
incoming legs of a route fit in `W_T`. Let `m(j)` be a job's cheapest
possible incoming leg (from any technician's start location or any other
job's location) and `n(j)` the team size it needs (its largest skill
count). A job counts only if some team holds its skills and one of its
windows (or the shift) holds a break-free stretch as long as its service.
Then the served jobs satisfy both `Σ (s(j) + m(j)) ≤ Σ_T W_T` and `Σ n(j)
(s(j) + m(j)) ≤ Σ_T k_T W_T`, and, for each skill `σ` with `n_σ(j)` the
count job `j` needs and `h_σ(T)` the members of `T` holding it,
`Σ_{j needs σ} n_σ(j) (s(j) + m(j)) ≤ Σ_T h_σ(T) W_T`. The most service
minutes of jobs satisfying one such inequality is at most the fractional
(linear-relaxation) knapsack value, rounded down (for a skill: that value
over the jobs needing `σ`, plus the service of all counting jobs that do
not). The bound is the smallest of these values and the service of all
jobs that count. The priority-3 bound applies the same to priority-3
jobs.

## 8. What the model leaves out

Travel times are static (no time of day, no traffic), the day is a single
day with no carry-over, every job is either served whole or not at all,
there is no overtime, and a team cannot split. Section "Known limitations"
of DATASHEET.md lists the modelling assumptions behind the data.
