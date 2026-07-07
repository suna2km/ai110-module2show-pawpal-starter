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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
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
