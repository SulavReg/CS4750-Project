# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.Text, primary_key=True)
    uname = db.Column(db.Text, nullable=False)
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
