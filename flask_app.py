"""A To-Do app"""
import os
import secrets
import sqlite3
from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    flash, 
    jsonify
)


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


def init_db():
    """Initialize the database"""
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                due_date TEXT NOT NULL,
                complete BOOLEAN NOT NULL DEFAULT 0
            )
        ''')
        conn.commit()


if not os.path.exists('tasks.db'):
    init_db()


@app.route('/')
def home():
    """Returns the home HTML"""
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add_task():
    """Adds a task to the task list"""
    try:
        task = request.form.get('task')
        due_date = request.form.get('due_date')
        if task and due_date:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO tasks (name, due_date) VALUES (?, ?)', (task, due_date))
                conn.commit()
                flash('Task added successfully', 'success')
    except Exception as e:
        flash('Error in adding task', 'error')
        print(f"Error when running add_task: {e}")
    return redirect('/')


@app.route('/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    """Marks a task as completed"""
    try:
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE tasks SET complete = NOT complete WHERE id = ?', (task_id,))
            conn.commit()
            flash('Task completion status updated', 'success')
    except Exception as e:
        flash('Error completing task', 'error')
        print(f"Error when running complete_task: {e}")
    return redirect('/')


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Deletes a task from the list"""
    try:
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            flash('Task deleted successfully', 'danger')
    except Exception as e:
        flash('Error deleting task', 'error')
        print(f"Error when running delete_task: {e}")
    return redirect('/')


@app.route('/delete_all', methods=['POST'])
def delete_all_tasks():
    """Deletes all tasks from the list"""
    try:
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks')
            conn.commit()
            flash('All tasks deleted successfully', 'danger')
    except Exception as e:
        flash('Error deleting all tasks', 'error')
        print(f"Error when running delete_all_tasks: {e}")
    return redirect('/')


@app.route("/api/tasks", methods=['GET'])
def get_tasks():
    """Returns a json containing all the tasks"""
    try:
        with sqlite3.connect('tasks.db') as conn:
            cursor.execute('SELECT * FROM tasks')
            tasks = cursor.fetchall()
            conn.close()
        return jsonify(tasks)
    except Exception as e:
        print(f"Error when returning all tasks: {e}")


if __name__ == '__main__':
    app.run()
