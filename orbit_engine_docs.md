# Orbit Data Engine — Project Documentation
**Course:** Database Management Systems (DBMS)
**University:** University of Malakand | Department of Artificial Intelligence
**Student:** Muhammad Roman Khan

---

## 1. Project Overview

The **Orbit Data Engine** is a standalone Python + SQLite backend that powers the "Orbit" productivity application. Orbit is a desktop app (built with Tauri + React) that manages **Tasks, Projects, Habits, Goals, and Notes** — all stored in a local SQLite database.

This project demonstrates how **Relational Database Design** and **Data Structures & Algorithms** work together to build a fast, reliable application backend.

---

## 2. Entity-Relationship Diagram (ERD)

### 2.1 Entities & Attributes

```
┌─────────────────────────────────────────────────────────────────┐
│                        STRONG ENTITIES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  GOAL_AREAS  │    │    GOALS     │    │   PROJECTS   │      │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤      │
│  │ PK: id       │    │ PK: id       │    │ PK: id       │      │
│  │ name         │    │ title        │    │ name         │      │
│  │ icon         │    │ description  │    │ description  │      │
│  │ color        │    │ FK: area_id  │    │ color        │      │
│  │ position     │    │ status       │    │ status       │      │
│  └──────────────┘    │ progress     │    │ deadline     │      │
│                      │ deadline     │    │ created_at   │      │
│                      │ is_priority  │    │ updated_at   │      │
│                      │ created_at   │    └──────────────┘      │
│                      └──────────────┘                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────┐    │
│  │    TASKS     │    │   HABITS     │    │     NOTES      │    │
│  ├──────────────┤    ├──────────────┤    ├────────────────┤    │
│  │ PK: id       │    │ PK: id       │    │ PK: id         │    │
│  │ title        │    │ name         │    │ title          │    │
│  │ description  │    │ description  │    │ content        │    │
│  │ status       │    │ icon         │    │ FK: parent_id  │    │
│  │ priority     │    │ color        │    │ category       │    │
│  │ due_date     │    │ frequency    │    │ is_favorite    │    │
│  │ completed_at │    │ difficulty   │    │ created_at     │    │
│  │ FK: project_id│   │ category     │    │ updated_at     │    │
│  │ FK: goal_id  │    │ archived     │    └────────────────┘    │
│  │ created_at   │    │ created_at   │                          │
│  │ updated_at   │    └──────────────┘                          │
│  └──────────────┘                                              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                         WEAK ENTITIES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────┐    │
│  │  HABIT_LOGS  │    │  GOAL_STEPS  │    │ CALENDAR_EVENTS│    │
│  ├──────────────┤    ├──────────────┤    ├────────────────┤    │
│  │ PK: id       │    │ PK: id       │    │ PK: id         │    │
│  │ FK: habit_id │    │ FK: goal_id  │    │ title          │    │
│  │ date         │    │ title        │    │ description    │    │
│  │ completed    │    │ completed    │    │ start_datetime │    │
│  │ note         │    │ FK: task_id  │    │ end_datetime   │    │
│  └──────────────┘    │ position     │    │ all_day        │    │
│                      └──────────────┘    │ color          │    │
│                                          └────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Relationships

```
  GOAL_AREAS ──────< GOALS ──────< GOAL_STEPS
      (1:N)           (1:N)

  PROJECTS ──────< TASKS
      (1:N)

  GOALS ──────< TASKS
      (1:N)

  HABITS ──────< HABIT_LOGS
      (1:N)          (Weak Entity)

  NOTES ──────< NOTES
      (1:N)    (Self-Referencing: parent_id → id)
