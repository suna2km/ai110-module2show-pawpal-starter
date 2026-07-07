# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

The scheduling engine in `pawpal_system.py` implements:

- **Priority sorting** — orders tasks high → low priority, breaking ties by shorter duration and then category name for a stable, predictable order.
- **Sorting by time** — arranges tasks chronologically by their preferred time of day, with flexible (un-anchored) tasks pushed to the end.
- **Time-budget filtering** — greedily selects the highest-priority tasks that fit within the owner's available minutes, and records which tasks were skipped for over-budget.
- **Preferred-time anchoring with auto-bumping** — places time-anchored tasks at their requested time, sliding them to the next free slot only as far as needed to avoid an overlap (and reporting the bump).
- **Gap-filling placement** — flows flexible tasks into the remaining gaps around anchored tasks, keeping the day packed without collisions.
- **Overflow handling** — tasks that can't fit before the day's time runs out are flagged rather than silently dropped.
- **Conflict warnings** — a non-throwing pairwise scan detects same-time overlaps and returns clear messages, distinguishing same-pet clashes from cross-pet ones.
- **Daily & weekly recurrence** — completing a recurring task automatically spawns its next occurrence using `timedelta`, so day/week rollovers stay correct across month, year, and leap-day boundaries.
- **Task filtering** — query tasks by pet name and/or completion status, composable in a single call.
- **Explainable plans** — every generated plan includes a plain-language summary of why tasks were chosen and ordered.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Owner: Sam
  Rex — Labrador dog, 3y (2 tasks)
  Luna — Tabby cat, 5y (2 tasks)

=== Today's Schedule ===
PawPal plan for 2026-07-06
  08:00-08:10  Luna: Give meds [meds, 10m]
  08:10-08:40  Rex: Morning walk [walk, 30m] (recurring)
  08:40-08:55  Luna: Breakfast [feeding, 15m]
  08:55-09:40  Rex: Grooming [grooming, 45m]
  total time used: 100 min
  reasoning: Ordered tasks by priority (high first), then packed them back-to-back within the owner's daily time budget. All pending tasks fit in the available time.  ...
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`) covers the core scheduling behaviors and their edge cases:

- **Sorting** — chronological order by `preferred_time` (flexible tasks last), and the priority order with duration/category tiebreakers.
- **Filtering** — greedily keeping the highest-priority tasks that fit the time budget while recording what was skipped.
- **Recurrence** — completing a `DAILY`/`WEEKLY` task marks it done and spawns the next occurrence for the following day/week, correctly rolling across month boundaries.
- **Conflict detection** — flagging same-time overlaps (both same-pet and cross-pet) and returning empty for back-to-back, non-overlapping plans.
- **Schedule generation edge cases** — an empty plan when a pet has no tasks, two tasks at the same preferred time being bumped apart (not left conflicting), anchored times before the start clamping to the start, and tasks past the day's window overflowing.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.0.3, pluggy-1.6.0
rootdir: ...\ai110-module2show-pawpal-starter
collected 18 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  5%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 11%]
tests/test_pawpal.py::test_sort_by_time_orders_by_preferred_time_with_flexible_last PASSED [ 16%]
tests/test_pawpal.py::test_sort_by_time_excludes_completed_tasks PASSED  [ 22%]
tests/test_pawpal.py::test_one_off_task_does_not_spawn_on_complete PASSED [ 27%]
tests/test_pawpal.py::test_daily_task_spawns_next_day_and_attaches_to_pet PASSED [ 33%]
tests/test_pawpal.py::test_weekly_recurrence_uses_timedelta_across_month_boundary PASSED [ 38%]
tests/test_pawpal.py::test_detect_conflicts_flags_cross_pet_overlap PASSED [ 44%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_pet_overlap PASSED [ 50%]
tests/test_pawpal.py::test_detect_conflicts_clean_plan_returns_empty PASSED [ 55%]
tests/test_pawpal.py::test_sort_tasks_by_priority_tie_break_by_duration_then_category PASSED [ 61%]
tests/test_pawpal.py::test_filter_keeps_high_priority_and_records_over_budget_skips PASSED [ 66%]
tests/test_pawpal.py::test_daily_task_marks_complete_and_creates_next_days_task PASSED [ 72%]
tests/test_pawpal.py::test_generate_plan_places_tasks_in_chronological_order PASSED [ 77%]
tests/test_pawpal.py::test_generate_plan_empty_when_no_tasks PASSED      [ 83%]
tests/test_pawpal.py::test_two_tasks_at_same_preferred_time_are_bumped_not_conflicting PASSED [ 88%]
tests/test_pawpal.py::test_anchored_task_before_start_is_clamped_to_start PASSED [ 94%]
tests/test_pawpal.py::test_anchored_task_past_day_end_overflows_and_is_reported PASSED [100%]

============================= 18 passed in 0.11s ==============================
```
Confidence Level: 4

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| **Sorting** | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks_by_priority()` | By `preferred_time` (flexible tasks last via `float("inf")` key), or high→low priority with duration/category tiebreakers. |
| **Filtering** | `Owner.get_tasks(pet_name, is_complete)`, `Scheduler.filter_tasks_by_available_time()` | Compose filters by pet and/or completion status; greedily keep the highest-priority tasks that fit the time budget. |
| **Conflict detection** | `Scheduler.detect_conflicts()`, `DailyPlan.earliest_slot()` | Non-throwing pairwise scan returns warning strings (notes same-pet vs. cross-pet); placement slides tasks into the first free slot to avoid collisions. |
| **Recurring tasks** | `Task.mark_complete()` → `Task._spawn_next_occurrence()` | Completing a `DAILY`/`WEEKLY` task auto-creates the next occurrence via `timedelta`, so month/year/leap boundaries are correct (Jul 30 → Aug 6). |

## 📸 Demo Walkthrough

### Main UI features

The Streamlit app (`app.py`) is organized top-to-bottom into four sections:

- **Owner** — set the owner's name and total available minutes per day (the scheduling time budget).
- **Add a Pet** — a form to register a pet (name, species, breed, age). Added pets appear in a live "Current pets" list.
- **Add a Task** — a form to attach a task to a chosen pet: title, category, duration, priority, recurrence, and an optional fixed time of day. `Category`, `Priority`, and `Recurrence` are drawn straight from the enums, so only valid values can be submitted.
- **Task List** — shows all pending tasks, re-orderable on the fly by **Time of day** or **Priority**, with completed tasks tucked into an expander.
- **Build Schedule** — a single **Generate schedule** button that runs the scheduler and renders the day's plan, at-a-glance metrics, and any conflict warnings.

All of this persists in `st.session_state`, so pets and tasks survive Streamlit's rerun-on-every-interaction behavior.

### Example workflow

1. **Set up the owner** — enter a name and, say, 120 available minutes.
2. **Add a pet** — fill the "Add a Pet" form (e.g. *Rex, dog, Labrador, 3*) and submit; Rex appears under "Current pets."
3. **Add a task** — in "Add a Task," pick Rex, enter *Morning walk*, category `walk`, 30 min, priority `High`, recurrence `daily`, and a fixed time of 08:00; submit.
4. **Add a few more** — repeat for other tasks/pets (e.g. Luna's meds at 08:00, dinner at 17:00).
5. **Review the task list** — toggle the sort between *Time of day* and *Priority* to see the ordering change.
6. **Generate the schedule** — click **Generate schedule** to see today's plan, total time used, and any warnings.

### Key Scheduler behaviors shown

- **Sorting** — the task list flips between chronological order (`sort_by_time()`, flexible tasks last) and priority order (`sort_tasks_by_priority()`, with duration/category tiebreakers).
- **Time-budget filtering** — with only 120 minutes available, lower-priority tasks that don't fit are skipped and explained in the reasoning line.
- **Anchoring & auto-bumping** — two tasks both requesting 08:00 don't collide; the scheduler slides one to the next free slot and reports the bump.
- **Overflow** — tasks that can't fit before the day's time runs out are flagged rather than dropped silently.
- **Conflict warnings** — same-time overlaps are surfaced as amber warnings, distinguishing same-pet from cross-pet clashes.
- **Recurrence** — completing Rex's daily walk spawns the next occurrence for the following day.

### Sample CLI output (`python main.py`)

```
Owner: Sam
  Rex — Labrador dog, 3y (3 tasks)
  Luna — Tabby cat, 5y (3 tasks)

