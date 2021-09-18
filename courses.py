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