# Orbit Data Engine — Viva Preparation Guide
**Every question your teacher might ask + confident answers**

---

## SECTION A: PROJECT OVERVIEW QUESTIONS

### Q1: What is this project about?
**A:** This project is a database backend for a productivity application called "Orbit." Orbit manages Tasks, Projects, Habits, Goals, and Notes. I built a standalone Python + SQLite engine that demonstrates relational database design (normalization, foreign keys, triggers, views) combined with data structures (Min-Heap for task scheduling, Trie for search). The goal is to show how DBMS and DSA work together in a real application.

### Q2: Why did you choose this project?
**A:** I already built the Orbit app as a desktop application using Tauri and React. It uses SQLite as its database. So instead of making a fake project, I took my real application and properly analyzed its database — added foreign key constraints, triggers, views, and implemented algorithms that optimize how the app handles data. It's a real-world application of everything we learned in DBMS.

### Q3: Why SQLite and not MySQL or PostgreSQL?
**A:** SQLite is an embedded database — it runs inside the application with zero setup, no server needed. This makes it perfect for desktop apps like Orbit where the data is local to the user's machine. MySQL and PostgreSQL are server-based, designed for multi-user web applications. For a single-user productivity app, SQLite is the industry standard choice (used by WhatsApp, Firefox, Android).

### Q4: What programming language did you use and why?
**A:** Python with the built-in `sqlite3` module. Python was chosen because it's simple, readable, and the `sqlite3` module comes pre-installed — no external dependencies needed. The actual Orbit app uses TypeScript, but for the academic demo, Python makes it easier to explain and present.

---

## SECTION B: DATABASE DESIGN QUESTIONS

### Q5: How many tables does your database have? Name them.
**A:** 9 tables: `goal_areas`, `goals`, `goal_steps`, `projects`, `tasks`, `habits`, `habit_logs`, `notes`, and `calendar_events`.

### Q6: What are the Strong and Weak entities?
**A:** 
- **Strong Entities:** `projects`, `tasks`, `habits`, `goals`, `notes`, `goal_areas`, `calendar_events` — they can exist independently.
- **Weak Entities:** `habit_logs` (depends on `habits` — a log cannot exist without a habit) and `goal_steps` (depends on `goals`). If the parent is deleted, the weak entity is automatically deleted via CASCADE.

### Q7: What is the difference between a Strong and Weak entity?
**A:** A Strong Entity can exist on its own — it has its own primary key and doesn't depend on any other table. A Weak Entity cannot exist without its parent — for example, a `habit_log` recording "completed on May 16" is meaningless if the parent `habit` doesn't exist. Weak entities have a foreign key that is part of their identifying relationship.

### Q8: Explain the relationships in your database.
**A:**
- `goal_areas` → `goals`: One goal area has many goals (1:N)
- `goals` → `goal_steps`: One goal has many steps (1:N)
- `goals` → `tasks`: One goal can have many tasks (1:N)
- `projects` → `tasks`: One project has many tasks (1:N)
- `habits` → `habit_logs`: One habit has many daily logs (1:N)
- `notes` → `notes`: Self-referencing — a note can have sub-notes (1:N)

### Q9: What is a self-referencing relationship? Give an example from your project.
**A:** A self-referencing relationship is when a table has a foreign key that points back to its own primary key. In my project, the `notes` table has `parent_id TEXT REFERENCES notes(id)`. This allows nested notes — a note can be a "child" of another note, creating a tree/hierarchy structure, similar to how Notion pages work.

### Q10: Is your database normalized? Prove it.
**A:** Yes, all tables are in 3NF (Third Normal Form).
- **1NF:** Every column stores atomic (single) values. No arrays or repeating groups.
- **2NF:** Every table has a single-column primary key (`id`), so partial dependencies are impossible.
- **3NF:** No transitive dependencies exist. For example, in `tasks`, the `priority` column doesn't determine the `status` column — they are independent attributes of the task.

### Q11: What is the difference between 1NF, 2NF, and 3NF?
**A:**
- **1NF:** Remove repeating groups. Every cell must contain a single atomic value.
- **2NF:** Must be in 1NF + remove partial dependencies. Every non-key attribute must depend on the ENTIRE primary key (relevant for composite keys).
- **3NF:** Must be in 2NF + remove transitive dependencies. No non-key column should depend on another non-key column. Example: If `department` determines `department_head`, that's a transitive dependency — it should be in a separate table.

---

## SECTION C: SQL & INTEGRITY QUESTIONS

