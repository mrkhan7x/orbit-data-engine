# Orbit Data Engine: Standalone SQLite Backend

A production-grade Python and SQLite database engine powering the **Orbit** desktop productivity app (built on Tauri + React). This engine implements relational data structures, strict schema normalization (3NF), database integrity constraints, and automated database triggers.

---

## 📂 System Architecture

The engine manages tasks, projects, habit logs, goal steps, and parent-child notes using an optimized relational model.

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

---

## 🛠️ Key Technical Features

### 1. Database Normalization (3NF) & Schema Design
*   **Third Normal Form (3NF):** Designed the schema to eliminate partial and transitive dependencies, ensuring zero data redundancy.
*   **Weak Entity Implementation:** Modeled the `habit_logs` table using composite unique constraints (`UNIQUE(habit_id, date)`) tied directly to the parent `habits` table lifecycle.

### 2. Referential & Domain Integrity
*   Implemented strict foreign keys with cascading deletions (`ON DELETE CASCADE`) to prevent orphaned records.
*   Added check constraints (`CHECK`) to enforce field boundaries (e.g., status types, priority limits, and habit completion percentages).

### 3. Automated Database Triggers
Implemented triggers to handle background operations, removing complexity from the application logic:
*   `auto_set_completed_at`: Automatically stamps the UTC timestamp when a task's status changes to 'completed'.
*   `auto_clear_completed_at`: Clears the completed timestamp if a task is reopened.

### 4. Advanced Views & Aggregations
*   `project_summary`: Dynamically computes total tasks, completed tasks, and completion percentages per project.
*   `habit_streaks`: Aggregates logs to compute daily habit patterns and tracking metrics.

---

## 🚀 API & Engine Integration

The engine runs as a lightweight, lightning-fast backend module.
*   **Database Engine:** SQLite (Local storage)
*   **Backend Interface:** Python (SQLite3 wrapper / API server)
*   **Performance:** Optimized queries utilizing indexes on foreign keys to prevent table scans during dashboard renders.
