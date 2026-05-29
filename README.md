# Orbit Data Engine

**A Local-First Productivity Database Backend — DBMS + DSA Project**

> University of Malakand | Department of Artificial Intelligence
> Student: Muhammad Roman Khan

---

## About

The **Orbit Data Engine** is a standalone Python + SQLite backend for the [Orbit](https://github.com/mrkhan7x) productivity application. It demonstrates how **Relational Database Design** (normalization, triggers, views) and **Data Structures & Algorithms** (Min-Heap, Trie) work together to build a fast, reliable application backend.

This project was built as a semester project for the **Database Management Systems (DBMS)** course, bridging concepts from the previous **Data Structures and Algorithms (DSA)** course.

## Features

### Database (DBMS)
- **9 Normalized Tables** (3NF) — Projects, Tasks, Habits, Goals, Notes, and more
- **Foreign Key Constraints** with `ON DELETE CASCADE` and `ON DELETE SET NULL`
- **CHECK Constraints** for domain integrity (status, priority, progress)
- **3 SQL Triggers** — Auto-set/clear timestamps on task completion
- **3 SQL Views** — Project summary, daily dashboard, habit streaks
- **Complex Queries** — INNER JOIN, LEFT JOIN, GROUP BY, UNION ALL, CASE WHEN

### Algorithms (DSA)
- **Min-Heap (Priority Queue)** — Dynamically schedules tasks by combining urgency and due date into a priority score. Serves the most urgent task in **O(1)** time.
- **Trie (Prefix Tree)** — Instant autocomplete search across all notes and tasks in **O(L)** time (L = query length), compared to SQL LIKE which is **O(n)**.

### Interactive CLI
- Browse projects, tasks, habits, and goals
- Run the Min-Heap scheduler live
- Type prefixes and watch the Trie return instant results
- Add new tasks interactively
- Run custom SQL queries directly

## Quick Start

```bash
# Clone the repository
git clone https://github.com/mrkhan7x/orbit-data-engine.git
cd orbit-data-engine

# Run the engine (interactive mode)
python orbit_engine.py

# Run without interactive menu (automated demo only)
python orbit_engine.py --auto
```

> **Note:** If you see Unicode errors on Windows, run:
> ```bash
> set PYTHONIOENCODING=utf-8 && python orbit_engine.py
> ```

**Requirements:** Python 3.7+ (no external dependencies — uses built-in `sqlite3` and `heapq`)

## Project Structure

```
orbit-data-engine/
├── orbit_engine.py          # Main engine — schema, data, triggers, views, DSA
├── orbit_engine_docs.md     # Full documentation (ERD, SQL, algorithms)
└── README.md                # This file
```

## Entity-Relationship Diagram

```
  GOAL_AREAS ──────< GOALS ──────< GOAL_STEPS
      (1:N)           (1:N)

  PROJECTS ──────< TASKS
      (1:N)         (CASCADE DELETE)

  GOALS ──────< TASKS
      (1:N)     (SET NULL on delete)

  HABITS ──────< HABIT_LOGS
      (1:N)      (Weak Entity, CASCADE)

  NOTES ──────< NOTES
      (1:N)  (Self-Referencing FK)
```

## DBMS Concepts Demonstrated

| Concept | Implementation |
|---|---|
| 3NF Normalization | All 9 tables — no redundancy |
| Entity Integrity | Every table has `id TEXT PRIMARY KEY` |
| Referential Integrity | Foreign keys with CASCADE / SET NULL |
| Domain Integrity | CHECK constraints on status, priority |
| Triggers | Auto-timestamp on task completion |
| Views | project_summary, daily_dashboard, habit_streaks |
| JOINs | INNER JOIN, LEFT JOIN |
| Aggregation | COUNT, SUM, ROUND, GROUP BY |
| Weak Entity | habit_logs, goal_steps |
| Self-Referencing FK | notes.parent_id → notes.id |

## DSA Algorithms

### Min-Heap — Task Scheduler
```
Score = priority_weight x 3 + days_until_due
Lower score = higher urgency = served first

         3              ← Most urgent (O(1) access)
        / \
       6    9
      / \  / \
    12 11 14  17
```

### Trie — Autocomplete Search
```
Search "des" → 3 steps → ["Design ERD", "Design homepage"]
vs SQL LIKE  → 1,000,000 steps (Full Table Scan)
```

## Tech Stack

- **Language:** Python 3
- **Database:** SQLite (embedded, zero-config)
- **DSA:** Min-Heap (`heapq`), Trie (custom implementation)
- **Dependencies:** None (stdlib only)

## License

This project was created for academic purposes at the University of Malakand.

## Author

**Muhammad Roman Khan**
- GitHub: [@mrkhan7x](https://github.com/mrkhan7x)
