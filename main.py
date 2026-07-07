"""PawPal demo — build an owner with pets and tasks, then print the day's plan."""

from datetime import date

from pawpal_system import (
    Owner, Pet, Task, Scheduler, Category, Priority, Recurrence,
    DailyPlan, ScheduledTask,
)


def build_owner() -> Owner:
    # Owner has 2 hours (120 min) of care time, starting at 08:00.
    owner = Owner(
        name="Sam",
        available_minutes_per_day=120,
        preferred_start_time=8 * 60,
    )

    rex = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    luna = owner.add_pet(Pet("Luna", "cat", "Tabby", 5))

    # Tasks are added deliberately OUT OF TIME ORDER (evening before morning,
    # flexible tasks mixed in) so sort_by_time() has real work to do.
    rex.add_task(Task("Evening walk", Category.WALK, 30, Priority.MEDIUM, preferred_time=18 * 60))
    rex.add_task(Task("Grooming", Category.GROOMING, 45, Priority.LOW))  # flexible
    rex.add_task(
        Task("Morning walk", Category.WALK, 30, Priority.HIGH,
             recurrence=Recurrence.DAILY, preferred_time=8 * 60, due_date=date.today())
    )
    luna.add_task(Task("Dinner", Category.FEEDING, 15, Priority.MEDIUM, preferred_time=17 * 60))
    luna.add_task(
        Task("Give meds", Category.MEDS, 10, Priority.HIGH, preferred_time=8 * 60)
    )
    luna.add_task(Task("Breakfast", Category.FEEDING, 15, Priority.MEDIUM))  # flexible

    # Mark one task done so completion filtering is visible.
    luna.tasks[-1].mark_complete()  # Breakfast already handled today

    return owner


def _print_tasks(label: str, tasks) -> None:
    print(label)
    if not tasks:
        print("  (none)")
    for t in tasks:
        who = t.pet.name if t.pet else "?"
        done = " [done]" if t.is_complete else ""
        print(f"  {who}: {t}{done}")
    print()


def main() -> None:
    owner = build_owner()
    scheduler = Scheduler(owner)

    print(f"Owner: {owner.name}")
    for pet in owner.pets:
        print(f"  {pet.get_pet_info()}")
    print()

    # --- Sorting: added out of order, now chronological (flexible tasks last) ---
    _print_tasks("=== Pending tasks sorted by time ===", scheduler.sort_by_time())

    # --- Filtering by pet name ---
    _print_tasks("=== Filter: Rex's tasks ===", owner.get_tasks(pet_name="Rex"))

    # --- Filtering by completion status ---
    _print_tasks("=== Filter: completed tasks ===", owner.get_tasks(is_complete=True))
    _print_tasks("=== Filter: pending tasks ===", owner.get_tasks(is_complete=False))

    # --- Combined filter: Luna's pending tasks ---
    _print_tasks("=== Filter: Luna's pending tasks ===",
                 owner.get_tasks(pet_name="Luna", is_complete=False))

    # --- Recurrence: completing a daily task spawns tomorrow's occurrence ---
    morning_walk = next(t for t in owner.get_tasks(pet_name="Rex") if t.name == "Morning walk")
    print("=== Completing Rex's daily 'Morning walk' ===")
    print(f"  before: due {morning_walk.due_date}, complete={morning_walk.is_complete}")
    next_walk = morning_walk.mark_complete()
    print(f"  after:  complete={morning_walk.is_complete}")
    print(f"  spawned: {next_walk} due {next_walk.due_date} (auto-added to {next_walk.pet.name})")
    print()

    plan = scheduler.generate_plan()
    print("=== Today's Schedule ===")
    plan.display_plan()
    print()

    # --- Conflict detection: hand-build a plan with two tasks at 09:00 ---
    # (One for Rex, one for Luna — the detector flags both same-pet and
    #  cross-pet overlaps without raising.)
    clash_plan = DailyPlan(date=date.today())
    rex, luna = owner.pets
    clash_plan.scheduled_tasks = [
        ScheduledTask(9 * 60, Task("Vet call", Category.MEDS, 30, Priority.HIGH, pet=rex)),
        ScheduledTask(9 * 60, Task("Playtime", Category.ENRICHMENT, 30, Priority.MEDIUM, pet=luna)),
    ]
    print("=== Conflict check on a hand-built plan ===")
    warnings = scheduler.detect_conflicts(clash_plan)
    if warnings:
        for w in warnings:
            print(f"  (!) {w}")
    else:
        print("  no conflicts")


if __name__ == "__main__":
    main()
