from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, Recipe

routes = Blueprint("routes", __name__)

# your login, home, new_recipe, logout routes here


# Login route
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, upassword=password).first()
        if user:
            session["username"] = user.username
            return redirect(url_for("routes.home"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")


# Home page
@routes.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("routes.login"))

    return render_template("home.html", username=session["username"])


# New recipe page
@routes.route("/new_recipe", methods=["GET", "POST"])
def new_recipe():
    if "username" not in session:
        return redirect(url_for("routes.login"))

    if request.method == "POST":
        recipe_name = request.form["recipe_name"]
        description = request.form["description"]
        # Insert into DB - assuming you have a Recipe model

        # e.g.:
        # new_recipe = Recipe(name=recipe_name, description=description, creator=session["username"])
        # db.session.add(new_recipe)
        # db.session.commit()

        return redirect(url_for("routes.home"))

    return render_template("new_recipe.html")


# Logout
@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))
