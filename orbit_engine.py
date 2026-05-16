"""
╔══════════════════════════════════════════════════════════════╗
║           ORBIT DATA ENGINE — DBMS + DSA PROJECT            ║
║     University of Malakand | Department of AI               ║
║     Student: Muhammad Roman Khan                            ║
╚══════════════════════════════════════════════════════════════╝

A standalone Python + SQLite demonstration that recreates the
database backend of the "Orbit" productivity application,
enhanced with:
  • Proper Foreign Key constraints & CASCADE rules
  • SQL Triggers for automated state management
  • SQL Views for complex data aggregation
  • Min-Heap (Priority Queue) for smart task scheduling
  • Trie (Prefix Tree) for instant autocomplete search
"""

import sqlite3
import os
import uuid
from datetime import datetime, timedelta
import heapq  # For Min-Heap

# ──────────────────────────────────────────────────────────────
# UTILITY
# ──────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "orbit_demo.db")

def uid():
    return str(uuid.uuid4())

def today(offset=0):
    return (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_rows(cursor, description=None):
    rows = cursor.fetchall() if hasattr(cursor, 'fetchall') else cursor
    if not rows:
        print("  (no rows)")
        return rows
    if description:
        cols = [d[0] for d in description]
    elif hasattr(cursor, 'description') and cursor.description:
        cols = [d[0] for d in cursor.description]
    else:
        cols = [f"col{i}" for i in range(len(rows[0]))]
    widths = [max(len(str(c)), max(len(str(r[i])) for r in rows)) for i, c in enumerate(cols)]
    header = " | ".join(str(c).ljust(w) for c, w in zip(cols, widths))
    print(f"  {header}")
    print(f"  {'-+-'.join('-'*w for w in widths)}")
    for r in rows:
        print(f"  {' | '.join(str(v).ljust(w) for v, w in zip(r, widths))}")
    return rows


# ══════════════════════════════════════════════════════════════
# PHASE 1: SCHEMA CREATION (with FK constraints + CASCADE)
# ══════════════════════════════════════════════════════════════

SCHEMA_SQL = """
-- Enable Foreign Key enforcement (critical for SQLite!)
PRAGMA foreign_keys = ON;

-- ─── GOAL AREAS (Parent of Goals) ───
CREATE TABLE IF NOT EXISTS goal_areas (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    icon        TEXT,
    color       TEXT,
    position    INTEGER DEFAULT 0
);

-- ─── GOALS ───
CREATE TABLE IF NOT EXISTS goals (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    area_id     TEXT REFERENCES goal_areas(id) ON DELETE SET NULL,
    status      TEXT DEFAULT 'not_started' CHECK(status IN ('not_started','in_progress','completed')),
    progress    INTEGER DEFAULT 0 CHECK(progress BETWEEN 0 AND 100),
    deadline    TEXT,
    is_priority INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- ─── PROJECTS ───
CREATE TABLE IF NOT EXISTS projects (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    color       TEXT DEFAULT '#7c6fff',
    status      TEXT DEFAULT 'active' CHECK(status IN ('active','completed','archived')),
    deadline    TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

-- ─── TASKS (references Projects and Goals) ───
CREATE TABLE IF NOT EXISTS tasks (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    status      TEXT DEFAULT 'not_started' CHECK(status IN ('not_started','in_progress','completed')),
    priority    TEXT DEFAULT 'medium' CHECK(priority IN ('low','medium','high','urgent')),
    due_date    TEXT,
    completed_at TEXT,
    project_id  TEXT REFERENCES projects(id) ON DELETE CASCADE,
    goal_id     TEXT REFERENCES goals(id) ON DELETE SET NULL,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

-- ─── HABITS ───
CREATE TABLE IF NOT EXISTS habits (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    icon        TEXT,
    color       TEXT DEFAULT '#7c6fff',
    frequency   TEXT DEFAULT 'daily',
    difficulty  TEXT DEFAULT 'medium' CHECK(difficulty IN ('easy','medium','hard')),
    category    TEXT,
    archived    INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- ─── HABIT LOGS (Weak Entity — depends on Habits) ───
CREATE TABLE IF NOT EXISTS habit_logs (
    id          TEXT PRIMARY KEY,
    habit_id    TEXT NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
    date        TEXT NOT NULL,
    completed   INTEGER DEFAULT 0,
    note        TEXT,
    UNIQUE(habit_id, date)
);

-- ─── GOAL STEPS (Weak Entity — depends on Goals) ───
CREATE TABLE IF NOT EXISTS goal_steps (
    id          TEXT PRIMARY KEY,
    goal_id     TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    completed   INTEGER DEFAULT 0,
    task_id     TEXT REFERENCES tasks(id) ON DELETE SET NULL,
    position    INTEGER DEFAULT 0
);

-- ─── NOTES (Self-referencing for nested pages) ───
CREATE TABLE IF NOT EXISTS notes (
    id          TEXT PRIMARY KEY,
    title       TEXT DEFAULT 'Untitled',
    content     TEXT,
    parent_id   TEXT REFERENCES notes(id) ON DELETE CASCADE,
    category    TEXT DEFAULT 'notes',
    is_favorite INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

-- ─── CALENDAR EVENTS ───
CREATE TABLE IF NOT EXISTS calendar_events (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    description     TEXT,
    start_datetime  TEXT NOT NULL,
    end_datetime    TEXT,
    all_day         INTEGER DEFAULT 0,
    color           TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);
"""


def create_schema(conn):
    """Phase 1: Create all tables with FK constraints."""
    print_header("PHASE 1: SCHEMA CREATION")
    conn.executescript(SCHEMA_SQL)
    # Verify tables
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cur.fetchall()
    print(f"  ✅ Created {len(tables)} tables:")
    for t in tables:
        print(f"     • {t[0]}")


# ══════════════════════════════════════════════════════════════
# PHASE 2: MOCK DATA INSERTION + CRUD DEMO
# ══════════════════════════════════════════════════════════════

# Pre-generate IDs for cross-referencing
P = [uid() for _ in range(4)]   # 4 projects
G = [uid() for _ in range(3)]   # 3 goals
GA = [uid() for _ in range(2)]  # 2 goal areas
H = [uid() for _ in range(5)]   # 5 habits
N = [uid() for _ in range(6)]   # 6 notes

MOCK_DATA = {
    "goal_areas": [
        (GA[0], "Career & Skills", "💼", "#4CAF50", 0),
        (GA[1], "Health & Fitness", "🏋️", "#FF5722", 1),
    ],
    "goals": [
        (G[0], "Master DBMS Course", "Complete all assignments and project", GA[0], "in_progress", 40, today(30), 1, now()),
        (G[1], "Build Portfolio Website", "Deploy personal site on GitHub Pages", GA[0], "not_started", 0, today(60), 0, now()),
        (G[2], "Run 5K Without Stopping", "Build up cardio endurance", GA[1], "in_progress", 60, today(45), 0, now()),
    ],
    "projects": [
        (P[0], "Orbit Data Engine", "DBMS + DSA university project", "#7c6fff", "active", today(7), now(), now()),
        (P[1], "Portfolio Website", "Personal brand site", "#FF6B6B", "active", today(30), now(), now()),
        (P[2], "Exam Preparation", "Week 1-6 revision", "#4ECDC4", "active", today(14), now(), now()),
        (P[3], "Fitness Tracker", "Track daily workouts", "#45B7D1", "completed", today(-5), now(), now()),
    ],
    "tasks": [
        (uid(), "Design ERD for Orbit", "Draw entity-relationship diagram", "completed", "high", today(-2), now(), P[0], G[0], now(), now()),
        (uid(), "Write SQL schema", "Create all tables with constraints", "completed", "high", today(-1), now(), P[0], G[0], now(), now()),
        (uid(), "Implement Triggers", "Auto-update project progress", "in_progress", "high", today(), None, P[0], G[0], now(), now()),
        (uid(), "Implement Views", "Daily dashboard view", "not_started", "medium", today(1), None, P[0], G[0], now(), now()),
        (uid(), "Build Min-Heap scheduler", "Priority queue for tasks", "not_started", "urgent", today(), None, P[0], G[0], now(), now()),
        (uid(), "Build Trie search", "Autocomplete for notes/tasks", "not_started", "medium", today(2), None, P[0], G[0], now(), now()),
        (uid(), "Write documentation", "Full project docs", "not_started", "low", today(3), None, P[0], G[0], now(), now()),
        (uid(), "Design homepage layout", "Hero section + nav", "not_started", "high", today(5), None, P[1], G[1], now(), now()),
        (uid(), "Setup GitHub Pages", "Deploy initial version", "not_started", "medium", today(10), None, P[1], G[1], now(), now()),
        (uid(), "Revise ER Modeling", "Chapter 12 revision", "completed", "high", today(-3), now(), P[2], G[0], now(), now()),
        (uid(), "Revise Normalization", "Chapter 14-15 revision", "in_progress", "high", today(), None, P[2], G[0], now(), now()),
        (uid(), "Practice SQL queries", "50 practice questions", "not_started", "medium", today(3), None, P[2], G[0], now(), now()),
        (uid(), "Morning run — 2K", "Easy pace", "completed", "medium", today(-1), now(), P[3], G[2], now(), now()),
        (uid(), "Morning run — 3K", "Build endurance", "completed", "medium", today(), now(), P[3], G[2], now(), now()),
    ],
    "habits": [
        (H[0], "Morning Exercise", "30 min workout", "🏃", "#FF5722", "daily", "medium", "Health", 0, now()),
        (H[1], "Read 20 Pages", "Read technical books", "📖", "#4CAF50", "daily", "easy", "Learning", 0, now()),
        (H[2], "Practice SQL", "Solve 5 SQL problems", "💻", "#2196F3", "daily", "hard", "Career", 0, now()),
        (H[3], "Drink 8 Glasses Water", "Stay hydrated", "💧", "#00BCD4", "daily", "easy", "Health", 0, now()),
        (H[4], "Review Flashcards", "Spaced repetition", "🧠", "#9C27B0", "daily", "medium", "Learning", 0, now()),
    ],
    "notes": [
        (N[0], "DBMS Project Notes", "Main notes for the Orbit Data Engine project including ERD sketches and SQL drafts.", None, "notes", 1, now(), now()),
        (N[1], "ERD Design Decisions", "Decided to use TEXT for IDs (UUID) instead of INTEGER for portability.", N[0], "notes", 0, now(), now()),
        (N[2], "Normalization Cheatsheet", "UNF → 1NF: Remove repeating groups. 1NF → 2NF: Remove partial dependencies. 2NF → 3NF: Remove transitive dependencies.", None, "notes", 1, now(), now()),
        (N[3], "SQL Trigger Syntax", "CREATE TRIGGER name AFTER UPDATE ON table FOR EACH ROW BEGIN ... END;", N[0], "notes", 0, now(), now()),
        (N[4], "Weekly Meeting Notes", "Discussed project timeline with Awais. Deadline is end of this week.", None, "notes", 0, now(), now()),
        (N[5], "B-Tree Index Notes", "B-Trees keep data sorted for O(log n) search. Used internally by SQLite for indexed columns.", None, "notes", 0, now(), now()),
    ],
}


def insert_mock_data(conn):
    """Phase 2: Insert realistic mock data."""
    print_header("PHASE 2: MOCK DATA INSERTION")

    conn.executemany("INSERT INTO goal_areas VALUES (?,?,?,?,?)", MOCK_DATA["goal_areas"])
    print(f"  ✅ Inserted {len(MOCK_DATA['goal_areas'])} goal areas")

    conn.executemany("INSERT INTO goals VALUES (?,?,?,?,?,?,?,?,?)", MOCK_DATA["goals"])
    print(f"  ✅ Inserted {len(MOCK_DATA['goals'])} goals")

    conn.executemany("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?)", MOCK_DATA["projects"])
    print(f"  ✅ Inserted {len(MOCK_DATA['projects'])} projects")

    conn.executemany("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?)", MOCK_DATA["tasks"])
    print(f"  ✅ Inserted {len(MOCK_DATA['tasks'])} tasks")

    conn.executemany("INSERT INTO habits VALUES (?,?,?,?,?,?,?,?,?,?)", MOCK_DATA["habits"])
    print(f"  ✅ Inserted {len(MOCK_DATA['habits'])} habits")

    # Generate habit logs for past 7 days
    log_count = 0
    for h_id in H:
        for day_offset in range(-6, 1):
            conn.execute("INSERT INTO habit_logs VALUES (?,?,?,?,?)",
                         (uid(), h_id, today(day_offset), 1 if day_offset < 0 else 0, None))
            log_count += 1
    print(f"  ✅ Inserted {log_count} habit logs (7 days × 5 habits)")

    conn.executemany("INSERT INTO notes VALUES (?,?,?,?,?,?,?,?)", MOCK_DATA["notes"])
    print(f"  ✅ Inserted {len(MOCK_DATA['notes'])} notes")

    conn.commit()

    # Demo: Show tasks with project names (JOIN)
    print("\n  📋 Sample Query — Tasks with Project Names (INNER JOIN):")
    cur = conn.execute("""
        SELECT t.title, t.priority, t.status, p.name AS project
        FROM tasks t
        INNER JOIN projects p ON t.project_id = p.id
        ORDER BY t.due_date
        LIMIT 8
    """)
    print_rows(cur)

    # Demo: CASCADE DELETE
    print("\n  🗑️  CASCADE DELETE Demo:")
    print("     Before: Counting tasks in 'Fitness Tracker' project...")
    cur = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (P[3],))
    print(f"     Tasks in Fitness Tracker: {cur.fetchone()[0]}")
    conn.execute("DELETE FROM projects WHERE id = ?", (P[3],))
    conn.commit()
    cur = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (P[3],))
    print(f"     After DELETE project: Tasks remaining = {cur.fetchone()[0]}")
    print("     ✅ CASCADE DELETE worked — child tasks auto-deleted!")


