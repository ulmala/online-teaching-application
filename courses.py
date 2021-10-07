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
    sql = """SELECT courses.name, courses.description, COUNT(tasks.id) as task_count
             FROM courses LEFT JOIN tasks ON courses.id = tasks.course_id
             WHERE courses.id=:course_id
             GROUP BY courses.id"""
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

def add_task(question, answer, correct, course_id):
    sql = """INSERT INTO tasks (course_id, question)
             VALUES (:course_id, :question)
             RETURNING id"""

    task_id = db.session.execute(sql, {"course_id":course_id, "question":question}).fetchone()[0]
    
    sql = """INSERT INTO answers (task_id, answer, correct)
             VALUES (:task_id, :answer, :correct)"""
    db.session.execute(sql, {"task_id":task_id, "answer":answer, "correct":correct})
    db.session.commit()

def remove_course(course_id):
    sql = "UPDATE courses SET visible=:visible WHERE id=:id"
    db.session.execute(sql, {"id":course_id, "visible":False})
    db.session.commit()

def get_random_task(course_id):
    sql = """SELECT T.id, T.question, A.answer, A.correct
             FROM tasks T, answers A
             WHERE T.course_id=:course_id
             AND T.id=A.task_id
             ORDER BY RANDOM()
             LIMIT 1"""
    task = db.session.execute(sql, {"course_id":course_id}).fetchone()
    return dict(zip(task.keys(), task))

def get_task_count(course_id):

    # LOITSU MITEN SAA TÄMÄN KURSSIN TIETOJEN KANSSA SAMAAN LOITSUUN!

    sql = """SELECT COUNT(*) FROM tasks
             WHERE course_id=:course_id"""
    count = db.session.execute(sql, {"course_id":course_id}).fetchone()[0]
    return count

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

def upload_material(course_id, name, data):
    sql = """INSERT INTO materials(course_id, name, data)
             VALUES (:course_id, :name, :data)"""
    db.session.execute(sql, {"course_id":course_id, "name":name, "data":data})
    db.session.commit()

def get_course_materials(course_id):
    sql = """SELECT id, name
             FROM materials
             WHERE course_id=:course_id"""
    materials = db.session.execute(sql, {"course_id":course_id}).fetchall()
    return materials

def get_material(material_id):
    sql = """SELECT name, data
             FROM materials
             WHERE id=:material_id"""
    materials = db.session.execute(sql, {"material_id":material_id}).fetchone()
    print(materials)
    return materials