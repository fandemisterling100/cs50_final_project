import os
import imdb
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd
import movie_suggest
import pandas as pd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Archivos para el modelo
df1=pd.read_csv('./model/tmdb_5000_credits.csv')
df2=pd.read_csv('./model/tmdb_5000_movies.csv')

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Mostrar peliculas favoritas del usuario"""
    current_user = session["user_id"]
    
    # pasar a la pagina principal y tomar los datos de la db para mostarlos siguiendo el mismo codigo del html de show movies
    movies_info = db.execute("SELECT * FROM movies_info WHERE user_id = ?", current_user)

    for movie in movies_info:

        if movie['url_image'] == None:
            movie['url_image'] = 'https://img.icons8.com/cotton/2x/movie-beginning.png'

    return render_template("index.html", movies_info = movies_info)


# Cambiar todo lo de buy! esta sera la pagina de busqueda
@app.route("/search_movie", methods=["GET", "POST"])
@login_required
def search_movie():
    """Agregar una pelicula a favoritos"""

    if request.method == "GET":
        return render_template("search_movie.html")
    else:
        user_input = request.form.get("user_in")

        if not user_input:
            return apology("Please enter a valid name for a movie or Tv serie")

        movies_info = lookup(user_input)

        if movies_info == None:
            return apology("We couldn't find any match")

        else:
            #print(type(movies_info))
            #print(movies_info)

            return render_template("show_movies.html", movies_info = movies_info, cont = 0)

@app.route("/show_movies", methods=["GET", "POST"])
@login_required
def show_movies():
    """Agregar una pelicula de las mostradas"""
    if request.method == "GET":
        return render_template("show_movies.html")
    else:
        but_value = request.form.get('submit_button')
        but_value = but_value.replace("'", "")
        data = but_value.split(',')

        movie_id = data[1]
        movie_title = data[2]
        movie_year = data[3]
        movie_kind = data[4]
        movie_genre = data[5]
        movie_rating = data[6]
        movie_director = data[7]
        movie_cover = data[8]

        # Traer los datos de peliculas del usuario actual
        user_movies = db.execute("SELECT movie_id FROM movies_info WHERE user_id = ?", session["user_id"])
        user_movies = [movie['movie_id'] for movie in user_movies]

        # La pelicula que intenta agregar ya esta en sus favs? Si no lo está agregarla sino, no hacer nada, solo el redirect
        if movie_id not in user_movies:
            db.execute("INSERT INTO movies_info (user_id, movie_id, title, year, kind, genres, rating, casting, directors, url_image) VALUES (:user_id, \
                :movie_id, :title, :year, :kind, :genres, :rating, :casting, :directors, :url_image)", user_id = session["user_id"], movie_id = movie_id, title = movie_title, year= movie_year, kind= movie_kind, \
                    genres= movie_genre, rating= movie_rating, casting= "", directors= movie_director, url_image = movie_cover)

        return redirect("/")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/recommendations", methods=["GET", "POST"])
@login_required
def recommendations():
    """Show recommended movies"""
    if request.method == "GET":

        current_user = session["user_id"]

        # Traigo los datos de titulos de peliculas que le gustan al usuario
        user_movies = db.execute("SELECT title FROM movies_info WHERE user_id = ?", current_user)
        user_movies = [movie['title'] for movie in user_movies]

        if user_movies == []:
            return apology("First add a movie to your list!")
        else:
            recommended = []

            for movie in user_movies:
                
                # Obtengo recomendaciones basadas en el titulo, me quedo con las primeras 3
                sugerencias = movie_suggest.recommender(movie.lstrip(), df1, df2)
                sugerencias = list(sugerencias)
                sugerencias = sugerencias[:3]

                for sugerencia in sugerencias:
                    # Busco la informacion de la sugerencia. Solo la primer ocurrencia
                    movie_info = lookup(sugerencia)

                    if movie_info == None:
                        pass
                    else:
                        first = list(movie_info)[0]
                        # Agrego a la lista el diccionario con los datos de la pelicula actual
                        recommended += [movie_info[first]]

            return render_template("recommendations.html", movies_info = recommended)
    else:

        but_value = request.form.get('submit_button')
        but_value = but_value.replace("'", "")
        data = but_value.split(',')

        movie_id = data[1]
        movie_title = data[2]
        movie_year = data[3]
        movie_kind = data[4]
        movie_genre = data[5]
        movie_rating = data[6]
        movie_director = data[7]
        movie_cover = data[8]

        # Traer los datos de peliculas del usuario actual
        user_movies = db.execute("SELECT movie_id FROM movies_info WHERE user_id = ?", session["user_id"])
        user_movies = [movie['movie_id'] for movie in user_movies]

        # La pelicula que intenta agregar ya esta en sus favs? Si no lo está agregarla sino, no hacer nada, solo el redirect
        if movie_id not in user_movies:
            db.execute("INSERT INTO movies_info (user_id, movie_id, title, year, kind, genres, rating, casting, directors, url_image) VALUES (:user_id, \
                :movie_id, :title, :year, :kind, :genres, :rating, :casting, :directors, :url_image)", user_id = session["user_id"], movie_id = movie_id, title = movie_title, year= movie_year, kind= movie_kind, \
                    genres= movie_genre, rating= movie_rating, casting= "", directors= movie_director, url_image = movie_cover)

        return redirect("/")


@app.route("/change_pass", methods=["GET", "POST"])
@login_required
def change_pass():
    """Change password."""
    if request.method == "GET":
        return render_template("change_pass.html")

    else:
        current_user = session["user_id"]
        rows = db.execute("SELECT * FROM users WHERE id = :username",
                          username=current_user)
        valid_current_pass = check_password_hash(rows[0]["hash"], request.form.get("password"))
        
        new_pass = request.form.get("new_pass")
        confirmation = request.form.get("confirm_pass")

        if not valid_current_pass:
            return apology("Your current password is not correct")

        if not new_pass:
            return apology("Please enter a new password")

        if not confirmation:
            return apology("Please enter a confirmation")

        if new_pass != confirmation:
            return apology("New pass and confirmation must match")
         
        new_pass = generate_password_hash(new_pass)

        db.execute("UPDATE users SET hash=? WHERE id = ?", new_pass, current_user)

        return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":

        return render_template("register.html")
    else:

        user = request.form.get("username")
        password = request.form.get("password")
        pass_confirm = request.form.get("confirmation")

        if not user:
            return apology("You must type an user")

        if not password:
            return apology("You must introduce a password")
        
        if not pass_confirm:
            return apology("You must confirm your password")

        if password != pass_confirm:
            return apology("Password and confirmation must be the same")

        exist = db.execute("SELECT * FROM users WHERE username = ?", user)

        if len(exist) == 1:
            return apology("This username already exists, try again")
        
        hash_pass = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash_p)", username = user, hash_p = hash_pass)
        return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
