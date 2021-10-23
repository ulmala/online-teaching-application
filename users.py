import secrets
from flask import session, abort, request
from werkzeug.security import check_password_hash, generate_password_hash
from db import db

def login(username, password):
    sql = "SELECT password, id, role FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    if not check_password_hash(user[0], password):
        return False
    session["user_id"] = user[1]
    session["username"] = username
    session["user_role"] = user[2]
    session["csrf_token"] = secrets.token_hex(16)
    return True

def logout():
    del session["user_id"]
    del session["username"]
    del session["user_role"]
    del session["csrf_token"]

def register(username, password, role):
    hash_value = generate_password_hash(password)
    try:
        sql = """INSERT INTO users (username, password, role)
                 VALUES (:username, :password, :role)"""
        db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
        db.session.commit()
    except:
        return False
    return login(username, password)

def user_exists(username):
    sql = """SELECT 1 FROM users
            WHERE USERNAME = :username"""
    count = db.session.execute(sql, {"username":username}).fetchall()
    if len(count) == 0:
        return False
    return True

def is_teacher(user_id):
    sql = """SELECT role FROM users
            WHERE id = :user_id"""
    role = db.session.execute(sql, {"user_id":user_id}).fetchone()[0]
    if role == 2:
        return True
    return False

def is_course_teacher(user_id, course_id):
    sql = """SELECT 1 FROM courses
             WHERE teacher_id = :user_id
             AND id = :course_id"""
    count = db.session.execute(sql, {"user_id":user_id, "course_id":course_id}).fetchall()
    if len(count) == 0:
        abort(403)

def get_teachers_courses(user_id):
    sql = """SELECT id, name FROM courses
             WHERE teacher_id = :user_id
             and visible = :visible"""
    courses = db.session.execute(sql, {"user_id":user_id, "visible":True}).fetchall()
    return courses

def get_students_courses(user_id):
    sql = """SELECT C.name, C.id, C.visible
             FROM users U, courses C, course_students E
             WHERE U.id = E.student_id
             AND C.id = E.course_id
             AND U.id = :user_id
             AND C.visible = :visible"""
    courses = db.session.execute(sql, {"user_id":user_id, "visible":True}).fetchall()
    return courses

def require_role(role):
    if role > session.get("user_role", 0):
        abort(403)

def is_enrolled(user_id, course_id):
    courses = get_students_courses(user_id)
    course_ids = [course[1] for course in courses]
    if course_id in course_ids:
        return True
    return False

def already_correct_answer(user_id, task_id):
    sql = """SELECT 1 FROM results
             WHERE user_id = :user_id
             AND task_id = :task_id
             AND result = 1"""
    rows = db.session.execute(sql, {"user_id":user_id, "task_id":task_id}).fetchall()
    if len(rows) == 0:
        return False
    return True

def add_solved_task(user_id, task_id):
    sql = """INSERT INTO results (user_id, task_id, result)
            VALUES (:user_id, :task_id, :result)"""
    db.session.execute(sql, {"user_id":user_id, "task_id":task_id, "result":1})
    db.session.commit()

def share_of_solved_tasks(user_id, course_id):
    sql = """SELECT COUNT(*) FROM tasks
             WHERE course_id=:course_id
             AND visible=true"""
    count = db.session.execute(sql, {"course_id":course_id}).fetchone()[0]

    sql = """SELECT COUNT(*) FROM tasks
             JOIN results ON tasks.id = results.task_id
             WHERE course_id=:course_id
             AND user_id=:user_id
             AND result=1
             AND visible=true"""
    solved = db.session.execute(sql, {"course_id":course_id, "user_id":user_id}).fetchone()[0]
    if count > 0:
        return round((solved/count)*100,2)
    return 0.0

def get_username(user_id):
    sql = """SELECT username
             FROM users
             WHERE id=:user_id"""
    name = db.session.execute(sql, {"user_id":user_id}).fetchone()[0]
    return name

def get_list_of_solved_tasks(user_id, course_id):
    sql = """SELECT question FROM tasks
             JOIN results ON tasks.id=results.task_id
             WHERE course_id=:course_id
             AND user_id=:user_id
             and result=1"""
    solved = db.session.execute(sql, {"user_id":user_id, "course_id":course_id}).fetchall()
    return solved

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
