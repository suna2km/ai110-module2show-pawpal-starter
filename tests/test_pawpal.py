"""Basic tests for the PawPal system."""

from datetime import date

from pawpal_system import (
    Owner, Pet, Task, Category, Priority, Scheduler, Recurrence,
    DailyPlan, ScheduledTask,
)


def _plan_with(*slots):
    plan = DailyPlan(date=date(2026, 7, 6))
    plan.scheduled_tasks = list(slots)
    return plan


def test_mark_complete_changes_status():
    task = Task("Give meds", Category.MEDS, 10, Priority.HIGH)
    assert task.is_complete is False

    task.mark_complete()

    assert task.is_complete is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Rex", "dog", "Labrador", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning walk", Category.WALK, 30, Priority.HIGH))

    assert len(pet.tasks) == 1


def test_sort_by_time_orders_by_preferred_time_with_flexible_last():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    pet = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    evening = pet.add_task(Task("Dinner", Category.FEEDING, 15, Priority.HIGH, preferred_time=18 * 60))
    morning = pet.add_task(Task("Meds", Category.MEDS, 10, Priority.HIGH, preferred_time=8 * 60))
    flexible = pet.add_task(Task("Grooming", Category.GROOMING, 45, Priority.LOW))

    ordered = Scheduler(owner).sort_by_time()

    # Anchored tasks come first in chronological order; flexible task last.
    assert ordered == [morning, evening, flexible]


def test_sort_by_time_excludes_completed_tasks():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    pet = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    done = pet.add_task(Task("Meds", Category.MEDS, 10, Priority.HIGH, preferred_time=8 * 60))
    done.mark_complete()

    assert Scheduler(owner).sort_by_time() == []


def test_one_off_task_does_not_spawn_on_complete():
    pet = Pet("Rex", "dog", "Labrador", 3)
    pet.add_task(Task("Nail trim", Category.GROOMING, 15, Priority.LOW))

    spawned = pet.tasks[0].mark_complete()

    assert spawned is None
    assert len(pet.tasks) == 1


def test_daily_task_spawns_next_day_and_attaches_to_pet():
    pet = Pet("Rex", "dog", "Labrador", 3)
    pet.add_task(
        Task("Morning walk", Category.WALK, 30, Priority.HIGH,
             recurrence=Recurrence.DAILY, due_date=date(2026, 7, 6))
    )

    spawned = pet.tasks[0].mark_complete()

    assert spawned is not None
    assert spawned.due_date == date(2026, 7, 7)
    assert spawned.is_complete is False
    assert spawned.recurrence is Recurrence.DAILY
    assert spawned in pet.tasks and spawned.pet is pet  # auto-attached


def test_weekly_recurrence_uses_timedelta_across_month_boundary():
    # timedelta(weeks=1) must roll July 30 -> August 6 correctly.
    pet = Pet("Luna", "cat", "Tabby", 5)
    pet.add_task(
        Task("Flea meds", Category.MEDS, 5, Priority.MEDIUM,
             recurrence=Recurrence.WEEKLY, due_date=date(2026, 7, 30))
    )

    spawned = pet.tasks[0].mark_complete()

    assert spawned.due_date == date(2026, 8, 6)


def test_detect_conflicts_flags_cross_pet_overlap():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    rex = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    luna = owner.add_pet(Pet("Luna", "cat", "Tabby", 5))
    plan = _plan_with(
        ScheduledTask(9 * 60, Task("Vet call", Category.MEDS, 30, Priority.HIGH, pet=rex)),
        ScheduledTask(9 * 60, Task("Playtime", Category.ENRICHMENT, 30, Priority.MEDIUM, pet=luna)),
    )

    warnings = Scheduler(owner).detect_conflicts(plan)

    assert len(warnings) == 1
    assert "Rex vs Luna" in warnings[0]


def test_detect_conflicts_flags_same_pet_overlap():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    rex = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    plan = _plan_with(
        ScheduledTask(9 * 60, Task("Walk", Category.WALK, 30, Priority.HIGH, pet=rex)),
        ScheduledTask(9 * 60 + 15, Task("Meds", Category.MEDS, 10, Priority.HIGH, pet=rex)),
    )

    warnings = Scheduler(owner).detect_conflicts(plan)

    assert len(warnings) == 1
    assert "same pet (Rex)" in warnings[0]


def test_detect_conflicts_clean_plan_returns_empty():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    rex = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    # Back-to-back, not overlapping: 09:00-09:30 then 09:30-09:40.
    plan = _plan_with(
        ScheduledTask(9 * 60, Task("Walk", Category.WALK, 30, Priority.HIGH, pet=rex)),
        ScheduledTask(9 * 60 + 30, Task("Meds", Category.MEDS, 10, Priority.HIGH, pet=rex)),
    )

    assert Scheduler(owner).detect_conflicts(plan) == []


# --- Sorting correctness ------------------------------------------------------

