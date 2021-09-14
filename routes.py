import users
from app import app
from flask import render_template, request, redirect, session, flash

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["get", "post"])
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