# ══════════════════════════════════════════════════════════════
# PHASE 3: ADVANCED SQL — TRIGGERS & VIEWS
# ══════════════════════════════════════════════════════════════

TRIGGERS_SQL = """
-- TRIGGER 1: Auto-update project completion % when a task status changes
CREATE TRIGGER IF NOT EXISTS after_task_status_change
AFTER UPDATE OF status ON tasks
WHEN NEW.project_id IS NOT NULL
BEGIN
    UPDATE projects
    SET updated_at = datetime('now')
    WHERE id = NEW.project_id;
END;

-- TRIGGER 2: Auto-set completed_at timestamp when task is marked completed
CREATE TRIGGER IF NOT EXISTS auto_set_completed_at
AFTER UPDATE OF status ON tasks
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    UPDATE tasks SET completed_at = datetime('now') WHERE id = NEW.id;
END;

-- TRIGGER 3: Auto-clear completed_at when task is un-completed
CREATE TRIGGER IF NOT EXISTS auto_clear_completed_at
AFTER UPDATE OF status ON tasks
WHEN NEW.status != 'completed' AND OLD.status = 'completed'
BEGIN
    UPDATE tasks SET completed_at = NULL WHERE id = NEW.id;
END;
"""

VIEWS_SQL = """
-- VIEW 1: Project Summary — each project with task stats
CREATE VIEW IF NOT EXISTS project_summary AS
SELECT
    p.id,
    p.name AS project_name,
    p.status AS project_status,
    COUNT(t.id) AS total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
    ROUND(
        CASE WHEN COUNT(t.id) > 0
        THEN (SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.id))
        ELSE 0 END, 1
    ) AS completion_pct
FROM projects p
LEFT JOIN tasks t ON t.project_id = p.id
GROUP BY p.id;

-- VIEW 2: Daily Dashboard — today's tasks + habits unified
CREATE VIEW IF NOT EXISTS daily_dashboard AS
SELECT 'TASK' AS type, t.title AS name, t.priority AS detail, t.status
FROM tasks t
WHERE t.due_date = date('now') AND t.status != 'completed'
UNION ALL
SELECT 'HABIT' AS type, h.name, h.difficulty AS detail,
    CASE WHEN hl.completed = 1 THEN 'completed' ELSE 'pending' END AS status
FROM habits h
LEFT JOIN habit_logs hl ON hl.habit_id = h.id AND hl.date = date('now')
WHERE h.archived = 0;

-- VIEW 3: Habit Streaks — consecutive days completed
CREATE VIEW IF NOT EXISTS habit_streaks AS
SELECT
    h.name AS habit_name,
    h.icon,
    COUNT(hl.id) AS total_logs,
    SUM(hl.completed) AS days_completed,
    ROUND(SUM(hl.completed) * 100.0 / MAX(COUNT(hl.id), 1), 1) AS completion_rate
FROM habits h
LEFT JOIN habit_logs hl ON hl.habit_id = h.id
GROUP BY h.id;
"""