```

**Legend:**
- `──────<` means One-to-Many (1:N)
- PK = Primary Key, FK = Foreign Key
- Weak Entity = Cannot exist without its parent (e.g., HabitLog needs a Habit)

### 2.3 Relationship Summary Table

| Parent Entity | Child Entity | Cardinality | FK Column | On Delete |
|---|---|---|---|---|
| `goal_areas` | `goals` | 1:N | `goals.area_id` | SET NULL |
| `goals` | `goal_steps` | 1:N | `goal_steps.goal_id` | CASCADE |
| `goals` | `tasks` | 1:N | `tasks.goal_id` | SET NULL |
| `projects` | `tasks` | 1:N | `tasks.project_id` | CASCADE |
| `habits` | `habit_logs` | 1:N | `habit_logs.habit_id` | CASCADE |
| `notes` | `notes` | 1:N (Self) | `notes.parent_id` | CASCADE |

---

## 3. Normalization Analysis

### 3.1 Is the Schema in 3NF?

**Yes.** Here is the proof for the `tasks` table:

| Normal Form | Rule | Satisfied? | Explanation |
|---|---|---|---|
| **1NF** | No repeating groups, atomic values | ✅ | Every column holds a single value. No arrays or lists. |
| **2NF** | No partial dependencies | ✅ | Single PK (`id`), so partial dependency is impossible. |
| **3NF** | No transitive dependencies | ✅ | No non-key column depends on another non-key column. `priority` doesn't determine `status`. |

**The `habit_logs` table** is a classic **Weak Entity** example:
- It has a composite uniqueness constraint: `UNIQUE(habit_id, date)`
- It cannot exist without its parent `habits` row (`ON DELETE CASCADE`)
- Its `habit_id` is both a Foreign Key and part of its identifying key

---

## 4. Integrity Constraints

### 4.1 Entity Integrity
Every table has a `PRIMARY KEY` (the `id` column). No PK can be NULL.

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,  -- Entity Integrity: guaranteed unique, NOT NULL
    ...
);
```

### 4.2 Referential Integrity
Foreign Keys ensure that child rows always reference valid parent rows.

```sql
-- A task MUST reference a valid project (or NULL)
project_id TEXT REFERENCES projects(id) ON DELETE CASCADE

-- If the project is deleted, all its tasks are automatically deleted too
```

### 4.3 Domain Integrity (CHECK Constraints)
Values are restricted to valid domains:

```sql
status TEXT CHECK(status IN ('not_started', 'in_progress', 'completed'))
priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent'))
progress INTEGER CHECK(progress BETWEEN 0 AND 100)
```

---

## 5. Advanced SQL Features

### 5.1 Triggers

**Trigger 1: Auto-set `completed_at` when task is completed**
```sql
CREATE TRIGGER auto_set_completed_at
AFTER UPDATE OF status ON tasks
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    UPDATE tasks SET completed_at = datetime('now') WHERE id = NEW.id;
END;
```
**Why?** Without this trigger, the application code would need to manually set the timestamp every time. The trigger ensures consistency even if the data is modified directly via SQL.

**Trigger 2: Auto-clear `completed_at` when task is un-completed**
```sql
CREATE TRIGGER auto_clear_completed_at
AFTER UPDATE OF status ON tasks
WHEN NEW.status != 'completed' AND OLD.status = 'completed'
BEGIN
    UPDATE tasks SET completed_at = NULL WHERE id = NEW.id;
END;
```

### 5.2 Views

**View 1: `project_summary`** — Aggregates task statistics per project
```sql
CREATE VIEW project_summary AS
SELECT
    p.name AS project_name,
    COUNT(t.id) AS total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) AS completed,
    ROUND(SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(t.id), 1) AS completion_pct
FROM projects p
LEFT JOIN tasks t ON t.project_id = p.id
GROUP BY p.id;
```

**Sample Output:**
| project_name | total_tasks | completed | completion_pct |
|---|---|---|---|
| Orbit Data Engine | 7 | 2 | 28.6 |
| Exam Preparation | 3 | 1 | 33.3 |
| Portfolio Website | 2 | 0 | 0.0 |

**View 2: `daily_dashboard`** — Unified agenda for today
```sql
CREATE VIEW daily_dashboard AS
SELECT 'TASK' AS type, t.title AS name, t.priority, t.status
FROM tasks t WHERE t.due_date = date('now') AND t.status != 'completed'
UNION ALL
SELECT 'HABIT', h.name, h.difficulty,
    CASE WHEN hl.completed = 1 THEN 'completed' ELSE 'pending' END
FROM habits h
LEFT JOIN habit_logs hl ON hl.habit_id = h.id AND hl.date = date('now')
WHERE h.archived = 0;
```

---

## 6. Data Structures & Algorithms

### 6.1 Min-Heap (Priority Queue) — Smart Task Scheduling

**Problem:** SQL `ORDER BY priority` is static — it doesn't consider multiple factors like urgency AND due date together dynamically.

**Solution:** Fetch tasks from the database, calculate a **dynamic priority score**, and insert them into a **Min-Heap**.

