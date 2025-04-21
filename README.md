# 🍽️ MealTracker System

**A complete meal tracking and reporting system designed for school cafeterias**, built to run across multiple terminals, support both local offline operation and centralized data storage, and provide state-compliant reporting for billing and audit purposes.

---

## 🛠️ What It Does

MealTracker is a fully featured terminal-based data system deployed in a small elementary school district. It tracks daily breakfast and lunch service, manages produce and food inventory, and generates monthly reports required for state and county reimbursement.

### ✅ Core Features

- **Multi-terminal Support** – 4 local terminals (2 per school) run MealTracker independently
- **Offline-First** – Uses SQLite for local data entry, then syncs with a central PostgreSQL server
- **Data Entry Utilities**:
  - Student meals served (breakfast + lunch)
  - Inventory: units received, leftovers, ending inventory
  - Produce tracking for salad bar
- **Automatic Calculations**:
  - Portions prepared & portions served
  - Meal category breakdown (Free / Reduced / Full Price)
- **State Reporting**:
  - Generates daily & monthly reports for submission to state/county
  - Includes breakdowns for billing (Free / Reduced / Paid meals)
- **Excel Workbook Generator**:
  - Outputs daily logs for backup filing
- **Student Database Sync**:
  - After manually downloading CSVs from Synergy (the county's SIS), scripts clean and merge:
    - Full student roster (name, ID, grade, etc.)
    - Free/Reduced eligibility records (with benefit start/end dates)
    - Cleaned data is inserted into the PostgreSQL database for use across all terminals

---

## 💻 Tech Stack

- **Python**
- **SQLite** (local terminals)
- **PostgreSQL** (central storage & reporting)
- **Pandas** for data manipulation
- **OpenPyXL / XlsxWriter** for Excel generation
- **CSV tools** for Synergy data cleanup

---

## 📁 Project Structure

mealtracker/ │ ├── local_sqlite/ │ ├── enter_orders.py │ ├── enter_leftovers_inv.py │ ├── enter_units_rcvd.py │ ├── mealtracker_local.py │ ├── student_entry.py │ ├── sync_meals_orders.py │├── sync_students_from_postgres.py │ └── menu_interface.py ← Run this on terminals │ ├── postgres_admin/ │ ├── generate_reports.py │ └── clean_student_download.py │ ├── requirements.txt ├── LICENSE └── README.md


---

## 🚀 Getting Started

### Run Locally on Terminals

```bash
cd local_sqlite
python3 menu_interface.py

---

 📊 Sample Outputs

Excel Reports (One sheet per day, plus monthly summaries)

CSV uploads for reimbursement submission

State-compliant formats for Free/Reduced/Paid meal tracking

---
👨‍💻 About the Developer
This system was designed, built, deployed, and supported entirely by one developer working inside a small school district. It demonstrates:

Strong data engineering and automation skills

Real-world problem solving

Direct support of essential services in education

Ability to manage, maintain, and document production systems
