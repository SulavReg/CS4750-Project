from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://group32:G1qlP1N4@bastion.cs.virginia.edu:5432/group32'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'  # match your actual table name
    username = db.Column(db.Text, primary_key=True)
    uname = db.Column(db.Text, nullable=False)
    upassword = db.Column(db.Text, nullable=False)
    bio = db.Column(db.Text)
    email = db.Column(db.Text)
    isadmin = db.Column(db.Boolean, nullable=False)


@app.route('/')
def home():
    users = User.query.all()
    user_list = ', '.join([user.username for user in users])
    return f"Users: {user_list}"


if __name__ == '__main__':
    app.run(debug=True)


