from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Recipes(db.Model):
    __tablename__ = "recipes"
    recipeid = db.Column('recipeid', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100), nullable=False)
    description = db.Column('description', db.Text, nullable=False)
    cookingtime = db.Column('cookingtime', db.Integer, nullable=False)
    instructions = db.Column('instructions', db.Text, nullable=False)
    userid = db.Column('userid', db.Integer, db.ForeignKey('users.userid'), nullable=False)

class Users(db.Model):
    __tablename__ = "users"
    userid = db.Column('userid', db.Integer, primary_key=True)
    username = db.Column('username',db.String(100), unique=True, nullable=False)
    email = db.Column('email',db.String(150), unique=True, nullable=False)
    firstName = db.Column('firstname',db.String(100), nullable=False)
    lastName = db.Column('lastname', db.String(100), nullable=False)
    created_at = db.Column('created_at', db.DateTime, default=datetime.utcnow)
    password = db.Column('password',db.Text, nullable=False)

