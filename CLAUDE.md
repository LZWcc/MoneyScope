# CLAUDE.md

## Project Overview

This project is `MoneyScope`, a Python course project.

Project name:

```text
MoneyScope：基于 Python 的个人消费记录与数据分析系统
```

The goal is to build a small but complete personal finance recording and consumption analysis system. The project should focus on Python implementation, SQLite persistence, data analysis, visualization, clean code, and clear documentation.

## Tech Stack

Use the following stack by default:

```text
Python 3.10+
Streamlit
SQLite
pandas
plotly
```

Do not switch to Flask, FastAPI, Django, MySQL, PostgreSQL, or a separate frontend framework unless the user explicitly asks.

## Course Requirements

The project must satisfy these requirements:

1. Use at least one Python technology or library not taught in class.
2. Persist data using SQLite, CSV, JSON, or files.
3. Include exception handling for common errors.
4. Use object-oriented design and define at least two meaningful classes.
5. Add docstrings for functions and classes.
6. Add necessary comments for key logic.
7. Maintain an `AI_LOG.md` file with prompts, AI outputs, manual modifications, and reflections.
8. Keep clear Git commit history with meaningful messages.
9. Prepare README, project report, PPT outline, screenshots, and demo video materials.

## Project Scope

Build a stable MVP first. Do not over-engineer.

Required MVP features:

1. Add income and expense records.
2. Store records in SQLite.
3. View all transaction records.
4. Filter records by date, category, and type.
5. Show monthly income, expense, and balance.
6. Show category expense distribution.
7. Show monthly trend chart.
8. Support CSV import and export.
9. Provide simple budget warning.
10. Provide clear error messages in the UI.

Optional features, only after MVP is stable:

1. Automatic category classification by keywords.
2. Data backup and restore.
3. Yearly summary report.
4. Abnormal expense reminder.
5. More polished dashboard layout.

## File Responsibilities

### `app/main.py`

Streamlit entry file. Build the page layout, call service functions, display forms, tables, and charts. Do not put database SQL directly here.

### `app/database.py`

SQLite database layer. Connect to SQLite, initialize database tables, provide reusable database helpers, and handle database connection errors.

### `app/models.py`

Data models and classes.

Recommended classes:

```python
class Transaction:
    """Represents one income or expense transaction."""

class Budget:
    """Represents monthly or category budget settings."""
```

### `app/services.py`

Business logic layer. Add, delete, update, query transactions, calculate summary data, check budget warnings, and import/export CSV.

### `app/charts.py`

Chart generation layer. Generate monthly trend charts, category charts, and income/expense comparison charts.

### `app/utils.py`

Utility functions for date parsing, amount validation, category keyword matching, and file path handling.

## Database Design

Use SQLite. Recommended database path:

```text
data/moneyscope.db
```

Recommended tables:

```text
transactions(id, date, type, category, amount, description, created_at)
categories(id, name, type, keywords)
budgets(id, month, category, amount)
```

`type` should be either:

```text
income
expense
```

## Coding Rules

1. Keep code simple and readable.
2. Prefer small functions over long functions.
3. Use type hints where helpful.
4. Add docstrings to public functions and classes.
5. Add comments only for key logic, not for every line.
6. Do not duplicate SQL queries everywhere.
7. Do not put all code in `main.py`.
8. Do not silently ignore exceptions.
9. Use clear error messages.
10. Keep UI text in Chinese because this is a Chinese course project.

## Git Rules

Before editing files, check:

```bash
git status --short
```

Do not commit or push unless the user explicitly asks.

When making commits, use clear commit messages:

```text
feat: add transaction CRUD service
feat: add monthly expense chart
fix: handle invalid amount input
docs: update AI development log
```

Keep commits small and meaningful.

## AI_LOG Rules

Whenever AI helps implement or debug a feature, update `AI_LOG.md`.

Each useful AI record should include:

1. Prompt
2. AI output summary
3. Manual modifications
4. Reason for modifications
5. Reflection

Do not fabricate AI logs at the end. Record them during development.

## Development Order

### Stage 1: Project Setup

1. Create project structure.
2. Add requirements.txt.
3. Add README.md.
4. Add initial AI_LOG.md.
5. Add SQLite initialization.

### Stage 2: Core Data Features

1. Create database tables.
2. Add transaction model.
3. Add transaction CRUD.
4. Add sample data.
5. Add basic tests or manual test records.

### Stage 3: Streamlit UI

1. Add record input page.
2. Add transaction list page.
3. Add filter controls.
4. Add summary cards.

### Stage 4: Analysis Features

1. Add monthly trend analysis.
2. Add category distribution chart.
3. Add income and expense comparison.
4. Add budget warning.

### Stage 5: Import and Export

1. Import CSV.
2. Export CSV.
3. Validate CSV format.
4. Handle invalid data.

### Stage 6: Documentation and Polish

1. Update README.
2. Update AI_LOG.md.
3. Add screenshots.
4. Write project report draft.
5. Write PPT outline.
6. Prepare demo script.

## Do Not Do

Do not do these unless explicitly requested:

1. Do not rewrite the whole project at once.
2. Do not introduce unnecessary frameworks.
3. Do not use cloud database.
4. Do not use paid APIs.
5. Do not store real private data.
6. Do not delete user-written documentation.
7. Do not change project scope without permission.
8. Do not commit or push automatically.
9. Do not generate fake screenshots.
10. Do not make the project too complex for a course presentation.
