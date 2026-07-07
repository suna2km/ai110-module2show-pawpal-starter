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
from datetime import date, timedelta
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


class Recurrence(Enum):
    """How often a task repeats. ``interval`` is the gap to the next occurrence."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"

    @property
    def interval(self) -> timedelta | None:
        """timedelta to the next occurrence, or None for one-off tasks."""
        return {
            Recurrence.DAILY: timedelta(days=1),
            Recurrence.WEEKLY: timedelta(weeks=1),
        }.get(self)


@dataclass
class Task:
    """A single care activity for a pet."""
    name: str
    category: Category
    duration: int  # minutes
    priority: Priority
    recurrence: Recurrence = Recurrence.NONE
    is_complete: bool = False
    preferred_time: int | None = None  # minutes since midnight; None = flexible
    due_date: date | None = None  # the day this instance is scheduled for
    pet: Pet | None = None  # back-reference, set by Pet.add_task()

    @property
    def is_recurring(self) -> bool:
        """True if this task repeats on some interval."""
        return self.recurrence is not Recurrence.NONE

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration

    def get_priority(self) -> Priority:
        """Return the task's priority level."""
        return self.priority

    def mark_complete(self) -> Task | None:
        """Mark this task done; if it recurs, spawn the next occurrence.

        Returns the newly-created next-occurrence Task (also attached to the
        same pet), or None for one-off tasks.
        """
        self.is_complete = True
        return self._spawn_next_occurrence()

    def _spawn_next_occurrence(self) -> Task | None:
        """Create the next dated instance of a recurring task.

        Uses ``timedelta`` so calendar boundaries are handled correctly:
        a DAILY task due Jan 31 rolls to Feb 1, and WEEKLY spans month/year
        ends and leap days without any manual day-counting.
        """
        interval = self.recurrence.interval
        if interval is None:
            return None  # one-off task, nothing to repeat
        base = self.due_date or date.today()
        next_task = Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            recurrence=self.recurrence,
            preferred_time=self.preferred_time,
            due_date=base + interval,
        )
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task

    def __str__(self) -> str:
        """Return a readable one-line label for the task."""
        flag = f" ({self.recurrence.value})" if self.is_recurring else ""
        anchor = f" @{_fmt(self.preferred_time)}" if self.preferred_time is not None else ""
        return f"{self.name} [{self.category.value}, {self.duration}m]{anchor}{flag}"


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

    def get_tasks(
        self,
        pet_name: str | None = None,
        is_complete: bool | None = None,
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Each filter is optional: pass ``None`` (the default) to ignore it.
        e.g. ``get_tasks(pet_name="Rex", is_complete=False)`` returns Rex's
        pending tasks only.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet is not None and t.pet.name == pet_name]
        if is_complete is not None:
            tasks = [t for t in tasks if t.is_complete == is_complete]
        return tasks


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
    conflicts: list[str] = field(default_factory=list)

    def display_plan(self) -> None:
        """Print the formatted daily plan to the terminal."""
        print(f"PawPal plan for {self.date.isoformat()}")
        if not self.scheduled_tasks:
            print("  (nothing scheduled)")
        for st in self.scheduled_tasks:
            who = st.task.pet.name if st.task.pet else "?"
            print(f"  {_fmt(st.start_time)}-{_fmt(st.end_time)}  {who}: {st.task}")
        print(f"  total time used: {self.get_total_time_used()} min")
        for note in self.conflicts:
            print(f"  (!) {note}")
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

    def earliest_slot(self, not_before: int, duration: int) -> int:
        """Earliest start time >= ``not_before`` whose slot overlaps nothing.

        Walks the already-placed tasks in time order, sliding the candidate
        start past any task it would collide with. Returns the first gap wide
        enough for ``duration``.
        """
        candidate = not_before
        for st in sorted(self.scheduled_tasks, key=lambda s: s.start_time):
            if candidate + duration <= st.start_time:
                break  # fits in the gap before this task
            candidate = max(candidate, st.end_time)
        return candidate


