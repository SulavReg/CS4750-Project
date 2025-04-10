from flask import Flask
from models import db, User, Recipe


def create_app():
    app = Flask(__name__, template_folder="app/templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://group32:G1qlP1N4@bastion.cs.virginia.edu:5432/group32'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "your-secret-key"

    db.init_app(app)

    from route import routes
    app.register_blueprint(routes)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
