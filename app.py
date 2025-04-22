from flask import Flask, render_template, request, redirect, flash, url_for, session
from models import db, Recipes, Users
from werkzeug.security import generate_password_hash, check_password_hash
import sys

app = Flask(__name__)
app.secret_key = 'f9d8a3d2a93c47d2a4ecb7df6fbd9f3c'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Fabitom25!@localhost/recipes_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recipes")
def get_recipes():
    recipes = Recipes.query.all()
    output = []
    for recipe in recipes:
        output.append(
            f"ID: {recipe.recipeid} | Name: {recipe.name} | Description: {recipe.description} | Time: {recipe.cookingtime} mins | User ID: {recipe.userid} | Instructions : {recipe.instructions} "
        )
    return "<br>".join(output)

@app.route("/users")
def get_users():
    users = Users.query.all()
    output = []
    for user in users:
        output.append(
            f"ID: {user.userid} | Username: {user.username} | Email: {user.email} | Name: {user.firstname} {user.lastname} | Creation Date: {user.created_at}"
        )
    return "<br>".join(output)

@app.route("/search")
def search():
    query = request.args.get("query")

    if query.isdigit():
        results = Recipes.query.filter_by(recipeid=int(query)).all()
    else:
        results = Recipes.query.filter(Recipes.name.ilike(f"%{query}%")).all()
    return render_template("search_results.html", results=results)

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect(url_for('index'))

    hashed_password = generate_password_hash(password)

    new_user = Users(
        firstName=first_name,
        lastName=last_name,
        email=email,
        username=username,
        password=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        print("User created with ID:", new_user.userid, file=sys.stderr)
        flash("User registered successfully!")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}")

    return redirect(url_for('index'))

@app.route("/login", methods=["POST"])
def login():
    username_or_email = request.form["username"]
    password = request.form["password"]
    user = Users.query.filter((Users.username == username_or_email) | (Users.email == username_or_email)).first()

    if user and check_password_hash(user.password, password):
        session["user_id"] = user.userid
        flash("Login successful!", "success")
        return redirect(url_for("index"))
    else:
        flash("Invalid credentials", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