@dataclass
class Scheduler:
    """The 'brain': retrieves, organizes, and schedules tasks across pets."""
    owner: Owner
    start_time: int | None = None  # minutes since midnight; defaults to owner pref
    _skipped: list[Task] = field(default_factory=list, init=False)
    _bumped: list[tuple[Task, int, int]] = field(default_factory=list, init=False)
    _overflow: list[Task] = field(default_factory=list, init=False)

    def generate_plan(self, plan_date: date | None = None) -> DailyPlan:
        """Build a DailyPlan: collect -> sort -> filter -> place -> explain.

        Placement honors each task's ``preferred_time`` when set, sliding it
        later only as far as needed to avoid an overlap (recording the bump),
        then fills the remaining gaps with flexible tasks in priority order.
        """
        start = self.start_time if self.start_time is not None else self.owner.preferred_start_time
        day_end = start + self.owner.get_available_time()
        plan = DailyPlan(date=plan_date or date.today())

        selected = self.filter_tasks_by_available_time()
        anchored = sorted(
            (t for t in selected if t.preferred_time is not None),
            key=lambda t: t.preferred_time,
        )
        flexible = [t for t in selected if t.preferred_time is None]

        self._bumped = []
        self._overflow = []

        # Time-anchored tasks first: they reserve their slots so flexible
        # tasks flow around them.
        for task in anchored:
            desired = max(task.preferred_time, start)
            slot_start = plan.earliest_slot(desired, task.duration)
            if slot_start + task.duration > day_end:
                self._overflow.append(task)
                continue
            if slot_start > desired:
                self._bumped.append((task, desired, slot_start))
            plan.scheduled_tasks.append(ScheduledTask(start_time=slot_start, task=task))

        # Flexible tasks (already priority-ordered) backfill the gaps.
        for task in flexible:
            slot_start = plan.earliest_slot(start, task.duration)
            if slot_start + task.duration > day_end:
                self._overflow.append(task)
                continue
            plan.scheduled_tasks.append(ScheduledTask(start_time=slot_start, task=task))

        plan.scheduled_tasks.sort(key=lambda st: st.start_time)
        # Placement is overlap-free by construction; run the detector anyway as
        # a safety net that also catches any manually-added slots.
        plan.conflicts = self._describe_conflicts() + self.detect_conflicts(plan)
        plan.reasoning = self.explain_reasoning()
        return plan

    def sort_tasks_by_priority(self) -> list[Task]:
        """Pending tasks ordered high -> low priority (shorter first on ties)."""
        pending = [t for t in self.owner.get_all_tasks() if not t.is_complete]
        return sorted(pending, key=lambda t: (t.priority.value, t.duration, t.category.value))

    def sort_by_time(self) -> list[Task]:
        """Pending tasks ordered by preferred time; flexible tasks (None) last.

        ``preferred_time`` is minutes since midnight, so a plain numeric key
        sorts chronologically. ``None`` maps to +infinity so unanchored tasks
        fall to the end rather than raising on a None-vs-int comparison.
        """
        pending = [t for t in self.owner.get_all_tasks() if not t.is_complete]
        return sorted(
            pending,
            key=lambda t: t.preferred_time if t.preferred_time is not None else float("inf"),
        )

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

    def detect_conflicts(self, plan: DailyPlan) -> list[str]:
        """Return warning messages for any two tasks scheduled at the same time.

        Lightweight, non-throwing overlap check: a plain pairwise scan over the
        plan's slots. An empty list means the plan is clean. Two slots overlap
        when one starts before the other ends; the message notes whether the
        clash is for the same pet or across different pets.
        """
        warnings: list[str] = []
        slots = sorted(plan.scheduled_tasks, key=lambda s: s.start_time)
        for i, a in enumerate(slots):
            for b in slots[i + 1:]:
                # Sorted by start, so a.start_time <= b.start_time here.
                if b.start_time >= a.end_time:
                    break  # b and every later slot start after a ends
                warnings.append(self._conflict_message(a, b))
        return warnings

    @staticmethod
    def _conflict_message(a: ScheduledTask, b: ScheduledTask) -> str:
        """Format a single overlap between two scheduled tasks."""
        who_a = a.task.pet.name if a.task.pet else "?"
        who_b = b.task.pet.name if b.task.pet else "?"
        same_pet = a.task.pet is not None and a.task.pet is b.task.pet
        scope = f"same pet ({who_a})" if same_pet else f"{who_a} vs {who_b}"
        return (
            f"Conflict [{scope}]: '{a.task.name}' "
            f"({_fmt(a.start_time)}-{_fmt(a.end_time)}) overlaps '{b.task.name}' "
            f"({_fmt(b.start_time)}-{_fmt(b.end_time)})."
        )

    def _describe_conflicts(self) -> list[str]:
        """Human-readable notes about bumped and unplaceable tasks."""
        notes = []
        for task, desired, actual in self._bumped:
            notes.append(
                f"{task.name} moved from {_fmt(desired)} to {_fmt(actual)} "
                f"to avoid an overlap."
            )
        for task in self._overflow:
            notes.append(f"{task.name} couldn't fit before the day's time ran out.")
        return notes

    def explain_reasoning(self) -> str:
        """Human-readable summary of the most recent scheduling decisions."""
        parts = ["Placed time-anchored tasks at their preferred times, then "
                 "filled the gaps with the highest-priority tasks that fit the "
                 "owner's daily time budget."]
        if self._skipped:
            names = ", ".join(t.name for t in self._skipped)
            parts.append(f"Skipped {len(self._skipped)} task(s) over budget: {names}.")
        else:
            parts.append("All pending tasks fit in the available time.")
        return " ".join(parts)
