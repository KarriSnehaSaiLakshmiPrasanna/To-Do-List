from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "todo.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            scheduled_time TEXT,
            difficulty TEXT DEFAULT 'moderate',
            time_taken INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    description = request.form.get("description", "")
    due_date = request.form.get("due_date", "")
    scheduled_time = request.form.get("scheduled_time", "")
    difficulty = request.form.get("difficulty", "moderate")
    time_taken = int(request.form.get("time_taken", "0") or 0)

    if title.strip():
        conn = get_db_connection()
        conn.execute("""INSERT INTO tasks
            (title, description, due_date, scheduled_time, difficulty, time_taken)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (title, description, due_date, scheduled_time, difficulty, time_taken))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    conn = get_db_connection()
    conn.execute("""UPDATE tasks SET completed =
        CASE WHEN completed = 0 THEN 1 ELSE 0 END WHERE id = ?""", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    conn = get_db_connection()
    if request.method == "POST":
        conn.execute("""UPDATE tasks SET title=?, description=?, due_date=?,
            scheduled_time=?, difficulty=?, time_taken=? WHERE id=?""",
            (request.form["title"], request.form.get("description", ""),
             request.form.get("due_date", ""), request.form.get("scheduled_time", ""),
             request.form.get("difficulty", "moderate"),
             int(request.form.get("time_taken", "0") or 0), task_id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return render_template("edit.html", task=task)

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
