"""PawPal — pet care daily scheduling system.

Relationships:
    Owner  1 --> * Pet          (an owner manages multiple pets)
    Pet    1 --> * Task         (a pet has its own list of care tasks)
    Scheduler --> Owner         (the "brain" reads tasks across all pets)
    Scheduler --> DailyPlan     (produces a scheduled plan for the day)

Time convention: all clock times and durations are expressed in
**minutes since midnight** (int) so slot math is plain arithmetic and
overlap checks never have to deal with timedelta/time rollover.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum, IntEnum


def _fmt(minutes: int) -> str:
    """Format minutes-since-midnight as HH:MM."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


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
class Task:
    """A single care activity for a pet."""
    name: str
    category: Category
    duration: int  # minutes
    priority: Priority
    is_recurring: bool = False
    is_complete: bool = False
    pet: Pet | None = None  # back-reference, set by Pet.add_task()

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration

    def get_priority(self) -> Priority:
        """Return the task's priority level."""
        return self.priority

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_complete = True

    def __str__(self) -> str:
        """Return a readable one-line label for the task."""
        flag = " (recurring)" if self.is_recurring else ""
        return f"{self.name} [{self.category.value}, {self.duration}m]{flag}"


@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks."""
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def get_pet_info(self) -> str:
        """Return a human-readable summary of the pet."""
        return f"{self.name} — {self.breed} {self.species}, {self.age}y ({len(self.tasks)} tasks)"

    def update_pet_info(self, **changes) -> None:
        """Update one or more pet attributes, e.g. update_pet_info(age=4)."""
        for key, value in changes.items():
            if not hasattr(self, key):
                raise AttributeError(f"Pet has no attribute {key!r}")
            setattr(self, key, value)

    def add_task(self, task: Task) -> Task:
        """Attach a task to this pet and set its back-reference."""
        task.pet = self
        self.tasks.append(task)
        return task


@dataclass
class Owner:
    """Manages multiple pets and exposes all their tasks."""
    name: str
    available_minutes_per_day: int
    preferred_start_time: int  # minutes since midnight
    pets: list[Pet] = field(default_factory=list)

    def get_available_time(self) -> int:
        """Return the owner's available time (minutes) for scheduling."""
        return self.available_minutes_per_day

    def update_preferences(
        self,
        available_minutes_per_day: int | None = None,
        preferred_start_time: int | None = None,
    ) -> None:
        """Update the owner's availability and/or preferred start time."""
        if available_minutes_per_day is not None:
            self.available_minutes_per_day = available_minutes_per_day
        if preferred_start_time is not None:
            self.preferred_start_time = preferred_start_time

    def add_pet(self, pet: Pet) -> Pet:
        """Register a pet under this owner and return it."""
        self.pets.append(pet)
        return pet

    def get_all_tasks(self) -> list[Task]:
        """Flatten every task across all pets into one list."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledTask:
    """A task placed at a specific start time within a DailyPlan."""
    start_time: int  # minutes since midnight
    task: Task

    @property
    def end_time(self) -> int:
        """Minutes since midnight at which this task finishes."""
        return self.start_time + self.task.duration


@dataclass
class DailyPlan:
    date: date
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    reasoning: str = ""

    def display_plan(self) -> None:
        """Print the formatted daily plan to the terminal."""
        print(f"PawPal plan for {self.date.isoformat()}")
        if not self.scheduled_tasks:
            print("  (nothing scheduled)")
        for st in self.scheduled_tasks:
            who = st.task.pet.name if st.task.pet else "?"
            print(f"  {_fmt(st.start_time)}-{_fmt(st.end_time)}  {who}: {st.task}")
        print(f"  total time used: {self.get_total_time_used()} min")
        if self.reasoning:
            print(f"  reasoning: {self.reasoning}")

    def get_total_time_used(self) -> int:
        """Return total scheduled minutes across all tasks."""
        return sum(st.task.duration for st in self.scheduled_tasks)

    def is_time_slot_available(self, start_time: int, duration: int) -> bool:
        """True if [start_time, start_time + duration) overlaps nothing."""
        end_time = start_time + duration
        return all(
            end_time <= st.start_time or start_time >= st.end_time
            for st in self.scheduled_tasks
        )


@dataclass
class Scheduler:
    """The 'brain': retrieves, organizes, and schedules tasks across pets."""
    owner: Owner
    start_time: int | None = None  # minutes since midnight; defaults to owner pref
    _skipped: list[Task] = field(default_factory=list, init=False)

    def generate_plan(self, plan_date: date | None = None) -> DailyPlan:
        """Build a DailyPlan: collect -> sort -> filter -> place -> explain."""
        start = self.start_time if self.start_time is not None else self.owner.preferred_start_time
        plan = DailyPlan(date=plan_date or date.today())

        selected = self.filter_tasks_by_available_time()

        cursor = start
        for task in selected:
            plan.scheduled_tasks.append(ScheduledTask(start_time=cursor, task=task))
            cursor += task.duration

        self.resolve_conflicts(plan)
        plan.reasoning = self.explain_reasoning()
        return plan

    def sort_tasks_by_priority(self) -> list[Task]:
        """Pending tasks ordered high -> low priority (shorter first on ties)."""
        pending = [t for t in self.owner.get_all_tasks() if not t.is_complete]
        return sorted(pending, key=lambda t: (t.priority.value, t.duration))

    def filter_tasks_by_available_time(self) -> list[Task]:
        """Greedily keep highest-priority tasks that fit the owner's budget.

        Records anything dropped in ``self._skipped`` for explain_reasoning().
        """
        budget = self.owner.get_available_time()
        selected: list[Task] = []
        self._skipped = []
        used = 0
        for task in self.sort_tasks_by_priority():
            if used + task.duration <= budget:
                selected.append(task)
                used += task.duration
            else:
                self._skipped.append(task)
        return selected

    def resolve_conflicts(self, plan: DailyPlan) -> None:
        """Push overlapping tasks later so slots never collide.

        Sequential placement in generate_plan is already non-overlapping;
        this is a safety pass that also fixes any manually-added tasks.
        """
        ordered = sorted(plan.scheduled_tasks, key=lambda st: st.start_time)
        cursor: int | None = None
        for st in ordered:
            if cursor is not None and st.start_time < cursor:
                st.start_time = cursor
            cursor = st.end_time
        plan.scheduled_tasks = ordered

    def explain_reasoning(self) -> str:
        """Human-readable summary of the most recent scheduling decisions."""
        parts = ["Ordered tasks by priority (high first), then packed them "
                 "back-to-back within the owner's daily time budget."]
        if self._skipped:
            names = ", ".join(t.name for t in self._skipped)
            parts.append(f"Skipped {len(self._skipped)} task(s) that didn't fit: {names}.")
        else:
            parts.append("All pending tasks fit in the available time.")
        return " ".join(parts)
