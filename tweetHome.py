from flask import Flask, render_template, redirect, url_for, request, session
# from flask_socketio import SocketIO
import twitter as tw
import sqlite3 as sql
import requests
import base64
import json
consumer_key = ''
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# socketio = SocketIO(app)

client_id = '194c63a96c7f41e09907d7dd294a3e92'
client_secret = '90b0da21280549a69a78ffb61a42086b'

consumer_key='sXlA0jXvqwoSJR24eaOQB5dJm'
consumer_secret='9Ghq9lyO9zxKBnokLYzF6C8e32vHQi3Qy10HA6PdQTLPcZ7d6Z'
access_token = '1177881836-nrMwpla5LKEerjyAxzYidAaxZG3eaIAcPxI5crJ'
access_token_secret='q7NOhA84xPUrGAk1K8V5uxwu1DpSyi3eFpvm9EMolvcz7'
s = 'something'
@app.route('/')
def tweetInvasion():
    contents = getContent()
    audience = getAudiences() 
    return render_template('tweetInvasion.html', contents=contents, audience=audience)

@app.route('/beginInvasion')
def beginInvasion():
    return render_template('results.html')

@app.route('/commence')
def commence():

    return 'invasion complete'

@app.route('/results', methods = ['POST'])
def results():
    global s 

    con = sql.connect("TWIdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    req_data = request.get_data()
    req_data = json.loads(req_data)
    i = 0

    for content in req_data['content']:
        cur.execute('select messages from messages where cID=%s' % content['id'])
        content = cur.fetchall()
        messages = []
        for row in content:
            messages.append(row['messages'])
        req_data['content'][i]['messages'] = messages
        i += 1
    i = 0
    for audience in req_data['audience']:
        cur.execute('select artist from audience where name="%s"' % audience)
        content = cur.fetchall()
        artists = []
        for row in content:
            artists.append(row['artist'])
        req_data['audience'][i] = {}

        req_data['audience'][i]['name'] = audience
        req_data['audience'][i]['artist'] = artists
        i += 1
    print(req_data)
    con.close() 
    s = req_data
    return s

def getContent():
    con = sql.connect("TWIdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('select title, cID from content')
    content = cur.fetchall()
    if len(content) == 0:
        content = 'empty'
    con.close() 
    return content   

def getMessages(id):
    if id is None:
        id = 1
    with sql.connect("TWIdatabase.db") as con:
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("select * from messages as m join content as c on c.cID = m.cID where c.cID = %s"% id)
        rows = cur.fetchall()
        content = getContent()
        if len(rows) == 0:
            cur.execute('select title from content where cID = %s'% id)
            title = cur.fetchone()
            title = title['title']
        else:
            title = rows[0]
    final = {
        "rows" : rows,
        "content" : content,
        "id": id,
        "title" : title
    }
    con.close()
    return final

@app.route('/messages/<id>')
def messages(id=None):

    final = getMessages(id)

    return render_template('messages.html', rows=final["rows"], content=final["content"], id=final["id"], title=final["title"])
    con.close()

@app.route('/newMessage<id>', methods = ['POST'])
def newMessage(id=None):
    message = request.form
    message = message["message"]

    con = sql.connect("TWIdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("INSERT INTO messages (messages, cID) VALUES (?,?)",(message, id))
    con.commit()
    con.close()
    return redirect(url_for('messages', id=id))

@app.route('/newContent', methods = ['POST'])
def newContent():
    content = request.form
    link = content["link"]
    title = content["title"]

    con = sql.connect("TWIdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("INSERT INTO content (link, title) VALUES (?,?)",(link, title))
    con.commit()
    con.close()
    return redirect(url_for('messages', id=1))

def authorizeSpotify():
    response = requests.post('https://accounts.spotify.com/api/token',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={'grant_type':'client_credentials'},
        auth=(client_id, client_secret))
    session['accessToken'] = json.loads(response.content)['access_token']
    print('session refreshed : ' + session['accessToken'])

@app.route('/getAudienceDetails/<an>')
def getAudienceDetails(an=None):
    
    con = sql.connect("TWIdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    SQL = "select artist, followers, genres from audience where name='" + an + "'"
    cur.execute(SQL)
    row_headers=[x[0] for x in cur.description]
    row = cur.fetchall()
    con.close()
    json_data=[]
    for result in row:
        json_data.append(dict(zip(row_headers,result)))

    return json.dumps(json_data)

@app.route('/searchsimiliarbands/<name>')
def searchsimiliarbands(name=None):
    if 'accessToken' not in session:
        authorizeSpotify()
        
    if name is not None:
        url = 'https://api.spotify.com/v1/search?q=' + name + '&type=artist'
        response = requests.get(url, params={'access_token': session['accessToken']})
        if response.status_code == 401:
            authorizeSpotify()
            response = requests.get(url, params={'access_token': session['accessToken']})

        response = json.loads(response.content)['artists']['items'][0]
        genres = ''
        for x in response['genres']:
            genres += x + ','
        genres = genres[0:-2]
        rawData = '{"index":"0", "name":"' + response['name'] + '", "genres": "' + genres + '", "id": "' + response['id']  +'"}'
        bandInQuestion = json.loads(rawData)
        filteredArtists = []
        filteredArtists.append(bandInQuestion)


        artID = response['id']
        relatedUrl = 'https://api.spotify.com/v1/artists/' + artID + '/related-artists'
        relatedResponse = requests.get(relatedUrl, params={'access_token': session['accessToken']})
        relatedArtists = json.loads(relatedResponse.content)['artists']
        # listOfArtists2 = []
        # listOfArtists2.append((bandInQuestion['name'].replace(" ", '')))
        i = 1
        for artist in relatedArtists:
            relatedGenres = ''
            for x in artist['genres']:
                relatedGenres += x + ','

            fa = {
                "name" : artist['name'],
                "genres" : relatedGenres,
                "id" : artist['id'],
                'index' : i
            }
            i += 1
            filteredArtists.append(fa)
            # listOfArtists2.append(artist['name'].replace(" ", ""))

        # listOfArtists = ','.join(listOfArtists2)
        # print(listOfArtists)
        # api = tw.Api(consumer_key=consumer_key,
        #               consumer_secret=consumer_secret,
        #               access_token_key=access_token,
        #               access_token_secret=access_token_secret)
        # results = api.UsersLookup(screen_name=listOfArtists)
        # followers = []
        # for result in results:
        #     temp = {}
        #     temp['name'] = result.name
        #     temp['screen_name'] = result.screen_name
        #     temp['id'] = result.id
        #     temp['verified'] = result.verified
        #     temp['followers'] = result.followers_count
        #     followers.append(temp)
        # followersIndex = 0
        # j = 0
        # everything = followers
        # everything.append(listOfArtists2)
    else:
        return 'watchmewhipwatchmenene'
    return json.dumps(filteredArtists)

def getAudiences():
    con = sql.connect("TWIdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT sum(followers) as fl, name from audience group by name")
    row = cur.fetchall()
    con.close()  
    if len(row) == 0:
        row = 'empty'
    
    
    return row

@app.route('/audiences')
def audiences():

    row = getAudiences() 
    return render_template('audiences.html', audience=row)

@app.route('/addNewAudience', methods = ['POST'])
def addNewAudience():
    req_data = request.get_data()
    req_data = json.loads(req_data)
    # print(req_data['artists'][0])

    con = sql.connect("TWIdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    sql2 = "INSERT INTO audience (name, artist, followers, genres) VALUES"
    values = []
    for artist in req_data['artists']:
        values.append('("' + req_data['audienceName'] + '", "' + artist['name'] + '", 0, "' + artist['genres'] + '")')
    
    values = (',').join(values)
    sql2 += values
    cur.execute(sql2)
    con.commit()
    con.close()

    return 'success'
