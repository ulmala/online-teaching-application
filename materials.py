from db import db

def upload_materials(course_id, name, data):
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
    return materials

def remove_material(material_id):
    sql = """DELETE FROM materials
             WHERE id=:material_id"""
    db.session.execute(sql, {"material_id":material_id})
    db.session.commit()

def get_material_info(material_id):
    sql = """SELECT id, name, course_id
             FROM materials
             WHERE id=:material_id"""
    info = db.session.execute(sql, {"material_id":material_id}).fetchone()
    return info