from flask import Flask
from app.routes import routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Register Blueprint
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)
