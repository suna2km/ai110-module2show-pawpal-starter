"""PawPal demo — build an owner with pets and tasks, then print the day's plan."""

from pawpal_system import Owner, Pet, Task, Scheduler, Category, Priority


def build_owner() -> Owner:
    # Owner has 2 hours (120 min) of care time, starting at 08:00.
    owner = Owner(
        name="Sam",
        available_minutes_per_day=120,
        preferred_start_time=8 * 60,
    )

    rex = owner.add_pet(Pet("Rex", "dog", "Labrador", 3))
    luna = owner.add_pet(Pet("Luna", "cat", "Tabby", 5))

    # At least three tasks, with different durations/priorities across pets.
    rex.add_task(Task("Morning walk", Category.WALK, 30, Priority.HIGH, is_recurring=True))
    rex.add_task(Task("Grooming", Category.GROOMING, 45, Priority.LOW))
    luna.add_task(Task("Give meds", Category.MEDS, 10, Priority.HIGH))
    luna.add_task(Task("Breakfast", Category.FEEDING, 15, Priority.MEDIUM))

    return owner


def main() -> None:
    owner = build_owner()

    print(f"Owner: {owner.name}")
    for pet in owner.pets:
        print(f"  {pet.get_pet_info()}")
    print()

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("=== Today's Schedule ===")
    plan.display_plan()


if __name__ == "__main__":
    main()
