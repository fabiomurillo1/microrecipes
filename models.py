# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Recipes(db.Model):
    __tablename__ = "recipes"
    recipeid = db.Column('recipeid', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100), nullable=False)
    description = db.Column('description', db.String(100), nullable=False)
    cookingtime = db.Column('cookingtime', db.Integer, nullable=False)
    userid = db.Column('userid', db.Integer, nullable=False)