**Score Formula:**
```
score = priority_weight × 3 + days_until_due
```
| Priority | Weight | Due in 0 days | Due in 5 days |
|---|---|---|---|
| urgent | 1 | 1×3 + 0 = **3** | 1×3 + 5 = **8** |
| high | 2 | 2×3 + 0 = **6** | 2×3 + 5 = **11** |
| medium | 3 | 3×3 + 0 = **9** | 3×3 + 5 = **14** |
| low | 4 | 4×3 + 0 = **12** | 4×3 + 5 = **17** |

Lower score = higher urgency = served first.

**Time Complexity:**
| Operation | Complexity |
|---|---|
| Insert task into heap | O(log n) |
| Get highest-priority task | O(1) |
| Build heap from n tasks | O(n log n) |

**How it works internally:**
```
Heap Array: [3, 6, 9, 12, 11, 14, 17]

         3              ← Root (most urgent task)
        / \
       6    9
      / \  / \
    12 11 14  17

get_next_task() → returns 3 (the root) in O(1)
```

### 6.2 Trie (Prefix Tree) — Instant Autocomplete Search

**Problem:** SQL `WHERE title LIKE '%query%'` performs a **Full Table Scan** — O(n) for every keystroke.

**Solution:** Load all titles into a **Trie (Prefix Tree)** at startup. Search becomes **O(L)** where L = length of query (independent of total records!).

**How it works:**
```
Inserting: "DBMS", "Design", "Daily"

Root
 ├── d
 │   ├── b
 │   │   └── m
 │   │       └── s → [DBMS Project Notes]
 │   ├── e
 │   │   └── s
 │   │       └── i
 │   │           └── g
 │   │               └── n → [Design ERD, Design homepage]
 │   └── a
 │       └── i
 │           └── l
 │               └── y → [Daily Dashboard]

Search "de" → traverse d → e → return all titles: [Design ERD, Design homepage]
Only 2 steps! Doesn't matter if database has 1 million records.
```

**Time Complexity:**
| Operation | Trie | SQL LIKE |
|---|---|---|
| Search | **O(L)** — L = query length | **O(n)** — n = total rows |
| 1M records, query "des" | **3 operations** | **1,000,000 operations** |

---

## 7. SQL Concepts Demonstrated

| DBMS Concept | Where Demonstrated |
|---|---|
| **3NF Normalization** | All 9 tables — no redundancy |
| **Primary Keys** | Every table has `id TEXT PRIMARY KEY` |
| **Foreign Keys** | tasks → projects, tasks → goals, habit_logs → habits |
| **CASCADE DELETE** | Deleting a project auto-deletes its tasks |
| **SET NULL on Delete** | Deleting a goal sets `tasks.goal_id = NULL` |
| **CHECK Constraints** | status, priority, progress validated |
| **Triggers** | Auto-set/clear `completed_at` timestamp |
| **Views** | project_summary, daily_dashboard, habit_streaks |
| **INNER JOIN** | Tasks with Project names |
| **LEFT JOIN** | Projects with task counts (including projects with 0 tasks) |
| **GROUP BY + Aggregate** | COUNT, SUM, ROUND in project_summary |
| **UNION ALL** | Combining tasks and habits in daily_dashboard |
| **Weak Entity** | habit_logs depends on habits (CASCADE) |
| **Self-Referencing FK** | notes.parent_id → notes.id (nested pages) |

---

## 8. How to Run

```bash
# Navigate to the project directory
cd c:\Users\Dell\OneDrive\Desktop\python

# Run the engine (use this on Windows if Unicode errors occur)
set PYTHONIOENCODING=utf-8 && python orbit_engine.py
```

The script will:
1. Create `orbit_demo.db` with 9 tables
2. Insert mock data (14 tasks, 5 habits, 6 notes, etc.)
3. Demonstrate CASCADE DELETE
4. Create and query 3 Triggers + 3 Views
5. Run Min-Heap task scheduling
6. Run Trie autocomplete search

---

## 9. References

- Connolly, T. M., & Begg, C. E. *Database Systems: A Practical Approach to Design, Implementation, and Management.* Pearson Education.
- Cormen, T. H., et al. *Introduction to Algorithms.* MIT Press.
- SQLite Official Documentation: https://www.sqlite.org/docs.html
