from operator import methodcaller
from os import remove
import re
import courses
import users
from app import app
from flask import render_template, request, redirect, session, Response

@app.route("/")
def index():
    if "user_role" in session:
        if users.is_teacher(session["user_id"]):
            return render_template("index.html", courses=users.get_teachers_courses(session["user_id"]))
        else:
            return render_template("index.html", courses=users.get_students_courses(session["user_id"]))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not users.login(username, password):
            return render_template("error.html", message="Wrong username or password")
        return redirect("/")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":

        username = request.form["username"]
        if len(username) < 1 or len(username) > 20:
            return render_template("error.html", message="Username needs to contain 1-20 characters")

        password = request.form["password"]
        if password == "":
            return render_template("error.html", message="Password is empty!")

        role = request.form["role"]
        if role not in ("1", "2"):
            return render_template("error.html", message="U")

        if users.user_exists(username):
            return render_template("error.html", message="Username already exists!")

        if not users.register(username, password, role):
            return render_template("error.html", message="Error when registering user")
        return redirect("/")

@app.route("/all-courses")
def all_courses():
    if "user_id" in session:
        return render_template("all-courses.html", courses=courses.get_all_courses())
    return redirect("/")

@app.route("/create-course", methods=["GET", "POST"])
def create_course():
    if users.is_teacher(session["user_id"]):
        if request.method == "GET":
            return render_template("create-course.html")

        if request.method == "POST":            
            name = request.form["course_name"]
            description = request.form["description"]
            teacher_id = session["user_id"]
            file = request.files['file']
            file_name = file.filename
            file_data = file.read()
            course_id = courses.create_course(name, description, teacher_id)
            courses.upload_material(course_id, file_name, file_data)
            return redirect("/course/" + str(course_id))
        
    return redirect("/")

@app.route("/course/<int:course_id>", methods=["GET", "POST"])
def show_course(course_id):
    if "user_id" in session:
        courses.course_is_valid(course_id)
        if request.method == "GET": 
            course_info = courses.get_course_info(course_id)
            solved_tasks = users.share_of_solved_tasks(session["user_id"], course_id)
            students = courses.get_course_students(course_id)
            materials = courses.get_course_materials(course_id)
            return render_template("course.html", name=course_info["name"], description=course_info["description"],
                                    task_count=course_info["task_count"],id=course_id, solved_tasks=solved_tasks,
                                    students=students, course_id=course_id, materials=materials)
        if request.method == "POST":
            if not courses.add_student(course_id, session["user_id"]):
                return render_template("error.html", message="You are already enrolled!")

    return redirect("/")

@app.route("/add-task/<int:course_id>", methods=["GET", "POST"])
def add_task(course_id):
    users.require_role(2)
    users.is_course_teacher(session["user_id"], course_id)
    if request.method == "GET":
        return render_template("add-task.html", course_id=course_id)

    if request.method == "POST":
        question = request.form["question"]
        answer = request.form["answer"]
        correct = True #request.form.getlist("correct")
        courses.add_task(question, answer, correct, course_id)

    return redirect("/course/" + str(course_id))

@app.route("/remove/<int:course_id>", methods=["GET", "POST"])
def remove_course(course_id):
    users.require_role(2)
    users.is_course_teacher(session["user_id"], course_id)
    
    course_info = courses.get_course_info(course_id)
    if request.method == "GET":
        return render_template("remove.html", name=course_info["name"], course_id=course_id)
    if request.method == "POST":
        if request.form["choice"] == "yes":
            courses.remove_course(course_id)
            return redirect("/")
        if request.form["choice"] == "no":
            return redirect("/course/" + str(course_id))

@app.route("/solve/<int:course_id>", methods=["GET", "POST"])
def solve(course_id):
    users.require_role(1)
    if not users.is_enrolled(session["user_id"], course_id):
        return render_template("error.html", message="You need to enroll first!")
    task = courses.get_random_task(course_id)
    if request.method == "GET":
        return render_template("solve.html", question=task["question"], course_id=course_id)
    if request.method == "POST":
        user_answer = request.form["answer"]
        correct = user_answer == task["answer"]
        if correct:
            if not users.already_correct_answer(session["user_id"], task["id"]):
                users.add_solved_task(session["user_id"], task["id"])
        return render_template("result.html", correct=correct, course_id=course_id)

@app.route("/course/<int:course_id>/student-stats/<int:student_id>", methods=["GET"])
def student_stats(student_id, course_id):
    users.require_role(2)
    users.is_course_teacher(session["user_id"], course_id)
    name = users.get_username(student_id)
    share_of_solved_tasks = users.share_of_solved_tasks(student_id, course_id)
    solved_tasks = users.get_list_of_solved_tasks(student_id, course_id)
    return render_template("student-stats.html", name=name, share_of_solved_tasks=share_of_solved_tasks,
                            solved_tasks=solved_tasks)

@app.route("/update-course/<int:course_id>", methods=["GET", "POST"])
def update_course(course_id):
    users.require_role(2)
    if request.method == "GET":
        course_info = courses.get_course_info(course_id)
        materials = courses.get_course_materials(course_id)
        return render_template("update-course.html", course_id=course_id, name=course_info["name"], 
                                description=course_info["description"], materials=materials)
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        file = request.files['file']
        file_name = file.filename
        file_data = file.read()
        courses.upload_material(course_id, file_name, file_data)

        courses.update_course_info(course_id, name, description)
        return redirect("/course/" + str(course_id))

@app.route("/download/<int:material_id>", methods=["GET"])
def download(material_id):
    file = courses.get_material(material_id)
    name = file[0]
    data = file[1]
    return Response(
        data,
        mimetype="text/csv",
        headers={"Content-disposition":
                 f"attachment; filename={name}"})

@app.route("/remove-material/<int:material_id>", methods=["GET", "POST"])
def remove_material(material_id):
    users.require_role(2)
    material_info = courses.get_material_info(material_id)
    if request.method == "GET":
        return render_template("remove-material.html", material_info=material_info)
    if request.method == "POST":
        if request.form["choice"] == "yes":
            courses.remove_material(material_id)
            return redirect("/")
        if request.form["choice"] == "no":
            return redirect("/course/" + str(material_id))