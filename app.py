from flask import Flask, render_template, request
from models import db, Recipes, Users

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
