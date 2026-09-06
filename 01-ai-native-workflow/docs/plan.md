# Project Plan

## 1. Project Goal

Build an AI Study Project Manager that helps an individual university student turn course PDFs into a usable weekly project roadmap and receive actionable progress guidance.

## 2. MVP Features

### Feature 1 — AI Roadmap Generator

Input:
- Multiple PDF course materials
- Final project deadline

Process:
1. Upload PDFs
2. Organize PDFs into folders
3. Extract project requirements
4. Extract learning topics
5. Allow the student to review and edit the extracted information
6. Generate a chronological weekly roadmap
7. Recommend trusted external learning resources

Output:
- Weekly tasks
- Weekly learning topics
- Recommended resources

### Feature 2 — Adaptive Progress Guidance

Process:
1. Student updates task status
2. Calculate weighted progress
3. Compare actual progress against expected progress
4. Display On Track / At Risk status
5. Student asks "What should I do next?"
6. AI recommends one highest-priority action

## 3. User Flow

Create Account
→ Upload PDFs
→ Organize PDFs
→ Enter Deadline
→ AI Analysis
→ Review Requirements + Topics
→ Confirm
→ Generate Roadmap
→ Edit Roadmap
→ Complete Tasks
→ Track Progress
→ Ask "What should I do next?"
→ Complete Project
→ Reflection

## 4. Progress Calculation

Actual progress:

Progress =
Completed Task Weight / Total Task Weight × 100

Expected progress is based on elapsed time:

Expected Progress =
Elapsed Project Time / Total Project Time × 100

On Track:

Actual Progress ≥ 70% of Expected Progress

Otherwise:

At Risk

## 5. Task Status

Tasks have exactly three statuses:

- Not Started
- In Progress
- Done

Students manually update task status.

## 6. AI Next-Best-Action

The AI considers:

- Task dependencies
- Overdue tasks
- Learning gaps

The system returns exactly one recommended action with a short explanation.

## 7. MVP Data Model

User
└── Project
    ├── Folder
    │   └── PDF
    ├── Requirement
    ├── LearningTopic
    ├── Week
    │   ├── Task
    │   └── Resource
    └── Reflection

## 8. Out of Scope

- Multiple active projects
- Team collaboration
- Automatic progress detection
- Automatic task completion
- Automatic roadmap modification
- Daily planning
- Study-hour scheduling
- Weekend optimization
- Complex prioritization
- Effort estimates
- Complex user profiles
- Reflection-based personalization
- Non-PDF files
- Automatic PDF categorization
- Source citations for extracted requirements/topics

## 9. Development Order

### Phase 1 — Django Setup
- Create Django project
- Create core app
- Configure settings
- Configure URLs
- Create database models

### Phase 2 — Project Setup
- User registration/login
- Create project
- Upload PDFs
- Create/manage folders
- Enter deadline

### Phase 3 — AI Analysis
- Extract text from PDFs
- Extract requirements
- Extract learning topics
- Build review/edit interface

### Phase 4 — Roadmap
- Generate weekly roadmap
- Generate tasks
- Generate learning topics
- Recommend trusted resources
- Allow roadmap editing

### Phase 5 — Progress
- Implement task statuses
- Implement task weights
- Calculate weighted progress
- Calculate expected progress
- Display On Track / At Risk

### Phase 6 — AI Guidance
- Implement "What should I do next?"
- Consider dependencies
- Consider overdue tasks
- Consider learning gaps
- Return one recommended action

### Phase 7 — Completion
- Detect all required tasks completed
- Show completion state
- Collect reflection

### Phase 8 — Testing
- Test project creation
- Test PDF upload
- Test AI extraction
- Test roadmap generation
- Test task editing
- Test progress calculation
- Test next-best-action recommendations
- Test project completion

## 10. MVP Success Criterion

A student should be able to go from:

Course PDFs + Deadline

to:

Reviewed requirements/topics → Weekly roadmap → Progress status → One useful next action

without manually building the entire project plan from scratch.