CS50 MOVIES
My name is Maria Isabel Jaramillo and this is my final project of the CS50 course. 
I have developed a web application where you can register with a unique user and store 
the information of your favorite movies and discover recommendations based on what you like to watch.

The app contains
9 HTML files that will be listed below to explain how it works

apology.html: It generates an apology to the user depending on the error 
that has occurred, it gives information about what the problem was.

change_pass.html: This file shows the structure of the page to change a user's password

index.html: It is the main page, where a list of information is shown for each 
favorite movie. Here appears the cover, title, year, genre, type, director and rating 
of each user's movie


layout.html: Contains the template of each HTML to always display the same presentation bar at 
the beginning of the page, here there are 3 links, one to search for a movie, another to look 
at the recommendations and the one to log out.

login.html: Asks the user for their username and password to login

recommendations.html: Shows the movies recommended by the predictive model, 
with the information returned by the IMDb API. As in index, the same information 
is shown per recommended movie.

register.html: Allows the user to register with a username and password that will be stored 
in a sqlite3 database

search_movie.html: The user can enter a hint of the name of the movie, series or tv show 
that he wants to search and can press submit to get all the matches.

show_movies.html: Shows the results obtained for the title searched in search_movies.html. 
Again, the web application will communicate with the API to obtain all possible matches and 
display their information via HTML.

How is the data of each user stored?

In an sql database called finance.db there are two important tables, one of them contains 
the username of each registered user and the hash that hides the password of each user. 
This information is in the users table.

How are the movies of each user stored?
Again, in the same database there is a table called movies_info which contains data on 
the id with which the movie is identified within the IMDb database, its title, directors, 
year of release, genre, type, rating and the url of the cover.


How is the information of the movies obtained?
Every time you need to search for information about a movie, you go to the helpers.py script, 
where you can find the lookup function that allows me to connect to the IMDb API in RapidApi. 
In this way, the API takes the matches with the title or part of the title with which the 
request has been made and returns a list of dictionaries with all the matches. This information 
takes time to return.

To achieve the connection with the API it is necessary to configure the token before, 
so whoever serves the page must register and obtain the token and configure it by means of:

$ export API_KEY = value

How are recommendations generated?

To carry out this step, machine learning tools were included, so the scikit-learn python library 
was used and a script taken from the internet in the reference:

https://www.datacamp.com/community/tutorials/recommender-systems-python

Therefore, there is a folder called model that contains two .csv files, these are the training 
set used for the model. The files contain information about different movies and are used in the 
script to achieve a correlation between the movies that the user likes and potential new candidates.

Thus, each time a recommendation is needed, the 'recommender' function of the movie_suggest.py 
script is called, which extracts the necessary features from the language and returns a list of 
titles with the candidates.

Since only the title is not useful, the API is called again to obtain the rest of the information 
of each recommendation. For this, the first 3 recommendations were taken for each movie that the 
user likes and it is assumed that the first match that IMDb finds is the expected one.