def test_sort_tasks_by_priority_tie_break_by_duration_then_category():
    owner = Owner("Sam", available_minutes_per_day=240, preferred_start_time=8 * 60)
    pet = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    # All HIGH so priority ties; duration breaks first, then category name.
    longer = pet.add_task(Task("Long walk", Category.WALK, 45, Priority.HIGH))
    walk = pet.add_task(Task("Quick walk", Category.WALK, 10, Priority.HIGH))
    meds = pet.add_task(Task("Meds", Category.MEDS, 10, Priority.HIGH))

    ordered = Scheduler(owner).sort_tasks_by_priority()

    # Same priority: shorter duration first; on equal duration, category
    # "meds" sorts before "walk".
    assert ordered == [meds, walk, longer]


# --- Filtering by available time ---------------------------------------------

def test_filter_keeps_high_priority_and_records_over_budget_skips():
    owner = Owner("Sam", available_minutes_per_day=40, preferred_start_time=8 * 60)
    pet = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    high = pet.add_task(Task("Meds", Category.MEDS, 30, Priority.HIGH))
    medium = pet.add_task(Task("Walk", Category.WALK, 20, Priority.MEDIUM))
    low = pet.add_task(Task("Groom", Category.GROOMING, 10, Priority.LOW))

    scheduler = Scheduler(owner)
    selected = scheduler.filter_tasks_by_available_time()

    # 30 fits, +20 would exceed the 40-min budget (skipped), +10 still fits.
    assert selected == [high, low]
    assert scheduler._skipped == [medium]


# --- Recurrence logic ---------------------------------------------------------

def test_daily_task_marks_complete_and_creates_next_days_task():
    pet = Pet("Rex", "dog", "Labrador", 3)
    walk = pet.add_task(
        Task("Morning walk", Category.WALK, 30, Priority.HIGH,
             recurrence=Recurrence.DAILY, preferred_time=8 * 60,
             due_date=date(2026, 7, 6))
    )

    spawned = walk.mark_complete()

    # Original is done; a fresh, incomplete task exists for the next day.
    assert walk.is_complete is True
    assert spawned is not None
    assert spawned.is_complete is False
    assert spawned.due_date == date(2026, 7, 7)
    assert spawned.name == walk.name and spawned.preferred_time == walk.preferred_time
    assert spawned in pet.tasks


# --- Schedule generation: happy path + edge cases -----------------------------

def test_generate_plan_places_tasks_in_chronological_order():
    # Budget spans 08:00-18:00 so both anchored times fall inside the window.
    owner = Owner("Sam", available_minutes_per_day=600, preferred_start_time=8 * 60)
    pet = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    pet.add_task(Task("Dinner", Category.FEEDING, 15, Priority.HIGH, preferred_time=12 * 60))
    pet.add_task(Task("Meds", Category.MEDS, 10, Priority.HIGH, preferred_time=8 * 60))

    plan = Scheduler(owner).generate_plan(plan_date=date(2026, 7, 6))

    starts = [st.start_time for st in plan.scheduled_tasks]
    assert starts == sorted(starts)
    assert [st.task.name for st in plan.scheduled_tasks] == ["Meds", "Dinner"]


def test_generate_plan_empty_when_no_tasks():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    owner.add_pet(Pet("Rex", "dog", "Labrador", 3))  # pet with no tasks

    plan = Scheduler(owner).generate_plan(plan_date=date(2026, 7, 6))

    assert plan.scheduled_tasks == []
    assert plan.conflicts == []


def test_two_tasks_at_same_preferred_time_are_bumped_not_conflicting():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    pet = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    pet.add_task(Task("Walk", Category.WALK, 30, Priority.HIGH, preferred_time=8 * 60))
    pet.add_task(Task("Meds", Category.MEDS, 10, Priority.HIGH, preferred_time=8 * 60))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(plan_date=date(2026, 7, 6))

    # Both placed, second slid past the first — no runtime overlap remains.
    assert len(plan.scheduled_tasks) == 2
    assert scheduler.detect_conflicts(plan) == []
    # The slide is reported as a bump note, not a hard conflict.
    assert any("moved from" in note for note in plan.conflicts)


def test_anchored_task_before_start_is_clamped_to_start():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    pet = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    pet.add_task(Task("Early walk", Category.WALK, 30, Priority.HIGH, preferred_time=6 * 60))

    plan = Scheduler(owner).generate_plan(plan_date=date(2026, 7, 6))

    # Preferred 06:00 is before the 08:00 start, so it moves up to 08:00.
    assert plan.scheduled_tasks[0].start_time == 8 * 60


def test_anchored_task_past_day_end_overflows_and_is_reported():
    owner = Owner("Sam", available_minutes_per_day=120, preferred_start_time=8 * 60)
    pet = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    # Day window is 08:00-10:00; an 18:00 task fits the budget but not the window.
    pet.add_task(Task("Evening walk", Category.WALK, 30, Priority.HIGH, preferred_time=18 * 60))

    plan = Scheduler(owner).generate_plan(plan_date=date(2026, 7, 6))

    assert plan.scheduled_tasks == []
    assert any("couldn't fit" in note for note in plan.conflicts)
