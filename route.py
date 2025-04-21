from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, Recipe, RecipeComment
from datetime import datetime


routes = Blueprint("routes", __name__)


# Login route
@routes.route("/", methods=["GET", "POST"])
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
    recipes = Recipe.query.all()

    return render_template("home.html", username=session["username"], recipes=recipes)


# New recipe page
@routes.route("/new_recipe", methods=["GET", "POST"])
def new_recipe():
    if "username" not in session:
        return redirect(url_for("routes.login"))

    if request.method == "POST":
        recipe_name = request.form["recipe_name"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        is_private = False

        new = Recipe(
            title=recipe_name,
            ingredients=ingredients,
            instructions=instructions,
            isprivate=is_private,
            publisher=session["username"]
        )

        db.session.add(new)
        db.session.commit()

        return redirect(url_for("routes.home"))

    return render_template("new_recipe.html")


# Recipe viewing page
@routes.route("/recipe/<int:recipe_id>")
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    comments = RecipeComment.query.filter_by(recipeid=recipe_id).order_by(RecipeComment.commentid.asc()).all()
    return render_template('view_recipe.html', recipe=recipe, comments=comments)

  
@routes.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if "username" not in session:
        return redirect(url_for("routes.login"))

    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.publisher != session["username"]:
        return "Unauthorized", 403

    if request.method == "POST":
        recipe.title = request.form["recipe_name"]
        recipe.ingredients = request.form["ingredients"]
        recipe.instructions = request.form["instructions"]
        db.session.commit()
        return redirect(url_for("routes.home"))

    return render_template("edit_recipe.html", recipe=recipe)

@routes.route("/delete_recipe/<int:recipe_id>", methods=["POST"])
def delete_recipe(recipe_id):
    if "username" not in session:
        return redirect(url_for("routes.login"))

    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.publisher != session["username"]:
        return "Unauthorized", 403

    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for("routes.home"))


# Logout
@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))
