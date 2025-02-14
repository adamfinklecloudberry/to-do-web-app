from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = "secret"

tasks = []

@app.route('/')
def home():
    return render_template('index.html', tasks = tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task')
    due_date = request.form.get('due_date')
    if task and due_date:
        tasks.append({'name': task, 'due_date': due_date, 'complete': False})
        flash('Task added successfully', 'success')
    return redirect('/')

@app.route('/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    if task_id < len(tasks):
        tasks[task_id]['complete'] = not tasks[task_id]['complete']  # Toggle complete status
        flash('Task completion status updated', 'success')
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if task_id < len(tasks):
        tasks.pop(task_id)
        flash('Task deleted successfully', 'danger')
    return redirect('/')

@app.route('/delete_all', methods=['POST'])
def delete_all_tasks():
    if tasks:
        tasks.clear()  # Clear all tasks
        flash('All tasks deleted successfully', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run()