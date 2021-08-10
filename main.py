from youtube_dl import YoutubeDL
from functools import partial
from flask import *
import json, hashlib, random, lyricsgenius, spotipy, asyncio
from spotipy.oauth2 import SpotifyClientCredentials  #To access authorised Spotify data

# os.system("pip install spotify_dl")

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id="fd9822fe9e144b6d8da4ca0da809d509",
    client_secret="2dcef7167f8a468ab22315ccd23c578f"))


app = Flask(__name__)
app.config['SECRET_KEY'] = ' ich liebe 4-$#" '
ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

genius = lyricsgenius.Genius("K2MVdGHG5avZZA5Ax7gtZxlGLKl1Y21Pnx8RGItkfER9zVwaSisYipJ_fKOMgrgd")

ytdl = YoutubeDL(ytdlopts)

async def create_source(search: str, download=False):
    loop = asyncio.get_event_loop()

    to_run = partial(ytdl.extract_info, url=search, download=download)
    d = await loop.run_in_executor(None, to_run)
    try:
        if 'entries' in d:
            d = d['entries'][0]
    except TypeError:
        return {
            # 'src': d['webpage_url'],
            'title': d['title'],
            "x":d['formats'][0]['url']
        }
    if download:
        source = ytdl.prepare_filename(d)
        return source

    return {
            'src': d['webpage_url'],
            'title': d['title'],
            "x":d['formats'][0]['url']
        }


with open("db/data.json") as fp:
    data = json.load(fp)
with open("db/songs.json") as fp:
    songs = json.load(fp)

def hasher(text) -> str: h = hashlib.md5(text.encode()); return h.hexdigest()


def auth(username, pw):
    global data
    try:
        if data[username]['pw'] == hasher(pw):
            return True
        return
    except KeyError:
        return


def saveJson():
    with open("db/data.json", "w+") as fp:
        json.dump(data, fp, indent=4)
    with open("db/songs.json", "w+") as fp:
        json.dump(songs, fp, indent=4)

@app.route('/logout')
def logout():
    global data
    cookie = make_response(redirect("/"))
    cookie.set_cookie('name', "")
    cookie.set_cookie('pw', "")
    flash("Logged out!", category="success")
    return cookie

@app.route('/login', methods=['POST'])
def login():
    global data
    try:
        name = request.form['name']
        pw = request.form['pw']
        if auth(name, pw):
            cookie = make_response(redirect("/"))
            cookie.set_cookie("name", name)
            cookie.set_cookie("pw", pw)
            
            return cookie
        flash("Username or password incorrect", category="error")
        return redirect("/")
    except:
        return redirect("/")



@app.route('/sign-up', methods=['POST', "GET"])
def sign_up():
    global data
    try:
        name = request.form['name']
        pw = request.form['pw']
        
        if name not in data.keys():
            data[name] = {
                "pw": str(hasher(pw)),
                "liked":{},
                "playlists":{},
                "history":{},
                "last":{}
            }
            saveJson()

            cookie = make_response(redirect('/'))
            cookie.set_cookie("name", name)
            cookie.set_cookie("pw", pw)
            return cookie

        flash("Username Taken", category="error")
        return redirect("/")
    except:
        return redirect("/")


@app.route("/searchq=<name>", methods=["GET"])
def search_link(name):
    try:
        songs = {}

        result = sp.search(name)
        song_uri = result["tracks"]["items"][0]["uri"]
        song_link = sp.track(song_uri)["external_urls"]["spotify"]

        i = 0

        for song in result["tracks"]["items"]:
            artists = []
            i += 1
            song_uri = song["uri"]
            song_link = sp.track(song_uri)["external_urls"]["spotify"]

            image = song["album"]["images"][0]["url"]

            for artist in song["artists"]:
                artists.append(artist["name"])

            song_name_modified = song['name'] + f' {{{",".join(artists)}}}'
            songs[song_name_modified] = {
                "img":image
            }

        return jsonify(songs)

    except IndexError:

        return jsonify('"song not found"')
    
