"""Basic tests for the PawPal system."""

from pawpal_system import Pet, Task, Category, Priority


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
