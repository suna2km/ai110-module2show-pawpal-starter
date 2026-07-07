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

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| **Sorting** | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks_by_priority()` | By `preferred_time` (flexible tasks last via `float("inf")` key), or high→low priority with duration/category tiebreakers. |
| **Filtering** | `Owner.get_tasks(pet_name, is_complete)`, `Scheduler.filter_tasks_by_available_time()` | Compose filters by pet and/or completion status; greedily keep the highest-priority tasks that fit the time budget. |
| **Conflict detection** | `Scheduler.detect_conflicts()`, `DailyPlan.earliest_slot()` | Non-throwing pairwise scan returns warning strings (notes same-pet vs. cross-pet); placement slides tasks into the first free slot to avoid collisions. |
| **Recurring tasks** | `Task.mark_complete()` → `Task._spawn_next_occurrence()` | Completing a `DAILY`/`WEEKLY` task auto-creates the next occurrence via `timedelta`, so month/year/leap boundaries are correct (Jul 30 → Aug 6). |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