### Q12: What is Entity Integrity?
**A:** Entity Integrity means the Primary Key of every table must be unique and NOT NULL. In my database, every table has `id TEXT PRIMARY KEY`. SQLite automatically enforces that no two rows can have the same `id` and no `id` can be NULL.

### Q13: What is Referential Integrity?
**A:** Referential Integrity means a Foreign Key must either reference a valid Primary Key in the parent table, or be NULL. In my database, `tasks.project_id` must either match an existing `projects.id` or be NULL (for tasks not assigned to any project). If someone tries to insert a task with a fake project_id, SQLite will reject it.

### Q14: What does ON DELETE CASCADE mean?
**A:** It means: "If the parent row is deleted, automatically delete all child rows that reference it." In my project, if I delete a Project, ALL tasks belonging to that project are automatically deleted. This prevents orphan records — tasks that reference a project that no longer exists.

### Q15: What is the difference between CASCADE and SET NULL?
**A:**
- **CASCADE:** Delete the child rows. Used when the child cannot exist without the parent (e.g., tasks under a project).
- **SET NULL:** Set the foreign key to NULL instead of deleting. Used when the child can exist independently (e.g., if a goal is deleted, the tasks still exist but their `goal_id` becomes NULL).

### Q16: What is a CHECK constraint?
**A:** A CHECK constraint restricts the values a column can hold. In my project: `status TEXT CHECK(status IN ('not_started', 'in_progress', 'completed'))`. If someone tries to insert `status = 'banana'`, SQLite will reject it. This is Domain Integrity.

### Q17: What is a Trigger? Explain from your project.
**A:** A Trigger is a piece of SQL that runs AUTOMATICALLY when a specific event happens (INSERT, UPDATE, DELETE). In my project, when a task's status is changed to 'completed', a trigger automatically sets the `completed_at` timestamp to the current time. The app code doesn't need to do this — the database handles it by itself. This ensures consistency even if data is modified outside the application.

### Q18: What is a View? Why did you use Views?
**A:** A View is a virtual table — it doesn't store data; it stores a query. When you SELECT from a View, it runs the underlying query in real-time. I used Views for two reasons:
1. **Simplicity:** Instead of writing a complex JOIN query every time, I just do `SELECT * FROM project_summary`.
2. **Security:** In production, you could grant users access to a View without giving them access to the raw tables.

### Q19: What is the difference between INNER JOIN and LEFT JOIN?
**A:**
- **INNER JOIN:** Returns only rows that have matching values in BOTH tables. If a project has no tasks, it won't appear.
- **LEFT JOIN:** Returns ALL rows from the left table, even if there's no match in the right table. I used LEFT JOIN in `project_summary` so that projects with zero tasks still appear with `total_tasks = 0`.

### Q20: Explain GROUP BY and aggregate functions in your project.
**A:** In the `project_summary` view, I use `GROUP BY p.id` to group all tasks by their parent project. Then I use aggregate functions: `COUNT(t.id)` to count total tasks, `SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END)` to count completed tasks, and `ROUND()` to calculate the completion percentage.

### Q21: What is UNION ALL and why did you use it?
**A:** `UNION ALL` combines the results of two SELECT statements into one result set. In my `daily_dashboard` view, I combine today's tasks and today's habits into a single list — even though they come from different tables with different structures. `UNION ALL` keeps all rows (including duplicates), while `UNION` removes duplicates.

---

## SECTION D: DSA QUESTIONS

### Q22: Why did you implement data structures? SQL already has ORDER BY.
**A:** SQL `ORDER BY` is static — it sorts by one column at a time. But in a productivity app, the "most urgent task" depends on MULTIPLE factors: the priority level AND the due date AND whether it's overdue. My Min-Heap calculates a dynamic score combining all these factors and gives O(1) access to the most urgent task. SQL would need a complex query re-executed every time, while the heap keeps the data pre-sorted in memory.

### Q23: What is a Min-Heap? How does it work?
**A:** A Min-Heap is a complete binary tree where every parent node is SMALLER than its children. The smallest element is always at the root. In my project, the "smallest" means the lowest priority score (= most urgent task). When I call `get_next_task()`, it returns the root in O(1). When I insert a new task, it takes O(log n) because the tree height is log(n).

### Q24: What is your priority score formula?
**A:** `score = priority_weight × 3 + days_until_due`. Priority weights are: urgent=1, high=2, medium=3, low=4. A lower score means higher urgency. So an "urgent" task due today gets score = 1×3 + 0 = 3, while a "low" task due in 5 days gets score = 4×3 + 5 = 17. The heap serves the score-3 task first.

