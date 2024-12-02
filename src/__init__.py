from flask import Flask
from src.models import db
from src.routes import routes
import os
from flask_swagger_ui import get_swaggerui_blueprint

def create_app():
    app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(__file__)) 
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "database.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    #Configure Swagger UI for documentation
    SWAGGER_URL = "/swagger"
    API_URL = "/static/swagger.json"
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    #Import and register blueprints
    app.register_blueprint(routes)

    return app