=== Pending tasks sorted by time ===
  Rex: Morning walk [walk, 30m] @08:00 (daily)
  Luna: Give meds [meds, 10m] @08:00
  Luna: Dinner [feeding, 15m] @17:00
  Rex: Evening walk [walk, 30m] @18:00
  Rex: Grooming [grooming, 45m]

=== Filter: Rex's tasks ===
  Rex: Evening walk [walk, 30m] @18:00
  Rex: Grooming [grooming, 45m]
  Rex: Morning walk [walk, 30m] @08:00 (daily)

=== Filter: completed tasks ===
  Luna: Breakfast [feeding, 15m] [done]

=== Filter: pending tasks ===
  Rex: Evening walk [walk, 30m] @18:00
  Rex: Grooming [grooming, 45m]
  Rex: Morning walk [walk, 30m] @08:00 (daily)
  Luna: Dinner [feeding, 15m] @17:00
  Luna: Give meds [meds, 10m] @08:00

=== Filter: Luna's pending tasks ===
  Luna: Dinner [feeding, 15m] @17:00
  Luna: Give meds [meds, 10m] @08:00

=== Completing Rex's daily 'Morning walk' ===
  before: due 2026-07-06, complete=False
  after:  complete=True
  spawned: Morning walk [walk, 30m] @08:00 (daily) due 2026-07-07 (auto-added to Rex)

=== Today's Schedule ===
PawPal plan for 2026-07-06
  08:00-08:10  Luna: Give meds [meds, 10m] @08:00
  08:10-08:40  Rex: Morning walk [walk, 30m] @08:00 (daily)
  total time used: 40 min
  (!) Morning walk moved from 08:00 to 08:10 to avoid an overlap.
  (!) Dinner couldn't fit before the day's time ran out.
  (!) Evening walk couldn't fit before the day's time ran out.
  reasoning: Placed time-anchored tasks at their preferred times, then filled the gaps with the highest-priority tasks that fit the owner's daily time budget. Skipped 1 task(s) over budget: Grooming.

=== Conflict check on a hand-built plan ===
  (!) Conflict [Rex vs Luna]: 'Vet call' (09:00-09:30) overlaps 'Playtime' (09:00-09:30).
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
