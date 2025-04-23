from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

recipe_preferences = db.Table(
    'recipe_preferences',
    db.Column('recipeid', db.Integer, db.ForeignKey('recipes.recipeid', ondelete="CASCADE"), primary_key=True),
    db.Column('preferenceid', db.Integer, db.ForeignKey('preferences.preferenceid', ondelete="CASCADE"), primary_key=True)
)

class Recipes(db.Model):
    __tablename__ = "recipes"
    recipeid = db.Column('recipeid', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(100), nullable=False)
    description = db.Column('description', db.Text, nullable=False)
    cookingtime = db.Column('cookingtime', db.Integer, nullable=False)
    instructions = db.Column('instructions', db.Text, nullable=False)
    userid = db.Column('userid', db.Integer, db.ForeignKey('users.userid'), nullable=False)
    user = db.relationship('Users', backref='recipes')
    preferences = db.relationship('Preferences', secondary=recipe_preferences, back_populates='recipes')


class Users(UserMixin,db.Model):
    __tablename__ = "users"
    userid = db.Column('userid', db.Integer, primary_key=True)
    username = db.Column('username',db.String(100), unique=True, nullable=False)
    email = db.Column('email',db.String(150), unique=True, nullable=False)
    firstName = db.Column('firstname',db.String(100), nullable=False)
    lastName = db.Column('lastname', db.String(100), nullable=False)
    created_at = db.Column('created_at', db.DateTime, default=datetime.utcnow)
    password = db.Column('password',db.Text, nullable=False)


class Favorites(db.Model):
    __tablename__ = 'user_favorites'
    favoriteid = db.Column('favoriteid', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.userid'), nullable=False)
    recipe_id = db.Column('recipe_id',db.Integer, db.ForeignKey('recipes.recipeid'), nullable=False)
    created_at = db.Column('created_at', db.DateTime, default=datetime.utcnow)
    user = db.relationship('Users', backref='favorites')
    recipe = db.relationship('Recipes', backref='favorites')

    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_favorite'),)

class Preferences(db.Model):
    __tablename__ = 'preferences'
    preferenceid =  db.Column('preferenceid', db.Integer, primary_key=True)
    preferencename = db.Column('preferencename',db.Text, nullable=False)
    recipes = db.relationship('Recipes', secondary=recipe_preferences, back_populates='preferences')


