import sqlite3
from flask import Flask, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# DB 초기화
def init_db():
    conn = sqlite3.connect('erp.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            employee_id TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            quantity INTEGER
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# HTML 템플릿
base_template = '''
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{{ title }}</title>
</head>
<body>
<div>
    <h2>{{ title }}</h2>
    {{ body | safe }}
</div>
</body>
</html>
'''

@app.route('/')
def home():
    if 'user' in session:
        body = f'안녕하세요, {session["user"]}님!<br><a href="/dashboard">대시보드</a><br><a href="/logout">로그아웃</a>'
    else:
        body = '<a href="/login">로그인</a> | <a href="/register">회원가입</a>'
    return render_template_string(base_template, title='홈', body=body)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        employee_id = request.form['employee_id']

        conn = sqlite3.connect('erp.db')
        c = conn.cursor()

        c.execute("INSERT INTO users VALUES (?, ?, ?)",
                  (username, password, employee_id))

        conn.commit()
        conn.close()

        session['user'] = username
        return redirect(url_for('dashboard'))

    return render_template_string(base_template, title='회원가입',
        body='<form method="POST"><input name="username"><input name="password"><input name="employee_id"><button>가입</button></form>')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('erp.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))

    return render_template_string(base_template, title='로그인',
        body='<form method="POST"><input name="username"><input name="password"><button>로그인</button></form>')

@app.route('/dashboard')
def dashboard():
    return render_template_string(base_template, title='대시보드',
        body='<a href="/production">생산</a>')

@app.route('/production')
def production():
    return render_template_string(base_template, title='생산',
        body='<a href="/production/input">입력</a> <a href="/production/inventory">재고</a>')

@app.route('/production/input', methods=['GET', 'POST'])
def production_input():
    if request.method == 'POST':
        item = request.form['item']
        quantity = int(request.form['quantity'])

        conn = sqlite3.connect('erp.db')
        c = conn.cursor()

        c.execute("INSERT INTO production (item, quantity) VALUES (?, ?)",
                  (item, quantity))

        conn.commit()
        conn.close()

        return redirect(url_for('production_inventory'))

    return render_template_string(base_template, title='입력',
        body='<form method="POST"><input name="item"><input name="quantity"><button>저장</button></form>')

@app.route('/production/inventory')
def production_inventory():
    conn = sqlite3.connect('erp.db')
    c = conn.cursor()

    c.execute("SELECT item, quantity FROM production")
    rows = c.fetchall()

    conn.close()

    body = ""
    for item, quantity in rows:
        body += f"{item} - {quantity}<br>"

    return render_template_string(base_template, title='재고', body=body)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
