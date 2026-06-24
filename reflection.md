# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design. Add a pet — The user can enter their pet's basic info (name, species, breed, age) to register them in the app. All tasks and scheduling are tied to this pet profile.
Add and edit care tasks — The user can create tasks like walks, feedings, medication, or grooming, giving each one a duration and a priority level. They can also edit or delete tasks they've already added.
Generate and view a daily plan — The user can trigger the scheduler to produce a time-ordered plan for the day, showing each task with its start time, duration, and priority, along with a brief explanation of why it was arranged that way.
- What classes did you include, and what responsibilities did you assign to each? Owner - stores the owner's name and total hours available in the day, Pet - stores the pet's name, species, breed, and age, Task - represents a single care item with a name, category, duration in minutes, priority (high/medium/low), and a recurring flag., Scheduler - takes an Owner and Pet and returns a sorted, time-slotted list of tasks, prioritizing by priority level and stopping when available time runs out.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
