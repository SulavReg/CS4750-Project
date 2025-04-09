import os
from flask import Flask
from models import db, User, Recipe

def create_app():
    app = Flask(__name__, template_folder="app/templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('FLASK_SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

    db.init_app(app)

    from route import routes
    app.register_blueprint(routes)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
