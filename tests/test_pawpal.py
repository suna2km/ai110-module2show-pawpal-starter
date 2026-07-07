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
