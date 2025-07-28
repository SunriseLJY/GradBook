from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from flask import send_from_directory  # 确保正确导入
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 资源文件夹路径
IMAGE_FOLDER = os.path.join('static', 'images')
VIDEO_FOLDER = os.path.join('static', 'videos')

# 按年份分类的资源
YEARS = [str(year) for year in range(2019, 2026)]

# 档案数量
teacher_profile_count = 0
student_profile_count = 0

def get_files_by_year(folder, years):
    """按年份分类获取文件"""
    files_by_year = {}
    for year in years:
        year_folder = os.path.join(folder, year)
        if os.path.exists(year_folder):
            files_by_year[year] = os.listdir(year_folder)
        else:
            files_by_year[year] = []
    return files_by_year

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化数据库
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # 创建 users 表
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL UNIQUE,
                 password TEXT NOT NULL,
                 role TEXT NOT NULL)''')
    
    # 处理 students 表
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS students
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     birthday TEXT,
                     contact TEXT)''')
    except sqlite3.OperationalError:
        # 检查表结构，若缺少列则添加
        c.execute("PRAGMA table_info(students)")
        columns = [row[1] for row in c.fetchall()]
        if 'birthday' not in columns:
            logging.info("Adding 'birthday' column to 'students' table")
            c.execute("ALTER TABLE students ADD COLUMN birthday TEXT")
        if 'contact' not in columns:
            logging.info("Adding 'contact' column to 'students' table")
            c.execute("ALTER TABLE students ADD COLUMN contact TEXT")

    # 处理 teachers 表
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS teachers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     birthday TEXT,
                     subject TEXT,
                     teaching_time TEXT,
                     contact TEXT)''')
    except sqlite3.OperationalError:
        c.execute("PRAGMA table_info(teachers)")
        columns = [row[1] for row in c.fetchall()]
        if 'birthday' not in columns:
            logging.info("Adding 'birthday' column to 'teachers' table")
            c.execute("ALTER TABLE teachers ADD COLUMN birthday TEXT")
        if 'subject' not in columns:
            logging.info("Adding 'subject' column to 'teachers' table")
            c.execute("ALTER TABLE teachers ADD COLUMN subject TEXT")
        if 'teaching_time' not in columns:
            logging.info("Adding 'teaching_time' column to 'teachers' table")
            c.execute("ALTER TABLE teachers ADD COLUMN teaching_time TEXT")
        if 'contact' not in columns:
            logging.info("Adding 'contact' column to 'teachers' table")
            c.execute("ALTER TABLE teachers ADD COLUMN contact TEXT")

    # 写入老师及同学档案数量
    c.execute("SELECT COUNT(*) FROM teachers")
    teacher_profile_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM students")
    student_profile_count = c.fetchone()[0]

    conn.commit()
    conn.close()
    logging.info("Database initialization completed")
    logging.info(f"Teacher profile count: {teacher_profile_count}")
    logging.info(f"Student profile count: {student_profile_count}")

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user'))
    return render_template('index_unlogged.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT id, role FROM users WHERE username =? AND password =?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['role'] = user[1]
            if user[1] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user'))
        else:
            error = "用户名或密码错误"
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            error = "两次输入的密码不一致"
        else:
            try:
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)", (username, password, 'user'))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = "用户名已存在，请选择其他用户名"

    return render_template('register.html', error=error)

@app.route('/admin')
def admin():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/user')
def user():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    return render_template('user.html')

@app.route('/user_list')
def user_list():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    users = c.fetchall()
    conn.close()

    # 将查询结果转换为字典列表，方便模板使用
    user_list = [{'username': user[0], 'role': user[1]} for user in users]
    return render_template('user_list.html', users=user_list)

@app.route('/photos')
def photos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    images_by_year = get_files_by_year(IMAGE_FOLDER, YEARS)
    return render_template('photos.html', years=YEARS, images_by_year=images_by_year)

@app.route('/videos')
def videos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    videos_by_year = get_files_by_year(VIDEO_FOLDER, YEARS)
    return render_template('videos.html', years=YEARS, videos_by_year=videos_by_year)

@app.route('/photos/<year>')
def photo_year(year):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    year_folder = os.path.join(IMAGE_FOLDER, year)
    if os.path.exists(year_folder):
        images = os.listdir(year_folder)
        return render_template('photo_year.html', year=year, images=images)
    else:
        return render_template("404.html"), 404

@app.route('/videos/<year>')
def video_year(year):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    year_folder = os.path.join(VIDEO_FOLDER, year)
    if os.path.exists(year_folder):
        videos = os.listdir(year_folder)
        return render_template('video_year.html', year=year, videos=videos)
    else:
        return render_template("404.html"), 404

@app.route('/download/<folder>/<year>/<filename>')
def download(folder, year, filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if folder == 'images':
        return send_from_directory(os.path.join(IMAGE_FOLDER, year), filename, as_attachment=True)
    elif folder == 'videos':
        return send_from_directory(os.path.join(VIDEO_FOLDER, year), filename, as_attachment=True)
    else:
        return render_template("nofile.html"), 404

def get_profile(profile_type, id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if profile_type == 'student':
        c.execute("SELECT id, name, birthday, contact FROM students WHERE id =?", (id,))
    elif profile_type == 'teacher':
        c.execute("SELECT id, name, birthday, subject, teaching_time, contact FROM teachers WHERE id =?", (id,))
    profile = c.fetchall()
    conn.close()
    return profile

def delete_profile(profile_type, id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if profile_type == 'student':
        c.execute("DELETE FROM students WHERE id =?", (id,))
    elif profile_type == 'teacher':
        c.execute("DELETE FROM teachers WHERE id =?", (id,))
    conn.commit()
    conn.close()

@app.route('/student_profile', methods=['GET', 'POST'])
def student_profile():
    global student_profile_count
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        contact = request.form.get('contact')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO students (name, birthday, contact) VALUES (?,?,?)", (name, birthday, contact))
        new_id = c.lastrowid
        conn.commit()
        conn.close()
        return redirect(url_for('student_profile_view', id=new_id))
    student_profile_count += 1
    return render_template('student_profile.html')

@app.route('/teacher_profile', methods=['GET', 'POST'])
def teacher_profile():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        subject = request.form.get('subject')
        teaching_time = request.form.get('teaching_time')
        contact = request.form.get('contact')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO teachers (name, birthday, subject, teaching_time, contact) VALUES (?,?,?,?,?)", (name, birthday, subject, teaching_time, contact))
        new_id = c.lastrowid
        conn.commit()
        conn.close()
        return redirect(url_for('teacher_profile_view', id=new_id))
    return render_template('teacher_profile.html')

@app.route('/student_profile_edit/<int:id>', methods=['GET', 'POST'])
def student_profile_edit(id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    profile = get_profile('student', id)
    if not profile:
        return render_template("404.html"), 404
    if request.method == 'POST':
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        contact = request.form.get('contact')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE students SET name =?, birthday =?, contact =? WHERE id =?", (name, birthday, contact, id))
        conn.commit()
        conn.close()
        return redirect(url_for('student_profile_view', id=id))
    profile_dict = {
        'id': profile[0][0],
        'name': profile[0][1],
        'birthday': profile[0][2],
        'contact': profile[0][3],
        'type': 'student'
    }
    return render_template('student_profile_edit.html', profile=profile_dict)

@app.route('/teacher_profile_edit/<int:id>', methods=['GET', 'POST'])
def teacher_profile_edit(id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    profile = get_profile('teacher', id)
    if not profile:
        return render_template("404.html"), 404
    if request.method == 'POST':
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        subject = request.form.get('subject')
        teaching_time = request.form.get('teaching_time')
        contact = request.form.get('contact')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE teachers SET name =?, birthday =?, subject =?, teaching_time =?, contact =? WHERE id =?", (name, birthday, subject, teaching_time, contact, id))
        conn.commit()
        conn.close()
        return redirect(url_for('teacher_profile_view', id=id))
    profile_dict = {
        'id': profile[0][0],
        'name': profile[0][1],
        'birthday': profile[0][2],
        'subject': profile[0][3],
        'teaching_time': profile[0][4],
        'contact': profile[0][5],
        'type': 'teacher'
    }
    return render_template('teacher_profile_edit.html', profile=profile_dict)

@app.route("/student_profile_list")
def student_profile_list():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name, id FROM students ORDER BY id")
    students = c.fetchall()
    conn.close()
    return render_template("student_profile_list.html", prof=students, count=student_profile_count)

@app.route("/teacher_profile_list")
def teacher_profile_list():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name, id FROM teachers ORDER BY id")
    teachers = c.fetchall()
    conn.close()
    return render_template("teacher_profile_list.html", prof=teachers, count=teacher_profile_count)

@app.route("/student_profile_delete/<int:id>")
def student_profile_delete(id):
    delete_profile('student', id)
    return redirect(url_for('student_profile_list'))

@app.route("/teacher_profile_delete/<int:id>")
def teacher_profile_delete(id):
    delete_profile('teacher', id)
    return redirect(url_for('teacher_profile_list'))

@app.route('/student_profile_view/<int:id>')
def student_profile_view(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    profile = get_profile('student', id)
    if not profile:
        return render_template("404.html"), 404
    profile_dict = {
        'id': profile[0][0],
        'name': profile[0][1],
        'birthday': profile[0][2],
        'contact': profile[0][3],
        'type': 'student'
    }
    return render_template('student_profile_view.html', profile=profile_dict)

@app.route('/teacher_profile_view/<int:id>')
def teacher_profile_view(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    profile = get_profile('teacher', id)
    if not profile:
        return render_template("404.html"), 404
    profile_dict = {
        'id': profile[0][0],
        'name': profile[0][1],
        'birthday': profile[0][2],
        'subject': profile[0][3],
        'teaching_time': profile[0][4],
        'contact': profile[0][5],
        'type': 'teacher'
    }
    return render_template('teacher_profile_view.html', profile=profile_dict)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

# 添加 404 错误处理函数
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    init_db()
    app.run(debug=True)