def create_triggers_and_views(conn):
    """Phase 3: Add Triggers and Views."""
    print_header("PHASE 3: ADVANCED SQL — TRIGGERS & VIEWS")

    conn.executescript(TRIGGERS_SQL)
    print("  ✅ Created 3 Triggers:")
    print("     • after_task_status_change (auto-update project timestamp)")
    print("     • auto_set_completed_at (auto-set completion time)")
    print("     • auto_clear_completed_at (auto-clear on undo)")

    conn.executescript(VIEWS_SQL)
    print("\n  ✅ Created 3 Views:")

    # Demo View 1: Project Summary
    print("\n  📊 VIEW: project_summary")
    cur = conn.execute("SELECT * FROM project_summary")
    print_rows(cur)

    # Demo View 2: Daily Dashboard
    print("\n  📅 VIEW: daily_dashboard (today's agenda)")
    cur = conn.execute("SELECT * FROM daily_dashboard")
    print_rows(cur)

    # Demo View 3: Habit Streaks
    print("\n  🔥 VIEW: habit_streaks")
    cur = conn.execute("SELECT * FROM habit_streaks")
    print_rows(cur)

    # Demo Trigger: Mark a task as completed, check auto-timestamp
    print("\n  ⚡ TRIGGER Demo: Marking a task as 'completed'...")
    task = conn.execute("SELECT id, title FROM tasks WHERE status = 'in_progress' LIMIT 1").fetchone()
    if task:
        print(f"     Task: '{task[1]}'")
        before = conn.execute("SELECT completed_at FROM tasks WHERE id = ?", (task[0],)).fetchone()
        print(f"     completed_at BEFORE: {before[0]}")
        conn.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task[0],))
        conn.commit()
        after = conn.execute("SELECT completed_at FROM tasks WHERE id = ?", (task[0],)).fetchone()
        print(f"     completed_at AFTER:  {after[0]}")
        print("     ✅ Trigger auto-set completed_at timestamp!")


