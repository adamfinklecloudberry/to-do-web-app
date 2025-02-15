from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    flash, 
    jsonify
)

app = Flask(__name__)

app.secret_key = 'secret_key'

tasks = []

@app.route('/')
def home():
    """Returns the home HTML"""
    return render_template('index.html', tasks = tasks)

@app.route('/add', methods=['POST'])
def add_task():
    """Adds a task to the task list"""
    try:
        task = request.form.get('task')
        due_date = request.form.get('due_date')
        if task and due_date:
            tasks.append({'name': task, 'due_date': due_date, 'complete': False})
            flash('Task added successfully', 'success')
    except Exception as e:
        flash('Error in adding task', 'error')
        print(f"Error when running add_task: {e}")
    return redirect('/')

@app.route('/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    """Marks a task as completed"""
    try:
        if task_id < len(tasks):
            tasks[task_id]['complete'] = not tasks[task_id]['complete']  # Toggle complete status
            flash('Task completion status updated', 'success')
    except Exception as e:
        flash('Error completing task', 'error')
        print(f"Error when running complete_task: {e}")
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Deletes a task from the list"""
    try:
        if task_id < len(tasks):
            tasks.pop(task_id)
            flash('Task deleted successfully', 'danger')
    except Exception as e:
        flash('Error deleting task', 'error')
        print(f"Error when running delete_task: {e}")
    return redirect('/')

@app.route('/delete_all', methods=['POST'])
def delete_all_tasks():
    """Deletes all tasks from the list"""
    try:
        if tasks:
            tasks.clear()  # Clear all tasks
            flash('All tasks deleted successfully', 'danger')
    except Exception as e:
        flash('Error deleting all tasks', 'error')
        print(f"Error when running delete_all_tasks: {e}")
    return redirect('/')

@app.route("/api/tasks", methods=['GET'])
def get_tasks():
    """Returns a json containing all the tasks"""
    try:
        return jsonify(tasks)
    except Exception as e:
        print(f"Error when returning all tasks: {e}")

if __name__ == '__main__':
    app.run(debug_mode)