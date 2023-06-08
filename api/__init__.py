from flask import Flask
from .models import db, flask_bcrypt, login_manager
from .routes import authentication


def create_app(config_class):

    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    flask_bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(authentication)

    return app