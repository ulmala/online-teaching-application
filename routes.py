from flask import render_template, request, redirect, session, Response
import courses
import users
import materials
from app import app

@app.route("/")
def index():
    if "user_role" in session:
        if users.is_teacher(session["user_id"]):
            return render_template("index.html",
                                   courses=users.get_teachers_courses(session["user_id"]))
        return render_template("index.html",
                                courses=users.get_students_courses(session["user_id"]))
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_role" in session:
        return redirect("/")
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
            return render_template("error.html",
                                   message="Username needs to contain 1-20 characters")
        password = request.form["password"]
        if password == "":
            return render_template("error.html", message="Password is empty!")
        role = request.form["role"]
        if users.user_exists(username):
            return render_template("error.html",
                                   message="Username already exists!")
        if not users.register(username, password, role):
            return render_template("error.html",
                                   message="Error when registering user")
        return redirect("/")

@app.route("/all-courses", methods=["GET"])
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
            users.check_csrf()
            name = request.form["course_name"]
            if len(name) < 1 or len(name) > 20:
                return render_template("error.html",
                    message="Course name must be between 1 and 20 chars!")
            description = request.form["description"]
            if len(description) < 20 or len(description) > 2000:
                return render_template("error.html",
                                       message="Description must be between 20 and 2000 chars")
            teacher_id = session["user_id"]
            file = request.files['file']
            file_name = file.filename
            file_data = file.read()
            if len(file_data) == 0:
                return render_template("error.html",
                                       message="Course must have one material at the start!")
            course_id = courses.create_course(name, description, teacher_id)
            materials.upload_materials(course_id, file_name, file_data)
            return redirect("/course/" + str(course_id))
    return redirect("/")

@app.route("/course/<int:course_id>", methods=["GET", "POST"])
def course(course_id):
    if "user_id" in session:
        courses.course_is_valid(course_id)
        if request.method == "GET":
            enrolled = users.is_enrolled(session["user_id"], course_id)
            course_info = courses.get_course_info(course_id)
            solved_tasks = users.share_of_solved_tasks(session["user_id"], course_id)
            task_count = courses.get_task_count(course_id)
            students = courses.get_course_students(course_id)
            course_materials = materials.get_course_materials(course_id)
            return render_template("course.html", name=course_info["name"],
                                   description=course_info["description"], task_count=task_count,
                                   id=course_id, solved_tasks=solved_tasks,
                                   students=students, course_id=course_id,
                                   materials=course_materials, enrolled=enrolled)
        if request.method == "POST":
            users.check_csrf()
            if not courses.add_student(course_id, session["user_id"]):
                return render_template("error.html", message="You are already enrolled!")

    return redirect("/")

@app.route("/add-task/<int:course_id>", methods=["GET", "POST"])
def add_task(course_id):
    users.require_role(2)
    users.is_course_teacher(session["user_id"], course_id)
    task_type = request.args["type"]
    if request.method == "GET":
        return render_template("add-task.html", course_id=course_id, task_type=task_type)
    if request.method == "POST":
        users.check_csrf()
        if task_type == "basic":
            question = request.form["question"]
            if len(question) < 10 or len(question) > 200:
                return render_template("error.html",
                                       message="Question must be between 10 and 200 chars!")
            answer = request.form["answer"]
            if len(answer) == 0:
                return render_template("error.html",
                                       message="Answer must be at least one character long!")
            correct = True
            courses.add_task(question, answer, correct, course_id, task_type)
        elif task_type == "multiple":
            question = request.form["question"]
            if len(question) < 10 or len(question) > 200:
                return render_template("error.html",
                                       message="Question must be between 10 and 200 chars!")
            choices = request.form.getlist("choice")
            if len(min(choices, key=len)) == 0:
                return render_template("error.html",
                                       message="Every choice must have at least one character!")
            if not "correct" in request.form:
                return render_template("error.html",
                                       message="You need to mark the correct answer!")
            correct_choice = int(request.form["correct"])
            answers = []
            for i in range(3):
                correct = False
                if i + 1 == correct_choice:
                    correct = True
                answers.append((choices[i], correct))
            courses.add_task(question, answers, correct, course_id, task_type)

    return redirect("/course/" + str(course_id))

@app.route("/remove-task/<int:task_id>", methods=["GET", "POST"])
def remove_task(task_id):
    users.require_role(2)
    task_info = courses.get_task(task_id)
    if request.method == "GET":
        return render_template("remove-task.html", task_info=task_info)
    if request.method == "POST":
        users.check_csrf()
        if request.form["choice"] == "yes":
            courses.remove_task(task_id)
            return redirect("/")
        if request.form["choice"] == "no":
            return redirect("/update-course/" + str(task_info[2]))

@app.route("/remove/<int:course_id>", methods=["GET", "POST"])
def remove_course(course_id):
    users.require_role(2)
    users.is_course_teacher(session["user_id"], course_id)

    course_info = courses.get_course_info(course_id)
    if request.method == "GET":
        return render_template("remove.html", name=course_info["name"], course_id=course_id)
    if request.method == "POST":
        users.check_csrf()
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
    if request.method == "GET":
        task, choices = courses.get_random_task(course_id)
        session["task"] = dict(task)
        if choices is not None:
            session["choices"] = choices
        return render_template("solve.html", question=task["question"], course_id=course_id,
                               task_type=task["task_type"], choices=choices, task_id=task["id"])
    if request.method == "POST":
        users.check_csrf()
        task = session["task"]
        if task["task_type"] == "basic":
            user_answer = request.form["answer"]
            if len(user_answer) == 0:
                return render_template("error.html", message="You must answer something!")
            correct = user_answer == task["answer"]
        else:
            choices = session["choices"]
            if not "answer" in request.form:
                return render_template("error.html", message="You must answer something!")
            user_answer = int(request.form["answer"])
            correct = choices[user_answer][1]
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
    return render_template("student-stats.html", name=name,
                           share_of_solved_tasks=share_of_solved_tasks,
                           solved_tasks=solved_tasks)

@app.route("/update-course/<int:course_id>", methods=["GET", "POST"])
def update_course(course_id):
    users.require_role(2)
    if request.method == "GET":
        course_info = courses.get_course_info(course_id)
        course_materials = materials.get_course_materials(course_id)
        course_tasks = courses.get_all_course_tasks(course_id)
        return render_template("update-course.html", course_id=course_id, name=course_info["name"],
                                description=course_info["description"], materials=course_materials,
                                course_tasks=course_tasks)
    if request.method == "POST":
        users.check_csrf()
        name = request.form["name"]
        description = request.form["description"]

        if len(name) < 1 or len(name) > 20:
            return render_template("error.html",
                                   message="Course name must be between 1 and 20 chars!")
        if len(description) < 20 or len(description) > 2000:
            return render_template("error.html",
                                   message="Description must be between 20 and 2000 chars")

        file = request.files['file']
        file_name = file.filename
        file_data = file.read()
        if len(file_data) > 0:
            materials.upload_materials(course_id, file_name, file_data)

        courses.update_course_info(course_id, name, description)
        return redirect("/course/" + str(course_id))

@app.route("/download/<int:material_id>", methods=["GET"])
def download(material_id):
    file = materials.get_material(material_id)
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
    material_info = materials.get_material_info(material_id)
    if request.method == "GET":
        return render_template("remove-material.html", material_info=material_info)
    if request.method == "POST":
        users.check_csrf()
        if request.form["choice"] == "yes":
            materials.remove_material(material_id)
            return redirect("/")
        if request.form["choice"] == "no":
            return redirect("/update-course/" + str(material_info[2]))
