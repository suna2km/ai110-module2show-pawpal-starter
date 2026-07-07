# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design. Add a pet — The user can enter their pet's basic info (name, species, breed, age) to register them in the app. All tasks and scheduling are tied to this pet profile.
Add and edit care tasks — The user can create tasks like walks, feedings, medication, or grooming, giving each one a duration and a priority level. They can also edit or delete tasks they've already added.
Generate and view a daily plan — The user can trigger the scheduler to produce a time-ordered plan for the day, showing each task with its start time, duration, and priority, along with a brief explanation of why it was arranged that way.
- What classes did you include, and what responsibilities did you assign to each? Owner - stores the owner's name and total hours available in the day, Pet - stores the pet's name, species, breed, and age, Task - represents a single care item with a name, category, duration in minutes, priority (high/medium/low), and a recurring flag., Scheduler - takes an Owner and Pet and returns a sorted, time-slotted list of tasks, prioritizing by priority level and stopping when available time runs out.

**b. Design changes**

- Did your design change during implementation? Yes
- If yes, describe at least one change and why you made it. Priority enum (IntEnum, HIGH=0 → LOW=2) so sort_tasks_by_priority sorts naturally with no rank map.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)? (1) the owner's available time budget in minutes, (2) task priority (high/medium/low), (3) preferences in the form of a preferred time of day that anchors a task to a slot, and (4) completion status 
- How did you decide which constraints mattered most?treated time and priority as *hard* constraints and preferred time as a *soft* constraint 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes. filter_tasks_by_available_time selects tasks greedily by priority instead of solving for the optimal set that maximizes time used.
- Why is that tradeoff reasonable for this scenario? Because priority is the point. A pet owner would rather do the one high-priority task (meds) than skip it to squeeze in two low-priority ones (grooming + enrichment) that happen to fill the clock better. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)? I used it in outlining, brainstorming and helping explain what I should be doing.
- What kinds of prompts or questions were most helpful? Prompts that targeted a specific issue with a specific section of code.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is. When it suggested improvements or expansion beyond what was required.
- How did you evaluate or verify what the AI suggested? I looked at the overall aim of the project and whether the suggestion would improve it or make it complicated.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test? I focused on the Scheduler's decision-making so task state, sorting, recurrence etc.
- Why were these tests important?  because those are the branches least likely to be exercised by casual manual clicking in the UI

**b. Confidence**

- How confident are you that your scheduler works correctly? I am pretty confident
- What edge cases would you test next if you had more time? tasks longer than the entire budget, 0 or negative durations etc.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with? I am most satisfied with the logic of this project.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign? I would add task editing/deletion to the UI

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project? I learned that prompting the AI to build on my work gives better results than telling it to write something from scratch.