@app.route('/')
def index():
    global data
    name = request.cookies.get("name")
    pw = request.cookies.get("pw")
    if name != "" and name != None and pw != "" and pw != None:
        if auth(name, pw):
            if data[name]['last'] != {}:
                return redirect(f"/song$$img={data[name]['last']['img']}$$name={data[name]['last']['songName']}")
            

            liked = data[name]['liked']
            history = data[name]['history']

            
            artists = []
            for i in liked:
                i = i.split("{")[1].replace("}", "")
                i = i.split(",")
                for j in i:
                    if j not in artists:
                        artists.append(j)

            req_songs = {}
            for ar in artists:

                result = sp.search(ar)  #search query
                song_uri = result["tracks"]["items"][0]["uri"]
                song_link = sp.track(song_uri)["external_urls"]["spotify"]

                i = 0

                for i in range(len(result["tracks"]["items"])):
                    if i == 4:
                        break
                    song = result["tracks"]["items"][i]
                    artists = []
                    i += 1
                    song_uri = song["uri"]

                    image = song["album"]["images"][0]["url"]

                    for artist in song["artists"]:
                        artists.append(artist["name"])
                    image = image.split('/')[-1]
                    song_name_modified = song['name'] + f' ({",".join(artists)})'
                    req_songs[song_name_modified] = f'/song$$img={image}$$name={song_name_modified}'


            return render_template(
                "index.html",
                r=random.randint(0,234234),
                name=name,
                src="",
                liked=liked,
                history=history,
                req_songs=req_songs
            )
        else:
            return render_template("auth.html", r=random.randint(0, 12132))
    else:
        return render_template("auth.html", r=random.randint(0, 12132)) 

@app.route('/song$$img=<img>$$name=<sname>')
def goto_song(img:str, sname:str):
    name = request.cookies.get("name")
    pw = request.cookies.get("pw")
    if auth(name, pw):
        try:
            src = asyncio.run(create_source(sname, download=False))
            data[name]['history'][sname] = {
                "src":src['x'],
                "img":img
            }
            data[name]['last'] = {
                "songName":sname,
                "src":src['x'],
                "img":img
            }
            saveJson()

            liked = data[name]['liked']
            history = data[name]['history']


            artists = []
            for i in liked:
                i = i.split("{")[1].replace("}", "")
                i = i.split(",")
                for j in i:
                    if j not in artists:
                        artists.append(j)

            req_songs = {}
            for ar in artists:

                result = sp.search(ar)  #search query
                song_uri = result["tracks"]["items"][0]["uri"]
                song_link = sp.track(song_uri)["external_urls"]["spotify"]

                i = 0

                for i in range(len(result["tracks"]["items"])):
                    if i == 4:
                        break
                    song = result["tracks"]["items"][i]
                    artists = []
                    i += 1
                    song_uri = song["uri"]

                    image = song["album"]["images"][0]["url"]

                    for artist in song["artists"]:
                        artists.append(artist["name"])
                    image = image.split('/')[-1]
                    song_name_modified = song['name'] + f' {{{",".join(artists)}}}'
                    req_songs[song_name_modified] = {
                        "img":image
                    }

            artists = []
            for i in liked:
                i = i.split("{")[1].replace("}", "")
                i = i.split(",")
                for j in i:
                    if j not in artists:
                        artists.append(j)

            req_songs2 = {}
            for ar in artists:

                result = sp.search(ar)  #search query
                song_uri = result["tracks"]["items"][0]["uri"]
                song_link = sp.track(song_uri)["external_urls"]["spotify"]

                i = 0

                for i in range(len(result["tracks"]["items"])):
                    if i == 4:
                        break
                    song = result["tracks"]["items"][i]
                    artists = []
                    i += 1
                    song_uri = song["uri"]

                    image = song["album"]["images"][0]["url"]

                    for artist in song["artists"]:
                        artists.append(artist["name"])
                    image = image.split('/')[-1]
                    song_name_modified = song['name'] + f' {{{",".join(artists)}}}'
                    req_songs2[song_name_modified] = {
                        "img":image
                    }

            
            return render_template(
                'index.html',
                r=random.randint(0, 234243),
                src=src['x'],
                img=img,
                songName=sname,
                name=name,
                pw=pw,
                isliked=sname in data[name]['liked'].keys(),
                liked=liked,
                history=history,
                req_songs=req_songs,
                req_songs2=req_songs2,
                songReal=sname.split("{")[0],
                artist=sname.split("{")[1].split(",")[0],
                playlists=data[name]['playlists']
            )
        except TypeError:
            return redirect("/")

    return redirect("/")




