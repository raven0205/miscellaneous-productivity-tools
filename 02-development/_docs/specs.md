# Project Plan: AI-Powered Expense Splitter

## 1. Overview
A full-stack expense-sharing web application that allows users to create groups, log shared expenses with custom split options, view net balances, and use an AI assistant to parse receipts automatically.

* **Frontend:** Node.js / React (or vanilla HTML/JS if preferred) for an intuitive UI.
* **Backend:** Python using **`uv`** for fast dependency management and FastAPI/Flask for API endpoints.
* **Database:** SQLite (lightweight and easy for local setup / homework deployment).
* **AI Integration:** LLM-powered receipt text parser to auto-extract expense names, amounts, and participants.

---

## 2. Core Features
* **Group & Member Management:** Create a trip/event group and add participant names.
* **Flexible Expense Entry:** Log who paid, the total amount, and choose **custom amounts/percentages** for how it's split.
* **AI Receipt Parsing:** Paste an itemized bill or receipt text to let the AI auto-fill the expense description and amount.
* **Net Balance Summary:** Real-time calculation showing each person's total net balance (e.g., who is owed money vs. who needs to pay).

---

## 3. Architecture & Tech Stack
* **Frontend (`/frontend`):** Node.js server/build tool, forms for adding expenses, dashboard for net balances.
* **Backend (`/backend`):** Python (`uv` managed), API routes for managing groups, expenses, and calling the AI model.
* **Database (`/database`):** 
  * `Groups` table (id, name)
  * `Members` table (id, group_id, name)
  * `Expenses` table (id, group_id, payer_id, description, total_amount)
  * `Splits` table (id, expense_id, member_id, owed_amount)

---

## 4. Step-by-Step Implementation Roadmap
1. **Database Setup:** Initialize SQLite and write models/tables.
2. **Backend API:** Build Python endpoints using `uv` for creating groups, adding expenses, and calculating net balances.
3. **AI Integration:** Connect a lightweight LLM endpoint in Python to parse unstructured receipt text into structured JSON.
4. **Frontend UI:** Build the Node.js frontend views (Dashboard, Add Expense form with AI button, and Balance Summary).
5. **Testing & Polish:** Run end-to-end tests and verify the UI connects smoothly with the Python backend.
