"""PawPal — pet care daily scheduling system.

Skeleton generated from diagrams/uml.mmd. Method bodies are stubs.
"""

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Owner:
    name: str
    available_hours_per_day: float
    preferred_start_time: time

    def get_available_time(self) -> float:
        """Return the owner's available time (hours) for scheduling."""
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
    category: str  # walk | feeding | meds | grooming | enrichment
    duration: int  # minutes
    priority: str  # high | medium | low
    is_recurring: bool = False

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        ...

    def get_priority(self) -> str:
        """Return the task priority."""
        ...

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        ...


@dataclass
class ScheduledTask:
    """A task placed at a specific start time within a DailyPlan."""
    start_time: time
    task: Task


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

    def is_time_slot_available(self, start_time: time, duration: int) -> bool:
        """Return True if the given slot does not overlap existing tasks."""
        ...


@dataclass
class Scheduler:
    owner: Owner
    pet: Pet
    task_list: list[Task] = field(default_factory=list)
    start_time: time | None = None

    def generate_plan(self) -> DailyPlan:
        """Build and return a DailyPlan for the day."""
        ...

    def sort_tasks_by_priority(self) -> list[Task]:
        """Return tasks ordered by priority (high -> low)."""
        ...

    def filter_tasks_by_available_time(self) -> list[Task]:
        """Return tasks that fit within the owner's available time."""
        ...

    def resolve_conflicts(self) -> None:
        """Adjust scheduling so no two tasks overlap."""
        ...

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of scheduling decisions."""
        ...