@app.route('/like$$songname=<sname>$$img=<img>', methods=['POST'])
def like_song(sname, img):
    name = request.cookies.get("name")
    pw = request.cookies.get("pw")
    if auth(name, pw):
        likes:dict = data[name]['liked']
        if sname in likes.keys():
            del likes[sname]
        else:
            src = asyncio.run(create_source(sname, download=False))
            likes[sname] = {
                "src":src['x'],
                "img":img
            }
        saveJson()
        return "True"
    return "False"

@app.route('/next-song')
def nex_song():
    name = request.cookies.get("name")
    pw = request.cookies.get("pw")
    if auth(name, pw):
        all_songs = {}
        temp = data[name]['liked']
        temp2 = data[name]['history']

        # for i in temp.keys():
        #     all_songs[i]['img'] = temp[i]['img']

        # for i in temp2.keys():
        #     all_songs[i]['img'] = temp2[i]['img']
        
        for i in temp.keys():
            all_songs[i] = temp[i]['img']

        for i in temp2.keys():
            all_songs[i] = temp2[i]['img']

        all_songs_list = []
        for i in all_songs:
            all_songs_list.append(i)

        x = random.choice(all_songs_list)

        nextSong = x
        return jsonify({"main":f"/song$$img={all_songs[nextSong]}$$name={nextSong}"})

    return "False"





    # data[name] = {
    #             "pw": str(hasher(pw)),
    #             "liked":{},
    #             "playlists":{},
    #             "history":{},
    #             "last":{}
    #         }



@app.route('/new-playlist', methods=['POST', 'GET'])
def new_playlist():
    name = request.cookies.get("name")
    pw = request.cookies.get("pw")
    if auth(name, pw):
        if request.method == "POST":
            playlistName = request.form['playlist-name']
            try:
                prv = request.form['prv']
                prv = True
            except:
                prv = False
            if playlistName in data[name]['playlists'].keys():
                flash("Playlist Name Already in use!", category="error")
                return redirect("/new-playlist")
            
            data[name]['playlists'][playlistName] = {
                "prv":prv,
                "songs":{}
            }
            saveJson()
            return redirect(f"/playlist/{name}/{playlistName}")
        return render_template('new_playlist.html', r=random.randint(0, 23434))
    return redirect("/")


@app.route('/get-ly$$artist=<artist>$$songname=<song>')
def get_ly(artist, song):
    artist = genius.search_artist(artist, max_songs=0, sort="title")
    song = genius.search_song(str(song), artist.name)
    return jsonify({"data":str(song.lyrics)})

    # playlists[name] = {
    #             "prv":True or False,
    #             "songs":{
    #                   "Lose {KSI,Lil Wayne}"{
    #                       "src": "url",
    #                       "img": "ab67616d0000b27388212f0818ebea83cdaae2ec"
    #             }
    #                   }
    #         }

@app.route('/add$$img=<img>$$name=<songName>$$playlist=<playlistName>')
def add_song(img, songName, playlistName):
    name = request.cookies.get("name")
    pw = request.cookies.get("pw")
    if auth(name, pw):
        if playlistName in data[name]['playlists'].keys():
            try:
                src = asyncio.run(create_source(songName, download=False))
                data[name]['history'][songName] = {
                    "src":src['x'],
                    "img":img
                }
                data[name]['last'] = {
                    "songName":songName,
                    "src":src['x'],
                    "img":img
                }
            
            
                data[name]['playlists'][playlistName]['songs'][songName] = {
                    "src":src['x'],
                    "img":img
                }
                
                saveJson()
                return redirect(f"/playlist/{name}/{playlistName}")

            except TypeError:
                    add_song(img, songName, playlistName)
    return "False"

@app.route('/playlist/<username>/<playlistName>')
def goto_playlist(username, playlistName):
    name = request.cookies.get("name")
    pw = request.cookies.get("pw")
    if auth(name, pw):
        if username in data.keys():
            if playlistName in data[username]['playlists'].keys():
                if data[username]['playlists'][playlistName]['prv'] == False or username == name:
                    all_songs = data[username]['playlists'][playlistName]['songs']
                    for song in all_songs:
                        all_songs[song]['src'] = asyncio.run(create_source(song, download=False))['x']
                    saveJson()
                    return render_template(
                        "index.html",
                        r=random.randint(0, 234234),
                        playlist_songs=all_songs,
                        playlistName=playlistName
                    )


            flash("Playlist not found or is Private!", category="error")
            return redirect("/")
        
        flash("User does not exist!", category="error")
        return redirect("/") 

    return redirect("/")



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)