from flask_sqlalchemy import SQLAlchemy

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
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

