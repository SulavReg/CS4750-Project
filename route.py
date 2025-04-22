from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Recipe, RecipeComment, Cookbook
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
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
        bio = request.form["bio"]
        email = request.form["email"]
        isadmin = False

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different username.")
            return redirect(url_for("routes.signup"))

        new_user = User(
            username=username,
            uname=f"{first_name} {last_name}",
            upassword=password,
            bio=bio,
            email=email,
            isadmin=isadmin
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("routes.login"))

    return render_template("signup.html")


# Home page
@routes.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("routes.login"))
    recipes = Recipe.query.all()
    user_recipes = [recipe for recipe in recipes if recipe.publisher == session["username"]]
    other_recipes = [recipe for recipe in recipes if recipe.publisher != session["username"]]
    cookbook_entries = Cookbook.query.filter_by(author=session["username"]).all()
    cookbook_recipes = {entry.recipeid for entry in cookbook_entries}

    return render_template("home.html", username=session["username"], user_recipes=user_recipes,
                           other_recipes=other_recipes, cookbook_recipes=cookbook_recipes)


# New recipe page
@routes.route("/new_recipe", methods=["GET", "POST"])
def new_recipe():
    if "username" not in session:
        return redirect(url_for("routes.login"))

    if request.method == "POST":
        recipe_name = request.form["recipe_name"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        privacy = request.form["privacy"]
        is_private = privacy == "private"

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


@routes.route("/recipe_cookbook/<int:recipe_id>")
def view_recipe_from_cookbook(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    comments = RecipeComment.query.filter_by(recipeid=recipe_id).order_by(RecipeComment.commentid.asc()).all()
    return render_template('view_recipe_from_cookbook.html', recipe=recipe, comments=comments)


@routes.route("/cookbook")
def view_cookbook():
    if "username" not in session:
        return redirect(url_for("routes.login"))

    cookbook = Cookbook.query.filter_by(author=session["username"]).all()
    recipe_ids = [entry.recipeid for entry in cookbook]
    recipes = Recipe.query.filter(Recipe.recipeid.in_(recipe_ids)).all()

    return render_template('view_cookbook.html', recipes=recipes)


@routes.route("/add_to_cookbook/<int:recipe_id>", methods=["POST"])
def add_to_cookbook(recipe_id):
    if "username" not in session:
        return redirect(url_for("routes.login"))

    username = session["username"]

    existing_entry = Cookbook.query.filter_by(author=username, recipeid=recipe_id).first()
    if existing_entry:
        flash("Recipe is already in your cookbook.")
    else:
        new_entry = Cookbook(author=username, recipeid=recipe_id)
        db.session.add(new_entry)
        db.session.commit()
        flash("Recipe added to your cookbook!")
    return redirect(url_for("routes.home"))


@routes.route("/remove_from_cookbook/<int:recipe_id>", methods=["POST"])
def remove_from_cookbook(recipe_id):
    if "username" not in session:
        return redirect(url_for("routes.login"))

    username = session["username"]

    entry = Cookbook.query.filter_by(author=username, recipeid=recipe_id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return redirect(url_for("routes.view_cookbook"))


@routes.route("/remove_from_cookbook_homeview/<int:recipe_id>", methods=["POST"])
def remove_from_cookbook_homeview(recipe_id):
    if "username" not in session:
        return redirect(url_for("routes.login"))

    username = session["username"]

    entry = Cookbook.query.filter_by(author=username, recipeid=recipe_id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return redirect(url_for("routes.home"))

  
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
        privacy = request.form["privacy"]
        recipe.isprivate = privacy =="private"
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
