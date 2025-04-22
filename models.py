# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.Text, primary_key=True)
    uname = db.Column(db.Text, nullable=False) #first last name
    upassword = db.Column(db.Text, nullable=False)
    bio = db.Column(db.Text)
    email = db.Column(db.Text)
    isadmin = db.Column(db.Boolean, nullable=False)

class Recipe(db.Model):
    __tablename__ = 'recipes'
    recipeid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    isprivate = db.Column(db.Boolean, nullable=False)
    publisher = db.Column(db.Text, db.ForeignKey('users.username'))

class RecipeComment(db.Model):
    __tablename__ = 'recipecomments'
    commentid = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('users.username'))
    recipeid = db.Column(db.Integer, db.ForeignKey('recipes.recipeid'))
    date_posted = db.Column(db.DateTime, nullable=False)

class Cookbook(db.Model):
    __tablename__ = 'cookbook'
    author = db.Column(db.Text, primary_key=True)
    recipeid = db.Column(db.Text, primary_key=True)

class Friends(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True) #friendship id
    user_id = db.Column(db.Text, db.ForeignKey('user.username')) 
    friend_id = db.Column(db.Text, db.ForeignKey('user.username'))
    status = db.Column(db.String(20), default = 'pending') #add functionality to request friendships
    
    user = db.relationship('User', foreign_keys=[user_id], backref = 'sent_requests')
    friend = db.relationship('User', foreign_keys=[friend_id], backref = 'received_requests')