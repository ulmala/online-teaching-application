import courses
import users
from app import app
from flask import render_template, request, redirect, session

@app.route("/")
def index():
    if "user_role" in session:
        if users.is_teacher(session["user_id"]):
            return render_template("index.html", courses=users.get_teachers_courses(session["user_id"]))
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
            courses.create_course(name, description, teacher_id)
        
    return redirect("/")

@app.route("/course/<int:course_id>")
def show_course(course_id):
    if "user_id" in session:
        course_info = courses.get_course_info(course_id)
        return render_template("course.html", name=course_info[0], description=course_info[1])
    return redirect("/")
