from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String, nullable=False)

class Balance(db.Model):
    payer = db.Column(db.String(100), primary_key=True)
    points = db.Column(db.Integer, nullable=False)

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)