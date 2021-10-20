from db import db
from flask import session, abort

def create_course(name, description, teacher_id):
    try:
        sql = """INSERT INTO courses (name, description, teacher_id, visible)
                 VALUES (:name, :description, :teacher_id, :visible) RETURNING id"""         
        course_id = db.session.execute(sql, {"name":name, "description":description,
                                             "teacher_id":teacher_id, "visible":True}).fetchone()[0]
        db.session.commit()
    except:
        return False
    return course_id

def get_course_info(course_id):
    sql = """SELECT name, description
             FROM courses
             WHERE courses.id=:course_id;"""
    info = db.session.execute(sql, {"course_id":course_id}).fetchone()
    return dict(zip(info.keys(), info))

def get_all_courses():
    sql = """SELECT id, name FROM courses
             WHERE visible=:visible"""
    courses = db.session.execute(sql, {"visible":True}).fetchall()
    return courses

def add_student(course_id, student_id):
    sql = """INSERT INTO course_students (course_id, student_id)
             VALUES (:course_id, :student_id)"""
    try:
        db.session.execute(sql, {"course_id":course_id, "student_id":student_id})
        db.session.commit()
    except:
        return False
    return True

def add_task(question, answer, correct, course_id, task_type):
    sql = """INSERT INTO tasks (course_id, question, task_type, visible)
             VALUES (:course_id, :question, :task_type, true)
             RETURNING id"""

    task_id = db.session.execute(sql, {"course_id":course_id, "question":question,
                                       "task_type":task_type}).fetchone()[0]
    
    if task_type == "basic":
        sql = """INSERT INTO answers (task_id, answer, correct)
                VALUES (:task_id, :answer, :correct)"""
        db.session.execute(sql, {"task_id":task_id, "answer":answer, "correct":correct})
        db.session.commit()
    else:
        for a in answer:
            sql = """INSERT INTO answers (task_id, answer, correct)
                    VALUES (:task_id, :answer, :correct)"""
            db.session.execute(sql, {"task_id":task_id, "answer":a[0], "correct":a[1]})
            db.session.commit()

def remove_course(course_id):
    sql = "UPDATE courses SET visible=:visible WHERE id=:id"
    db.session.execute(sql, {"id":course_id, "visible":False})
    db.session.commit()

def get_random_task(course_id):
    sql = """SELECT T.id, T.question, T.task_type, A.answer, A.correct
             FROM tasks T, answers A
             WHERE T.course_id=:course_id
             AND T.id=A.task_id
             AND T.visible=true
             ORDER BY RANDOM()
             LIMIT 1"""
    task = db.session.execute(sql, {"course_id":course_id}).fetchone()
    task = dict(zip(task.keys(), task))
    if task["task_type"] == "multiple":
        sql = """SELECT answer, correct FROM answers
                WHERE task_id=:task_id"""
        choices = db.session.execute(sql, {"task_id":task["id"]}).fetchall()
        choices = [list(c) for c in choices]
    else:
        choices = None
    return task, choices

def get_task_count(course_id):
    sql = """SELECT COUNT(*) FROM tasks
             WHERE course_id=:course_id
             AND visible=true"""
    count = db.session.execute(sql, {"course_id":course_id}).fetchone()[0]
    return count

def get_all_course_tasks(course_id):
    sql = """SELECT id, question
             FROM tasks
             WHERE course_id=:course_id
             AND visible=true"""
    tasks = db.session.execute(sql, {"course_id":course_id}).fetchall()
    return tasks

def get_task(task_id):
    sql = """SELECT id, question, course_id
             FROM tasks
             WHERE id=:task_id"""
    task = db.session.execute(sql, {"task_id":task_id}).fetchone()
    return task

def remove_task(task_id):
    sql = "UPDATE tasks SET visible=:visible WHERE id=:task_id"
    db.session.execute(sql, {"visible":False, "task_id":task_id})
    db.session.commit()

def get_course_students(course_id):
    sql = """SELECT username, student_id
             FROM course_students
             JOIN users ON course_students.student_id=users.id
             WHERE course_id=:course_id"""
    students = db.session.execute(sql, {"course_id":course_id}).fetchall()
    return students

def course_is_valid(course_id):
    sql = """SELECT visible
             FROM courses
             WHERE id=:course_id"""
    visible = db.session.execute(sql, {"course_id":course_id}).fetchone()[0]
    if not visible:
        abort(403)

def update_course_info(course_id, name, description):
    sql = """UPDATE courses
             SET name=:name, description=:description
             WHERE id=:course_id"""
    db.session.execute(sql, {"name":name, "description":description, "course_id":course_id})
    db.session.commit()
