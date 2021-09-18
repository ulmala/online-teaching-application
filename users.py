import secrets
from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

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
    print(user_id, course_id)
    sql = """SELECT 1 FROM courses
             WHERE teacher_id = :user_id
             AND id = :course_id"""
    count = db.session.execute(sql, {"user_id":user_id, "course_id":course_id}).fetchall()
    if len(count) == 0:
        return False
    return True

def get_teachers_courses(user_id):
    sql = """SELECT id, name FROM courses
             WHERE teacher_id = :user_id"""
    courses = db.session.execute(sql, {"user_id":user_id}).fetchall()
    return courses