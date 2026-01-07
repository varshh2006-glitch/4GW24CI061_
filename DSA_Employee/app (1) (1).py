from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ems_secret_key'

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # Table for permanent employee information
        conn.execute('''CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT, 
            gender TEXT, department TEXT
        )''')
        # Table for daily activity (Login/Logout updates)
        conn.execute('''CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            action_type TEXT,
            timestamp TEXT,
            FOREIGN KEY(emp_id) REFERENCES employees(id)
        )''')
    conn.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['user'] = 'admin'
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login'))
    db = get_db()
    emps = db.execute('SELECT * FROM employees').fetchall()
    return render_template('index.html', employees=emps)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    db = get_db()
    db.execute('INSERT INTO employees (name, email, phone, gender, department) VALUES (?,?,?,?,?)',
               (request.form['name'], request.form['email'], request.form['phone'], 
                request.form['gender'], request.form['dept']))
    db.commit()
    return redirect(url_for('index'))

@app.route('/log_action/<int:emp_id>/<action>')
def log_action(emp_id, action):
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    db.execute('INSERT INTO daily_logs (emp_id, action_type, timestamp) VALUES (?,?,?)', (emp_id, action, now))
    db.commit()
    return redirect(url_for('view_logs'))

@app.route('/logs')
def view_logs():
    if 'user' not in session: return redirect(url_for('login'))
    db = get_db()
    logs = db.execute('''SELECT employees.name, daily_logs.action_type, daily_logs.timestamp 
                         FROM daily_logs JOIN employees ON employees.id = daily_logs.emp_id 
                         ORDER BY daily_logs.id DESC''').fetchall()
    return render_template('logs.html', logs=logs)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)