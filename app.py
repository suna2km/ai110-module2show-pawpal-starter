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

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("All tasks across pets:")
    st.table(
        [
            {
                "pet": t.pet.name if t.pet else "?",
                "task": t.name,
                "category": t.category.value,
                "duration (min)": t.duration,
                "priority": t.priority.name.title(),
                "preferred": _fmt(t.preferred_time) if t.preferred_time is not None else "—",
                "repeats": t.recurrence.value,
            }
            for t in all_tasks
        ]
    )

st.divider()

# --- Generate Schedule: hand the Owner to the Scheduler brain ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    if not plan.scheduled_tasks:
        st.info("Nothing to schedule — add some tasks first.")
    else:
        st.write("### Today's Schedule")
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
        st.caption(f"Total time used: {plan.get_total_time_used()} minutes")
        for note in plan.conflicts:
            st.warning(note)
        st.info(plan.reasoning)
