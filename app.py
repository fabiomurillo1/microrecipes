from flask import Flask
from models import db, Recipes

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Fabitom25!@localhost/recipes_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
@app.route("/")
def index():
    return "PostgreSQL is connected!"

@app.route("/recipes")
def get_recipes():
    recipes = Recipes.query.all()
    output = []
    for recipe in recipes:
        output.append(
            f"ID: {recipe.recipeid} | Name: {recipe.name} | Description: {recipe.description} | Time: {recipe.cookingtime} mins | User ID: {recipe.userid}"
        )
    return "<br>".join(output)

if __name__ == "__main__":
    app.run(debug=True)