### Q25: What is a Trie? Why not just use SQL LIKE?
**A:** A Trie (Prefix Tree) is a tree where each node represents one character. To search for "des", you traverse: root → d → e → s, and the node at 's' stores all titles starting with "des" (like "Design ERD", "Design homepage"). This takes O(L) time where L=3 (length of query). SQL `LIKE '%des%'` does a Full Table Scan — O(n) where n=total rows. With 1 million records, Trie takes 3 operations vs LIKE takes 1,000,000.

### Q26: What is the time complexity difference?
**A:**
| Operation | Min-Heap | Trie | SQL Equivalent |
|---|---|---|---|
| Get top task | O(1) | — | O(n log n) for ORDER BY |
| Search prefix | — | O(L) | O(n) for LIKE |
| Insert | O(log n) | O(L) | O(1) for INSERT |

### Q27: What is the difference between O(n), O(log n), and O(1)?
**A:**
- **O(1):** Constant time — doesn't matter if you have 100 or 1 million records, it takes the same time. Like reading the root of a heap.
- **O(log n):** Logarithmic — doubles the data, adds only ONE extra step. Like searching a B-Tree index.
- **O(n):** Linear — doubles the data, doubles the time. Like a Full Table Scan.

---

## SECTION E: TRICKY / ADVANCED QUESTIONS

### Q28: What are ACID properties? Does SQLite support them?
**A:** ACID = Atomicity, Consistency, Isolation, Durability. Yes, SQLite fully supports ACID:
- **Atomicity:** A transaction either completes fully or rolls back entirely.
- **Consistency:** The database always moves from one valid state to another.
- **Isolation:** Concurrent transactions don't interfere (SQLite uses file-level locking).
- **Durability:** Once committed, data survives crashes (SQLite uses a journal/WAL).

### Q29: What would happen if you didn't enable PRAGMA foreign_keys?
**A:** By default, SQLite does NOT enforce foreign keys! You must explicitly run `PRAGMA foreign_keys = ON` at the start of every connection. Without it, you could insert a task with `project_id = 'fake123'` and SQLite wouldn't complain — breaking referential integrity. My script enables this on the first line of the connection.

### Q30: Can you have a Clustered Index in SQLite?
**A:** SQLite automatically creates a B-Tree index on every PRIMARY KEY — this is essentially a clustered index because the row data is stored in the B-Tree itself, sorted by the primary key. Non-clustered indexes can be created manually with `CREATE INDEX`.

### Q31: How would you scale this to multiple users?
**A:** SQLite is designed for single-user/embedded use. To scale to multiple concurrent users, I would migrate to PostgreSQL, which supports row-level locking and true multi-user concurrency. The schema (tables, triggers, views) would remain almost identical — only the connection code would change.

### Q32: What is the difference between a View and a Table?
**A:** A Table physically stores data on disk. A View is a saved query — it stores no data. When you query a View, it runs the underlying SQL in real-time. Advantage: Views simplify complex queries and can restrict what data users see (security). Disadvantage: Views can be slower for very complex queries since they compute results on every access.

### Q33: Why did you use TEXT for Primary Keys instead of INTEGER?
**A:** I used UUIDs (Universally Unique Identifiers) as TEXT primary keys. This is an industry practice for distributed systems and client-side apps. Unlike auto-increment integers, UUIDs can be generated on the client side without querying the database, which is essential for offline-first apps like Orbit.

---

## SECTION F: QUICK-FIRE DEFINITIONS

| Term | One-Line Definition |
|---|---|
| **Primary Key** | A column that uniquely identifies each row; never NULL, never duplicated |
| **Foreign Key** | A column that references the Primary Key of another table |
| **Normalization** | Process of organizing data to eliminate redundancy and anomalies |
| **1NF** | Atomic values only — no repeating groups |
| **2NF** | 1NF + no partial dependencies on composite keys |
| **3NF** | 2NF + no transitive dependencies between non-key columns |
| **Trigger** | SQL code that runs automatically on INSERT/UPDATE/DELETE |
| **View** | A virtual table defined by a stored SELECT query |
| **CASCADE** | Auto-delete child rows when parent is deleted |
| **SET NULL** | Set FK to NULL when parent is deleted |
| **Weak Entity** | An entity that cannot exist without its parent |
| **Self-Referencing FK** | A foreign key that points to the same table's primary key |
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **B-Tree** | Balanced tree used for database indexing; O(log n) search |
| **Min-Heap** | Binary tree where parent is always smaller than children |
| **Trie** | Prefix tree for O(L) string search |
| **Full Table Scan** | Reading every row to find a match; O(n) — slowest method |
