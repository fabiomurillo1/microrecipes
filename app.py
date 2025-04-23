from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_login import current_user,login_required, LoginManager, logout_user, login_user
from models import db, Recipes, Users, Favorites, Preferences, recipe_preferences
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import String, text
import sys
import os

app = Flask(__name__)
app.secret_key = 'f9d8a3d2a93c47d2a4ecb7df6fbd9f3c'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Fabitom25!@localhost/recipes_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Define the login view, in case the user isn't logged in

app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recipes")
@app.route("/recipes")
def get_recipes():
    query = request.args.get("query", "").strip()
    sort = request.args.get("sort")
    user_id = session.get("user_id")
    preference_filter = request.args.get("preference")

    if user_id is None:
        flash("Please log in to view recipes.")
        return redirect(url_for("login"))

    # Start building the query with joins
    recipes = (
        db.session.query(Recipes)
        .join(recipe_preferences)
        .join(Preferences)
    )

    # Filter by search query (matches recipe name or preference name)
    if query:
        recipes = recipes.filter(
            or_(
                Recipes.name.ilike(f"%{query}%"),
                Preferences.preferencename.ilike(f"%{query}%")
            )
        )

    # Optional dropdown filter by specific preference
    if preference_filter:
        recipes = recipes.filter(Preferences.preferencename == preference_filter)

    # Sorting
    if sort == "asc":
        recipes = recipes.order_by(Recipes.name.asc())
    elif sort == "desc":
        recipes = recipes.order_by(Recipes.name.desc())

    # Finalize query
    recipes = recipes.all()

    # Get favorite recipe IDs
    favorite_ids = db.session.query(Favorites.recipe_id).filter_by(user_id=user_id).all()
    favorite_ids = [f[0] for f in favorite_ids]

    # Send all preferences for dropdown
    all_preferences = Preferences.query.order_by(Preferences.preferencename).all()

    return render_template("recipes.html", recipes=recipes, favorite_ids=favorite_ids, all_preferences=all_preferences)


@app.route("/view_all_recipes", methods=["GET", "POST"])
def view_all_recipes():
    if "user_id" not in session:
        flash("Please log in to view all recipes.")
        return redirect(url_for("login"))

    # Get all recipes
    recipes = Recipes.query.all()

    # Get the IDs of the favorite recipes for the current user
    favorite_recipes = Favorites.query.filter_by(user_id=session["user_id"]).all()
    favorite_ids = [fav.recipe_id for fav in favorite_recipes]

    return render_template("recipes.html", recipes=recipes, favorite_ids=favorite_ids)
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



    new_user = Users(
        firstName=first_name,
        lastName=last_name,
        email=email,
        username=username,
        password=password
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

    # Look for user based on username or email
    user = Users.query.filter(
        (Users.username == username_or_email) | (Users.email == username_or_email)
    ).first()

    # Check if user exists and if password matches
    if user and user.password == password:  # No hash check as requested
        session["user_id"] = user.userid
        flash("Login successful!", "success")
        return redirect(url_for("dashboard"))  # Redirect to dashboard after successful login
    else:
        flash("Invalid credentials", "error")
        return redirect(url_for("index"))  # Redirect back to the index page if login fails


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to view your dashboard.")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Show only the user's created recipes (optional section)
    own_recipes = Recipes.query.filter_by(userid=user_id).all()

    # Show favorite recipes regardless of who created them
    favorite_recipes = (
        db.session.query(Recipes)
        .join(Favorites, Recipes.recipeid == Favorites.recipe_id)
        .filter(Favorites.user_id == user_id)
        .all()
    )

    favorite_ids = [recipe.recipeid for recipe in favorite_recipes]

    return render_template(
        "dashboard.html",
        recipes=own_recipes,
        favorite_recipes=favorite_recipes,
        favorite_ids=favorite_ids
    )



@app.route("/new_recipe", methods=["GET", "POST"])
def new_recipe():
    if "user_id" not in session:
        flash("Please log in to create a recipe.")
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            # Collect form inputs
            name = request.form["name"].strip()
            description = request.form["description"].strip()
            cookingtime = int(request.form["cookingtime"])
            instructions = request.form["instructions"].strip()
            selected_preference_ids = request.form.getlist("preferences")  # list of strings

            # Create new recipe object
            new_recipe = Recipes(
                name=name,
                description=description,
                cookingtime=cookingtime,
                instructions=instructions,
                userid=session["user_id"]
            )

            # Link dietary preferences (many-to-many)
            for pid in selected_preference_ids:
                preference = Preferences.query.get(int(pid))
                if preference:
                    new_recipe.preferences.append(preference)

            # Save to DB
            db.session.add(new_recipe)
            db.session.commit()
            flash("Recipe created successfully!")

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating recipe: {e}")

        return redirect(url_for("dashboard"))

    # GET request → load preference options for the form
    all_preferences = Preferences.query.order_by(Preferences.preferencename).all()
    return render_template("new_recipe.html", all_preferences=all_preferences)

@app.route("/delete_recipe/<int:recipeid>", methods=["POST"])
def delete_recipe(recipeid):
    recipe = Recipes.query.get_or_404(recipeid)
    if recipe.userid != session["user_id"]:
        flash("Unauthorized action.")
        return redirect(url_for("dashboard"))

    db.session.delete(recipe)
    db.session.commit()
    flash("Recipe deleted.")
    return redirect(url_for("dashboard"))

@app.route('/toggle_favorite/<int:id>', methods=['POST'])
def toggle_favorite(id):
    if 'user_id' not in session:
        flash("Please log in to favorite recipes.")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Check if this recipe is already favorited by the user
    favorite = Favorites.query.filter_by(user_id=user_id, recipe_id=id).first()

    if favorite:
        # Already favorited — remove it
        db.session.delete(favorite)
        flash("Removed from favorites.")
    else:
        # Not favorited yet — add it
        new_fav = Favorites(user_id=user_id, recipe_id=id)
        db.session.add(new_fav)
        flash("Added to favorites!")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error toggling favorite: {e}")

    return redirect(request.referrer or url_for('get_recipes'))

@app.route("/top_preferences")
def top_preferences():
    query = text("""
        SELECT p.preferencename, COUNT(*) AS total_favorites
        FROM user_favorites f
        JOIN recipe_preferences rp ON f.recipe_id = rp.recipeid
        JOIN preferences p ON rp.preferenceid = p.preferenceid
        GROUP BY p.preferencename
        ORDER BY total_favorites DESC
        LIMIT 3;
    """)
    results = db.session.execute(query).fetchall()
    return render_template("top_preferences.html", results=results)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
@app.route("/logout")
def logout():
    session.clear()  # This will remove all data from the session
    return redirect(url_for("login"))  # Redirect the user back to login page

if __name__ == "__main__":
    app.run(debug=True)
