import os
import requests
import urllib.parse
import imdb
from flask import redirect, render_template, request, session
from functools import wraps
from bs4 import BeautifulSoup
import urllib.request
import re

moviesDB = imdb.IMDb()


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = "https://imdb8.p.rapidapi.com/title/find"

        querystring = {"q": symbol}

        headers = {
            'x-rapidapi-host': "imdb8.p.rapidapi.com",
            'x-rapidapi-key': api_key
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        data = response.json()
    except:
        return None

    data = data["results"]
    movies_data = {}

    for movie in data:

        try:

            # ID
            movie_id = movie["id"]

            # Titulo
            if 'title' in movie:
                title = movie["title"]
            else:
                title = "Not found"

            # Year
            if 'year' in movie:
                year = movie["year"]
            else:
                year = "Not found"

            # Type
            if "titleType" in movie:
                kind = movie["titleType"]
            else:
                kind = "Not found"

            # Usar libreria para obtener datos faltantes
            cod = re.findall("\d+", movie_id)
            cod = cod[0]
            movie_d = moviesDB.get_movie(cod)

            # Generos
            if 'genres' in movie_d:
                genres = movie_d['genres']
                genres = ' / '.join(genres)
            else:
                genres = "Not found"

            # Rating
            if 'rating' in movie_d:
                rating = movie_d['rating']
            else:
                rating = "Not found"

            # Casting
            if 'principals' in movie:
                principals = movie['principals']
                actors = []
                for actor in principals:
                    actors = actors + [actor["name"]]

                casting = ', '.join(actors)
            else:
                casting = "Not found"

            # Director
            if 'directors' in movie_d:
                directores = movie_d["directors"]
                directores = str(directores[0])
                directors = directores
            else:
                directors = "Not found"

            # Cover
            if 'image' in movie:
                cover = movie['image']['url']
            else:
                cover = 'https://w7.pngwing.com/pngs/940/807/png-transparent-graphic-film-reel-movie-film-silver-and-black-film-strip-and-reel-illustration-angle-photography-monochrome-thumbnail.png'

            if (title and year and kind) != "Not found":
                movies_data[movie_id] = {'id': movie_id, 'title': title, 'year': year, 'kind': kind,
                                         'genres': genres, 'rating': rating, 'casting': casting, 'directors': directors, 'cover': cover}
        except:
            pass

    if movies_data == {}:
        return None
    else:
        return movies_data


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
