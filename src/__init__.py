from flask import Flask
from src.models import db
from src.routes import routes
import os

def create_app():
    app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(__file__)) 
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "database.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    #Import and register blueprints
    app.register_blueprint(routes)

    return app
