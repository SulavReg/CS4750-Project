from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Recipe, RecipeComment, Cookbook, Friends
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

    # Get the current logged-in user from session
    username = session["username"]

    # Query to get all recipes created by the logged-in user (including private ones)
    user_recipes = Recipe.query.filter_by(publisher=username).all()

    # Query to get all public recipes or recipes that are private but owned by the logged-in user
    other_recipes = Recipe.query.filter(
        (Recipe.isprivate == False) & (Recipe.publisher != username)
    ).all()

    # You can also pass `user_recipes` and `other_recipes` to the template as before
    return render_template("home.html", user_recipes=user_recipes, other_recipes=other_recipes)


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

#routes for friendship functionality (add_friend, view_friend_requests, accept_friend, reject_friend, view_friends)
@routes.route("/add_friend/<string:friend_username>", methods=["POST"])
def add_friend(friend_username): #user sends a friend request to another user
    if "username" not in session:
        return redirect(url_for("routes.login"))
    user = User.query.filter_by(username=session["username"]).first()
    friend = User.query.filter_by(username=friend_username).first()
    if not friend: #check friend exists
        flash("User not found!")
        return redirect(url_for("routes.home"))

    existing_request = Friends.query.filter(#added to check if the friendship alr exists
        (Friends.user_id==user.username) &(Friends.friend_id==friend.username) |
        (Friends.user_id==friend.username)&(Friends.friend_id==user.username)
    ).first()
    if existing_request:
        #flash("Friendship already exists or is pending")
        return redirect(url_for("routes.home"))
    
    #make request set to pending
    request = Friends(user_id=user.username, friend_id=friend.username, status='pending')
    db.session.add(request)
    db.session.commit()

    #return to user profile page
    return redirect(url_for("routes.view_user_profile", username=friend.username))

@routes.route("/view_friend_requests", methods=["GET"])
def view_friend_requests():
    if "username" not in session:
        return redirect(url_for("routes.login"))
    
    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        return redirect(url_for("routes.home"))
    
    #get incoming pending requests
    pending_requests = Friends.query.filter(
        Friends.friend_id == user.username,
        Friends.status == 'pending'
    ).all()
    
    pending_usernames = [request.user_id for request in pending_requests]
    #debugging: print("Pending Usernames:", pending_usernames)
    pending_users = User.query.filter(User.username.in_(pending_usernames)).all()

    #debugging:
    # print("Pending Requests:", pending_requests)
    # print("Pending Users:", pending_users)
    return render_template("view_friend_requests.html", pending_requests=pending_requests, pending_users=pending_users)


@routes.route("/accept_friend/<string:friend_username>", methods = ["POST"])#accept friend request
def accept_friend(friend_username):
    if "username" not in session:
        return redirect(url_for("routes.login"))
    user =User.query.filter_by(username=session["username"]).first()
    friend = User.query.filter_by(username=friend_username).first()
    if not friend: #check taht friend exist
        flash("User not found :(")
        return redirect(url_for("routes.home"))
    #find the request to accept--
    request= Friends.query.filter(
        Friends.user_id == friend.username,
        Friends.friend_id == user.username,
        Friends.status == 'pending'
    ).first()
    if not request: 
        flash("No request to accept:(")
        return redirect(url_for("routes.home"))
    request.status = 'accepted'
    db.session.commit()
    flash("You are friends now!")
    return redirect(url_for("routes.home"))

@routes.route("/reject_friend/<string:friend_username>", methods =["POST"])
def reject_friend(friend_username):
    if "username" not in session:
        return redirect(url_for("routes.login"))
    user = User.query.filter_by(username=session["username"]).first()
    friend = User.query.filter_by(username=friend_username).first()
    if not friend:
        flash("User not found :(")
        return redirect(url_for("routes.home"))
    #find request to reject
    request = Friends.query.filter(
        Friends.user_id == friend.username,
        Friends.friend_id == user.username,
        Friends.status == 'pending'
    ).first()
    if not request:  #no pending request exists
        flash("No request to reject")
        return redirect(url_for("routes.home"))
    db.session.delete(request)
    db.session.commit()
    return redirect(url_for("routes.home"))

@routes.route("/view_friends", methods=["GET"])
def view_friends(): #see ur friends list
    if "username" not in session: 
        return redirect(url_for("routes.home"))
    
    user= User.query.filter_by(username=session["username"]).first()
    #get list of accepted friends--
    friends = Friends.query.filter(
        (Friends.user_id==user.username)|(Friends.friend_id==user.username), 
        Friends.status=='accepted'
    ).all()

    friend_usernames=[]
    for friend in friends:
        if friend.user_id==user.username:
            friend_usernames.append(friend.friend_id)
        else:
            friend_usernames.append(friend.user_id)
    friend_users = User.query.filter(User.username.in_(friend_usernames)).all()  #get the user objects for each friend
    return render_template("view_friends.html", friends=friend_users)

@routes.route("/user/<username>", methods=["GET", "POST"]) #view others + with edits to check friendship status
def view_user_profile(username): 
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found")
        return redirect(url_for("routes.home"))
    #add stuff to check friendship status
    current_user = User.query.filter_by(username=session["username"]).first()
    existing_request = Friends.query.filter(
        ((Friends.user_id == current_user.username) & (Friends.friend_id == user.username)) |
        ((Friends.user_id == user.username) & (Friends.friend_id == current_user.username))
    ).first()

    recipes = Recipe.query.filter_by(publisher=username).all()
    #return render_template("user_profile.html", user=user, recipes=recipes)
    return render_template("user_profile.html", user=user, recipes=recipes, existing_request=existing_request)

@routes.route("/my_profile")
def view_my_profile(): #can view own friends list and cookbook, too
    username = session.get("username")
    if not username: 
       # flash("Login please!")
        return redirect(url_for("routes.login"))
    user = User.query.filter_by(username=username).first()
    if not user:
      #  flash("User not found")
        return redirect(url_for("routes.home"))
    my_recipes = Recipe.query.filter_by(publisher = username).all()
    cookbook_entries = Cookbook.query.filter_by(author = username).all()
    cookbook_recipe_ids =[entry.recipeid for entry in cookbook_entries]
    return render_template("my_profile.html", user=user,user_recipes=my_recipes, cookbook_recipes=cookbook_recipe_ids)

@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))
