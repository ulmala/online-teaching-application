from db import db

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
    sql = """SELECT name, description FROM courses
             WHERE id = :course_id"""
    info = db.session.execute(sql, {"course_id":course_id}).fetchone()
    return info

def get_all_courses():
    sql = """SELECT id, name FROM courses
             WHERE visible = :visible"""
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
             WHERE T.course_id = :course_id
             AND T.id = A.task_id
             ORDER BY RANDOM()
             LIMIT 1"""
    task = db.session.execute(sql, {"course_id":course_id}).fetchone()
    return dict(zip(task.keys(), task))