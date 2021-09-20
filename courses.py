from db import db

def create_course(name, description, teacher_id):
    try:
        sql = """INSERT INTO courses (name, description, teacher_id)
                 VALUES (:name, :description, :teacher_id)"""
        db.session.execute(sql, {"name":name, "description":description, "teacher_id":teacher_id})
        db.session.commit()
    except:
        return False
    return True

def get_course_info(course_id):
    sql = """SELECT name, description FROM courses
             WHERE id = :course_id"""
    info = db.session.execute(sql, {"course_id":course_id}).fetchone()
    return info

def get_all_courses():
    sql = """SELECT id, name FROM courses"""
    courses = db.session.execute(sql).fetchall()
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