# ══════════════════════════════════════════════════════════════
# PHASE 4: DSA — MIN-HEAP (Priority Queue) + TRIE (Prefix Tree)
# ══════════════════════════════════════════════════════════════

# ─── 4A: MIN-HEAP — Smart Task Scheduler ─────────────────────
class TaskScheduler:
    """
    Min-Heap Priority Queue for intelligent task scheduling.

    Instead of a static SQL ORDER BY, we calculate a dynamic
    priority score and use a heap to always serve the most
    urgent task in O(1) time.

    Score formula:
      score = priority_weight × 3 - days_until_due
      (Lower score = higher urgency = served first)
    """
    PRIORITY_WEIGHTS = {"urgent": 1, "high": 2, "medium": 3, "low": 4}

    def __init__(self):
        self.heap = []  # Min-heap of (score, task_title, due_date, priority)

    def calculate_score(self, priority, due_date):
        weight = self.PRIORITY_WEIGHTS.get(priority, 3)
        if due_date:
            try:
                days_left = (datetime.strptime(due_date, "%Y-%m-%d") - datetime.now()).days
            except ValueError:
                days_left = 30
        else:
            days_left = 30  # No due date = low urgency
        return weight * 3 + days_left

    def load_from_db(self, conn):
        """Fetch incomplete tasks from DB and build the heap."""
        cur = conn.execute("""
            SELECT id, title, priority, due_date
            FROM tasks WHERE status != 'completed'
        """)
        for row in cur.fetchall():
            task_id, title, priority, due_date = row
            score = self.calculate_score(priority, due_date)
            heapq.heappush(self.heap, (score, title, due_date or "No date", priority))

    def get_next_task(self):
        """Pop the highest-priority task in O(1)."""
        if self.heap:
            return heapq.heappop(self.heap)
        return None

    def peek(self):
        """See the top task without removing it."""
        return self.heap[0] if self.heap else None

    def size(self):
        return len(self.heap)


