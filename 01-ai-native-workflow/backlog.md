# AI Study Project Manager — Backlog

## Task 1 — Set Up Django Project and Core App

* Install Django in the existing virtual environment.
* Create the Django project.
* Create the core `projects` app.
* Add `projects` to `INSTALLED_APPS` in `settings.py`.
* Configure the project URLs.
* Run initial database migrations.
* Verify the Django development server runs successfully.

**Expected result:** A working Django project with the `projects` app registered and ready for development.

---

## Task 2 — Create Core Data Models

Create Django models for:

* Project
* Folder
* PDF
* Requirement
* LearningTopic
* Week
* Task
* Resource
* Reflection

Define the relationships between the models and run database migrations.

---

## Task 3 — Build Project and PDF Management

Implement the basic project setup flow:

* Create a project.
* Enter a final deadline.
* Upload multiple PDFs.
* Create folders.
* Assign PDFs to folders.
* View and remove uploaded PDFs.

---

## Task 4 — Build AI Material Analysis

Implement PDF text extraction and AI analysis to:

* Extract project requirements.
* Extract learning topics.
* Display a warning if extraction may be incomplete.
* Allow the student to edit or remove extracted requirements and topics.
* Confirm the extracted information before roadmap generation.

---

## Task 5 — Generate and Edit the Weekly Roadmap

Implement AI roadmap generation using the confirmed requirements, learning topics, and deadline.

The roadmap should contain:

* Weekly tasks.
* Weekly learning topics.
* AI-curated trusted learning resources.
* Task weights.

Allow students to add, delete, rename, move, and edit tasks.

---

## Task 6 — Implement Progress Tracking

Implement:

* `Not Started`, `In Progress`, and `Done` statuses.
* Manual task status updates.
* AI-generated task weights with student editing.
* Weighted progress calculation.
* Expected progress calculation.
* `On Track` / `At Risk` status using the 70% threshold.

---

## Task 7 — Implement AI Next-Best-Action

Add a **“What should I do next?”** feature.

The AI should consider:

* Task dependencies.
* Overdue tasks.
* Learning gaps.

Return exactly one recommended action with a short explanation.

---

## Task 8 — Project Completion and Reflection

Implement:

* Project completion when required tasks are done.
* Completion screen.
* Two-question reflection:

  * What went well?
  * What was difficult?
* Saving reflection responses.

Reflection should not affect future AI recommendations in the MVP.

---

## Task 9 — Test the MVP End-to-End

Test the complete flow:

`PDF upload → AI analysis → review → roadmap → task updates → progress → next-best-action → completion → reflection`

Fix major bugs and verify the MVP success criterion.
