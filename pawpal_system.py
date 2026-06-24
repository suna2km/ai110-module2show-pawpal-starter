"""PawPal — pet care daily scheduling system.

Skeleton generated from diagrams/uml.mmd. Method bodies are stubs.

Time convention: all clock times and durations are expressed in
**minutes since midnight** (int) so slot math is plain arithmetic and
overlap checks never have to deal with timedelta/time rollover.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum, IntEnum


class Priority(IntEnum):
    """Lower value == higher priority, so tasks sort high -> low naturally."""
    HIGH = 0
    MEDIUM = 1
    LOW = 2


class Category(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    preferred_start_time: int  # minutes since midnight

    def get_available_time(self) -> int:
        """Return the owner's available time (minutes) for scheduling."""
        ...

    def update_preferences(self) -> None:
        """Update the owner's availability / preferred start time."""
        ...


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int

    def get_pet_info(self) -> str:
        """Return a human-readable summary of the pet."""
        ...

    def update_pet_info(self) -> None:
        """Update one or more of the pet's attributes."""
        ...


@dataclass
class Task:
    name: str
    category: Category
    duration: int  # minutes
    priority: Priority
    pet: Pet
    is_recurring: bool = False
    is_complete: bool = False

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        ...

    def get_priority(self) -> Priority:
        """Return the task priority."""
        ...

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        ...


@dataclass
class ScheduledTask:
    """A task placed at a specific start time within a DailyPlan."""
    start_time: int  # minutes since midnight
    task: Task

    @property
    def end_time(self) -> int:
        """Minutes since midnight at which this task finishes."""
        ...


@dataclass
class DailyPlan:
    date: date
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    reasoning: str = ""

    def display_plan(self) -> None:
        """Print/return the formatted daily plan."""
        ...

    def get_total_time_used(self) -> int:
        """Return total scheduled minutes across all tasks."""
        ...

    def is_time_slot_available(self, start_time: int, duration: int) -> bool:
        """Return True if [start_time, start_time + duration) does not
        overlap any already-scheduled task."""
        ...


@dataclass
class Scheduler:
    owner: Owner
    pet: Pet
    task_list: list[Task] = field(default_factory=list)
    start_time: int | None = None  # minutes since midnight

    def generate_plan(self) -> DailyPlan:
        """Build and return a DailyPlan for the day."""
        ...

    def sort_tasks_by_priority(self) -> list[Task]:
        """Return tasks ordered by priority (high -> low)."""
        ...

    def filter_tasks_by_available_time(self) -> list[Task]:
        """Return tasks that fit within the owner's available minutes."""
        ...

    def resolve_conflicts(self, plan: DailyPlan) -> None:
        """Adjust the given plan so no two tasks overlap."""
        ...

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of scheduling decisions."""
        ...