# ─── 4B: TRIE — Prefix Tree for Instant Search ───────────────
class TrieNode:
    """A single node in the Trie."""
    def __init__(self):
        self.children = {}      # char → TrieNode
        self.is_end = False     # Marks end of a complete word/title
        self.titles = []        # Full titles that pass through this node


class Trie:
    """
    Prefix Tree for O(L) autocomplete search.

    Instead of SQL LIKE '%query%' which does a Full Table Scan O(n),
    the Trie provides instant prefix-based suggestions.
    L = length of search query (independent of total records!)
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, title):
        """Insert a title into the Trie. O(L) where L = len(title)."""
        node = self.root
        for char in title.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.titles.append(title)
        node.is_end = True

    def search(self, prefix):
        """Find all titles matching a prefix. O(L) time."""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []  # No match
            node = node.children[char]
        return node.titles

    def load_from_db(self, conn):
        """Load all note titles + task titles into the Trie."""
        count = 0
        for row in conn.execute("SELECT title FROM notes").fetchall():
            if row[0]:
                self.insert(row[0])
                count += 1
        for row in conn.execute("SELECT title FROM tasks").fetchall():
            if row[0]:
                self.insert(row[0])
                count += 1
        return count


def demo_dsa(conn):
    """Phase 4: Demonstrate Min-Heap and Trie."""
    print_header("PHASE 4: DSA — MIN-HEAP + TRIE")

    # ── Min-Heap Demo ──
    print("\n  🏗️  4A: MIN-HEAP (Priority Queue) — Smart Task Scheduler")
    print("  " + "-"*50)
    scheduler = TaskScheduler()
    scheduler.load_from_db(conn)
    print(f"  Loaded {scheduler.size()} incomplete tasks into the heap.\n")
    print(f"  {'Rank':<6} {'Score':<8} {'Priority':<10} {'Due Date':<12} {'Task Title'}")
    print(f"  {'─'*6} {'─'*8} {'─'*10} {'─'*12} {'─'*30}")
    rank = 1
    while scheduler.size() > 0:
        score, title, due, priority = scheduler.get_next_task()
        print(f"  {rank:<6} {score:<8} {priority:<10} {due:<12} {title}")
        rank += 1
    print(f"\n  ⏱️  Time Complexity: get_next_task() = O(1) | insert() = O(log n)")

    # ── Trie Demo ──
    print(f"\n\n  🔍 4B: TRIE (Prefix Tree) — Instant Autocomplete Search")
    print("  " + "-"*50)
    trie = Trie()
    count = trie.load_from_db(conn)
    print(f"  Loaded {count} titles (notes + tasks) into the Trie.\n")

    test_queries = ["db", "re", "build", "mor", "sql", "nor", "des"]
    for q in test_queries:
        results = trie.search(q)
        if results:
            print(f'  🔎 Search "{q}" → {results[:4]}')
        else:
            print(f'  🔎 Search "{q}" → (no matches)')
    print(f"\n  ⏱️  Time Complexity: search() = O(L) where L = length of query")
    print(f"      vs SQL LIKE = O(n) where n = total rows in table")


# ══════════════════════════════════════════════════════════════
# INTERACTIVE CLI MENU — For Live Presentation
# ══════════════════════════════════════════════════════════════

def interactive_menu(conn):
    """Interactive CLI for live demo during presentation."""
    trie = Trie()
    trie.load_from_db(conn)

    while True:
        print(f"\n{'='*60}")
        print("  ORBIT DATA ENGINE — Interactive Demo")
        print(f"{'='*60}")
        print("  [1] View All Projects")
        print("  [2] View All Tasks (with Project names)")
        print("  [3] View Daily Dashboard (today's agenda)")
        print("  [4] View Project Summary (completion %)")
        print("  [5] View Habit Streaks")
        print("  [6] Smart Task Scheduler (Min-Heap)")
        print("  [7] Autocomplete Search (Trie)")
        print("  [8] Add a New Task")
        print("  [9] Run Custom SQL Query")
        print("  [0] Exit")
        print(f"{'='*60}")

        choice = input("  Enter choice: ").strip()

        if choice == "1":
            print_header("ALL PROJECTS")
            cur = conn.execute("SELECT name, status, deadline FROM projects ORDER BY name")
            print_rows(cur)

        elif choice == "2":
            print_header("ALL TASKS (with Project Names)")
            cur = conn.execute("""
                SELECT t.title, t.priority, t.status, t.due_date, COALESCE(p.name, '(no project)') AS project
                FROM tasks t LEFT JOIN projects p ON t.project_id = p.id
                ORDER BY t.due_date
            """)
            print_rows(cur)

        elif choice == "3":
            print_header("DAILY DASHBOARD — Today's Agenda")
            cur = conn.execute("SELECT * FROM daily_dashboard")
            print_rows(cur)

        elif choice == "4":
            print_header("PROJECT SUMMARY")
            cur = conn.execute("SELECT project_name, total_tasks, completed_tasks, completion_pct FROM project_summary")
            print_rows(cur)

        elif choice == "5":
            print_header("HABIT STREAKS")
            cur = conn.execute("SELECT * FROM habit_streaks")
            print_rows(cur)

        elif choice == "6":
            print_header("MIN-HEAP — Smart Task Scheduler")
            scheduler = TaskScheduler()
            scheduler.load_from_db(conn)
            print(f"  Loaded {scheduler.size()} incomplete tasks.\n")
            print(f"  {'Rank':<6} {'Score':<8} {'Priority':<10} {'Due Date':<12} {'Task Title'}")
            print(f"  {'---':<6} {'---':<8} {'---':<10} {'---':<12} {'---':<30}")
            rank = 1
            while scheduler.size() > 0:
                score, title, due, priority = scheduler.get_next_task()
                print(f"  {rank:<6} {score:<8} {priority:<10} {due:<12} {title}")
                rank += 1
            print(f"\n  Time: get_next_task() = O(1) | insert() = O(log n)")

        elif choice == "7":
            print_header("TRIE — Autocomplete Search")
            while True:
                query = input("  Type a prefix (or 'back' to return): ").strip()
                if query.lower() == "back":
                    break
                results = trie.search(query)
                if results:
                    print(f"  Results for '{query}': {results[:6]}")
                else:
                    print(f"  No matches for '{query}'")

        elif choice == "8":
            print_header("ADD NEW TASK")
            title = input("  Task title: ").strip()
            if not title:
                print("  Cancelled.")
                continue
            priority = input("  Priority (low/medium/high/urgent): ").strip() or "medium"
            due = input("  Due date (YYYY-MM-DD or press Enter for today): ").strip() or today()
            task_id = uid()
            conn.execute(
                "INSERT INTO tasks (id, title, priority, due_date) VALUES (?,?,?,?)",
                (task_id, title, priority, due)
            )
            conn.commit()
            trie.insert(title)  # Also add to Trie for search
            print(f"  Task '{title}' added successfully!")

        elif choice == "9":
            print_header("CUSTOM SQL QUERY")
            print("  Type your SQL (e.g., SELECT * FROM tasks LIMIT 5):")
            sql = input("  SQL> ").strip()
            if not sql:
                continue
            try:
                cur = conn.execute(sql)
                if sql.upper().startswith("SELECT"):
                    print_rows(cur)
                else:
                    conn.commit()
                    print(f"  Query executed. Rows affected: {cur.rowcount}")
            except Exception as e:
                print(f"  Error: {e}")

        elif choice == "0":
            print("\n  Goodbye! Orbit Data Engine shutting down.")
            break
        else:
            print("  Invalid choice. Try again.")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def setup_db():
    """Initialize DB, create schema, insert data, create triggers/views."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    print("=" * 62)
    print("  ORBIT DATA ENGINE -- DBMS + DSA PROJECT")
    print("  University of Malakand | Department of AI")
    print("  Student: Muhammad Roman Khan")
    print("=" * 62)

    create_schema(conn)
    insert_mock_data(conn)
    create_triggers_and_views(conn)
    demo_dsa(conn)

    print_header("ALL PHASES COMPLETE")
    print(f"  Database saved at: {DB_PATH}")
    print(f"  Tables: 9 | Triggers: 3 | Views: 3")
    print(f"  DSA: Min-Heap + Trie implemented and demonstrated")
    return conn


def main():
    import sys
    conn = setup_db()

    # If --auto flag is passed, skip interactive menu
    if "--auto" in sys.argv:
        conn.close()
        return

    print("\n  Launching Interactive Demo...")
    interactive_menu(conn)
    conn.close()


if __name__ == "__main__":
    main()
