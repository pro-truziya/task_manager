from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    assignee = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='новая')
    deadline = db.Column(db.String(50), nullable=False)
    hours = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
    if Task.query.count() == 0:
        tasks = [
            Task(title="Спроектировать БД", assignee="Антон", status="новая", deadline="2026-06-01", hours=8),
            Task(title="Написать бэкенд", assignee="Антон", status="в работе", deadline="2026-06-05", hours=16),
            Task(title="Сверстать интерфейс", assignee="Мария", status="завершена", deadline="2026-05-28", hours=12),
        ]
        db.session.add_all(tasks)
        db.session.commit()

@app.route('/')
def index():
    status_filter = request.args.get('status', '')
    if status_filter:
        tasks = Task.query.filter_by(status=status_filter).all()
    else:
        tasks = Task.query.all()
    
    total = Task.query.count()
    completed = Task.query.filter_by(status='завершена').count()
    
    return render_template('index.html', tasks=tasks, total=total, completed=completed, status_filter=status_filter)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task = Task(
            title=request.form['title'],
            assignee=request.form['assignee'],
            status=request.form['status'],
            deadline=request.form['deadline'],
            hours=float(request.form['hours'])
        )
        db.session.add(task)
        db.session.commit()
        flash('Задача добавлена', 'success')
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.assignee = request.form['assignee']
        task.status = request.form['status']
        task.deadline = request.form['deadline']
        task.hours = float(request.form['hours'])
        db.session.commit()
        flash('Задача обновлена', 'success')
        return redirect(url_for('index'))
    return render_template('edit_task.html', task=task)

@app.route('/status/<int:id>/<new_status>')
def change_status(id, new_status):
    task = Task.query.get_or_404(id)
    if new_status in ['новая', 'в работе', 'завершена']:
        task.status = new_status
        db.session.commit()
        flash(f'Статус изменён на "{new_status}"', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Задача удалена', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)