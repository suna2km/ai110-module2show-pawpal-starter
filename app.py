from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Category, Priority, Recurrence

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()


def _fmt(minutes: int) -> str:
    """Format minutes-since-midnight as HH:MM for display."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _task_row(t: Task) -> dict:
    """Flatten a Task into a table row for st.table."""
    return {
        "pet": t.pet.name if t.pet else "?",
        "task": t.name,
        "category": t.category.value,
        "duration (min)": t.duration,
        "priority": t.priority.name.title(),
        "preferred": _fmt(t.preferred_time) if t.preferred_time is not None else "—",
        "repeats": t.recurrence.value,
    }


# --- Persistent state: the Owner lives in the session "vault" so pets and
# --- tasks survive Streamlit's rerun-on-every-interaction model. ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_minutes_per_day=120,
        preferred_start_time=8 * 60,
    )
owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes_per_day = int(
    st.number_input(
        "Available minutes per day",
        min_value=15,
        max_value=1440,
        value=owner.available_minutes_per_day,
    )
)

st.divider()

# --- Add a Pet: the form data is handled by Owner.add_pet(Pet(...)) ---
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed", value="mixed")
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=2)
    if st.form_submit_button("Add pet"):
        owner.add_pet(Pet(pet_name, species, breed, int(age)))
        st.success(f"Added {pet_name} to {owner.name}'s pets.")

if owner.pets:
    st.write("Current pets:")
    for pet in owner.pets:
        st.write(f"- {pet.get_pet_info()}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task: routed to the chosen Pet via Pet.add_task(Task(...)) ---
st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet first, then you can assign tasks to it.")
else:
    with st.form("add_task_form"):
        target_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox("Category", [c.value for c in Category], index=0)
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", [p.name.title() for p in Priority], index=0)
        recurrence = st.selectbox("Repeats", [r.value for r in Recurrence], index=0)
        anchored = st.checkbox("Fixed time of day?", value=False)
        anchor_time = st.time_input("Preferred time", value=time(8, 0))
        if st.form_submit_button("Add task"):
            target_pet = next(p for p in owner.pets if p.name == target_pet_name)
            preferred = anchor_time.hour * 60 + anchor_time.minute if anchored else None
            target_pet.add_task(
                Task(
                    task_title,
                    Category(category),
                    int(duration),
                    Priority[priority.upper()],
                    recurrence=Recurrence(recurrence),
                    preferred_time=preferred,
                    due_date=date.today(),
                )
            )
            st.success(f"Added '{task_title}' to {target_pet_name}.")

# The Scheduler is the "brain": all task ordering/conflict logic lives there,
# so the UI just calls its methods rather than re-implementing sorting itself.
scheduler = Scheduler(owner)

if owner.get_all_tasks():
    st.markdown("#### 📋 Task List")
    sort_choice = st.radio(
        "Sort by",
        ["Time of day", "Priority"],
        horizontal=True,
    )
    ordered = (
        scheduler.sort_by_time()
        if sort_choice == "Time of day"
        else scheduler.sort_tasks_by_priority()
    )
    if ordered:
        st.caption(f"{len(ordered)} pending task(s), ordered by {sort_choice.lower()}.")
        st.table([_task_row(t) for t in ordered])
    else:
        st.success("All tasks are complete — nothing pending!", icon="✅")

    completed = owner.get_tasks(is_complete=True)
    if completed:
        with st.expander(f"Completed tasks ({len(completed)})"):
            st.table([_task_row(t) for t in completed])

st.divider()

# --- Generate Schedule: hand the Owner to the Scheduler brain ---
st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_plan()

    if not plan.scheduled_tasks:
        st.info("Nothing to schedule — add some tasks first.")
    else:
        # Headline status: green when the day is clear, amber the moment the
        # scheduler flags an overlap so the owner can't miss it.
        if plan.conflicts:
            st.warning(
                f"Heads up — {len(plan.conflicts)} scheduling conflict"
                f"{'s' if len(plan.conflicts) != 1 else ''} to resolve below.",
                icon="⚠️",
            )
        else:
            st.success("Plan generated — no conflicts. You're all set!", icon="✅")

        # At-a-glance summary of the plan.
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Tasks scheduled", len(plan.scheduled_tasks))
        col_b.metric("Time used", f"{plan.get_total_time_used()} min")
        col_c.metric("Conflicts", len(plan.conflicts))

        st.markdown("#### 🗓️ Today's Schedule")
        st.table(
            [
                {
                    "time": f"{_fmt(slot.start_time)}–{_fmt(slot.end_time)}",
                    "pet": slot.task.pet.name if slot.task.pet else "?",
                    "task": slot.task.name,
                    "duration (min)": slot.task.duration,
                }
                for slot in plan.scheduled_tasks
            ]
        )

        # Conflicts: one clearly-scoped card each, with an actionable next step —
        # far more useful to an owner than a single lumped-together error string.
        if plan.conflicts:
            st.markdown("#### ⚠️ Conflicts to resolve")
            for note in plan.conflicts:
                st.warning(note, icon="⚠️")
            st.caption(
                "To fix: shorten a task, give it a different preferred time, or "
                "mark one complete — then regenerate the plan."
            )

        with st.expander("Why this plan? (scheduler reasoning)"):
            st.info(plan.reasoning)
