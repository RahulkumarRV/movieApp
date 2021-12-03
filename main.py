import re
from flask import Flask, render_template, request, jsonify
from requests.sessions import Request
from werkzeug.utils import redirect
import pymongo
import requests
import json


app = Flask(__name__)


mongo = pymongo.MongoClient(
    'mongodb+srv://rahulkumarmongo:rahulkumarmongo@cluster0.0pvpt.mongodb.net/movie_db?retryWrites=true&w=majority', tls=True, tlsAllowInvalidCertificates=True)
db = pymongo.database.Database(mongo, 'movie_db')
authcollection = pymongo.collection.Collection(db, 'auth')
postscollection = pymongo.collection.Collection(db, 'posts')

data = authcollection.find()

username = ""
password = ""
searchtitle = ""
curentMovieData = {}
playlistsname = []
data

# print("data start")
# for i in data:
#     print(i)


@app.route('/', methods=['GET'])
def option():
    return render_template('option.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form.get("Email")
        username = request.form.get("Username")
        password = request.form.get("Password")
        data = authcollection.find()
        for i in data:
            if i["username"] == username:
                return render_template('signup.html', msg="username alredy exist")

        authcollection.insert_one(
            {"email": email, "username": username, "password": password, "playlistName": []})
        return redirect('/login')
    else:
        return render_template('signup.html', msg="")


@app.route('/login', methods=['GET', 'POST'])
def login():
    global playlistsname
    if request.method == 'POST':
        global username
        username = request.form.get("Username")
        global password
        password = request.form.get("Password")
        data = authcollection.find()
        for i in data:
            if i["username"] == username and i["password"] == password:
                playlistsname = i["playlistName"]
                return redirect('/home')
        return render_template('login.html', msg="Invalid username or password")
    else:
        return render_template('login.html', msg="")


@app.route('/home', methods=['GET', 'POST'])
def home():
    global searchtitle
    global curentMovieData
    global data
    if request.method == 'GET':
        moviedata = requests.get(
            "http://www.omdbapi.com/?i=tt3896198&apikey=acf38bf4")
        data = json.loads(moviedata.content)
        searchtitle = data["Title"]
        return render_template('home.html', data=data)
    else:
        searchtitle = request.form.get("Search")
        moviedata = requests.get(
            "http://www.omdbapi.com/?i=tt3896198&apikey=acf38bf4&t=" + searchtitle)
        data = json.loads(moviedata.content)
        # postscollection.insert_one({"Title": data["Title"],
        #                             "Description": data["Plot"],
        #                             "Released": data["Released"],
        #                             "Director": data["Director"],
        #                             "Actors": data["Actors"],
        #                             "Writer": data["Writer"],
        #                             "Language": data["Language"],
        #                             "Country": data["Country"],
        #                             "Visibility": "private",
        #                             "username": username,
        #                             })
        curentMovieData = {"Title": data["Title"],
                           "Poster": data["Poster"],
                           "Description": data["Plot"],
                           "Released": data["Released"],
                           "Director": data["Director"],
                           "Actors": data["Actors"],
                           "Writer": data["Writer"],
                           "Language": data["Language"],
                           "Country": data["Country"],
                           "Visibility": "private",
                           "username": username,
                           "playlistName": ""
                           }

        print(curentMovieData)
        return render_template("home.html", data=data)


@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    global curentMovieData
    global username
    global playlistsname
    mode = ["Public", "Private"]
    if request.method == 'POST':
        print(curentMovieData)
        curentMovieData["Visibility"] = str(request.form.get("select"))
        curentMovieData["playlistName"] = request.form.get("Playlistname")
        print(playlistsname)
        if not (curentMovieData["playlistName"] in playlistsname):
            authcollection.update_one({"username": username}, {
                "$push": {"playlistName": curentMovieData["playlistName"]}})

        if curentMovieData["Visibility"] == "Public":
            authcollection.update_many({}, {
                "$push": {"playlistName": curentMovieData["playlistName"]}})

        postscollection.insert_one(curentMovieData)
        return render_template("/playlist.html", msg="Movie added to playlist successfully", mode=mode)
    else:
        return render_template("playlist.html", msg="", mode=mode)


@app.route('/showplaylists', methods=['GET', 'POST'])
def showplaylist():
    global playlistsname
    return render_template("home2.html", data=data, playlist=playlistsname)


@app.route('/playlistmovies', methods=['GET', 'POST'])
def playlistmovies():
    global playlistsname
    if request.method == 'POST':
        playlist = str(request.form.get("select"))
        movielist = []
        data = postscollection.find()
        for i in data:
            if i["username"] == username and i["playlistName"] == playlist:
                movielist.append(i)
            if i["playlistName"] == playlist and i["Visibility"]:
                movielist.append(i)
        return render_template("playlistmovies.html", playlistmovies=movielist)
    else:
        return render_template("playlistmovies.html")


if __name__ == "__main__":
    app.run(debug=True)
