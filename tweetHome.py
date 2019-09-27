from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO, emit
import twitter as tw
import sqlite3 as sql
from random import randint
from pprint import pprint
import requests
import base64
import json
import time
consumer_key = ''
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socketio = SocketIO(app)

client_id = '194c63a96c7f41e09907d7dd294a3e92'
client_secret = '90b0da21280549a69a78ffb61a42086b'

consumer_key='dJSfZB5YgplrNkNU5zcvRMclC'
consumer_secret='I8oXO61516cshtXIvCMXSLVGO38AZJuj1Xxm96lWPwj3qGtAcJ'
access_token = '1177881836-AXnnXtfc43GUR2DmlSmBUnXEwcxq3njXQ2TfZmQ'
access_token_secret='fr0BgeDzvsEOBQZp41vy7cgjP0BXTtI3q1sTqNlY1ZIp8'
s = ''

api = tw.Api(consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token_key=access_token,
                access_token_secret=access_token_secret,
                sleep_on_rate_limit=True)
# results = api.UsersLookup(screen_name=listOfArtists)

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
    global api

    con = sql.connect("TWIdatabase.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    s = session['userSelected']
    artistID = []
    for audience in s['audience']:

        # sql3 = 'update audience set twitterID ="", audienceContent="",screenName="" where name="%s"' % (audience['name'])
        # print(sql3)
        # cur.execute(sql3)
        # con.commit()

        for artist in audience['artist']:
            cur.execute('select name, artist, twitterID from audience where name = "%s" AND artist = "%s"'% (audience['name'], artist))
            content = cur.fetchone()

            if content['twitterID'] is None or content['twitterID'] is '':
                results = api.GetUsersSearch(term=content['artist'], count=2)

                if results[0].verified is True and artist.lower() in results[0].name.lower():
                    sql2 = 'update audience set screenName = "%s", twitterID = %d where name = "%s" and artist = "%s"' % (results[0].screen_name, results[0].id, audience['name'], artist)
                    cur.execute(sql2)
                    # print(sql2)
                    artistID.append(results[0].id)
                else:
                    sql2 = 'update audience set screenName = "%s", twitterID = %d where name = "%s" and artist = "%s"' % (results[0].screen_name, -1, audience['name'], artist)
                    cur.execute(sql2)
                    # print(sql2)
                con.commit()
                print('twitter Work')
            else:
                print('twitter no need to work')

    if len(artistID) != 0:
        for ids in artistID:
            cur.execute('select cursor, cursorIndex, screenName, audienceContent from audience where twitterID = %d' % ids)
            result = cur.fetchone()

            if result['audienceContent'] is '' or result['audienceContent'] is None:
                ids2 = str(ids)
                newFollowers = api.GetFollowersPaged(user_id=ids2, cursor=-1, screen_name=result['screenName'], count=200)
                filteredFollowers = []
                # print(newFollowers)
                for follower in newFollowers[2]:
                    temp = {}
                    temp['id'] = follower.id
                    temp['screen_name'] = follower.screen_name
                    filteredFollowers.append(temp)
                
                filteredFollowers = json.dumps(filteredFollowers)
                finalSql = "update audience set audienceContent = '%s', cursor='%s' where twitterID= %d"%(filteredFollowers, newFollowers[0], ids)
                # pprint(filteredFollowers)
                cur.execute(finalSql)
                con.commit()
                print('work')
            else:
                print('no need to work')
    else:
        print('no need to work2')

    audienceNames = []
    if len(artistID) == 0:
        for audience in s['audience']:
            audienceNames.append(audience['name'])

        temp = ''
        if len(audienceNames) == 1:
            temp = 'select twitterID from audience where name="' + audienceNames[0] + '"'
        else:
            temp = 'select twitterID from audience where name in (' + (', ').join(audienceNames) + ')'
        temp += 'AND twitterID != -1'
        cur.execute(temp)

        row = cur.fetchall()
        artistID = [str(artist['twitterID']) for artist in row]

    sqlFollowers = 'SELECT audienceContent, twitterID, screenName from audience WHERE twitterID IN (' + (', ').join(artistID) + ')'
    cur.execute(sqlFollowers)
    followers2 = cur.fetchall()
    followers = [json.loads(follower['audienceContent']) for follower in followers2]
    twitterIDs = [ids['twitterID'] for ids in followers2]
    sqlIndex = 'SELECT cursorIndex from audience WHERE twitterID IN (' + (', ').join(artistID) + ')'
    cur.execute(sqlIndex)
    indexList = cur.fetchall()
    indexList = [index['cursorIndex'] for index in indexList]
    # pprint(session['userSelected'])

    i = 1
    if i == 2:
        while(i>=0):
            
            rand = randint(0, len(artistID)-1)
            twitterRand = randint(0, len(twitterIDs)-1)
            currentIndex = indexList[rand]
            print(type(currentIndex))
            print(type(len(followers[rand])))
            currentIndex = int(currentIndex)
            
                
            print(currentIndex)
            
            content = session['userSelected']['content']
            randContent = randint(0, len(content)-1)
            randMessage = randint(0, len(content[randContent]['messages'])-1)

            chosenContent = content[randContent]
            chosenMessage = chosenContent['messages'][randMessage]

            cur.execute('select link from content where cID = %d'% chosenContent['id'])

            chosenLink = cur.fetchone()['link']
            
            post = ''
            post += chosenMessage + '\n' + chosenLink + '\n'

            followersPerPost = 0
            while(len(post) < 250):
                currentIndex = indexList[rand]
                currentIndex = int(currentIndex)

                if currentIndex == len(followers[rand]):
                    print('yes')
                    cur.execute('select cursor, screenName from audience where twitterID = %d' % twitterIDs[twitterRand])
                    row = cur.fetchone()
                    cursor = row['cursor']
                    screenName = row['screenName']
                    indexList[rand] = 0
                    currentIndex = 0
                    newFollowers = api.GetFollowersPaged(user_id=twitterIDs[rand], cursor=int(cursor), screen_name=screenName, count=200)
                    filteredFollowers = []
                    # print(newFollowers)
                    for follower in newFollowers[2]:
                        temp = {}
                        temp['id'] = follower.id
                        temp['screen_name'] = follower.screen_name
                        filteredFollowers.append(temp)
                    followers = filteredFollowers
                    filteredFollowers = json.dumps(filteredFollowers)
                    finalSql = "update audience set audienceContent = '%s', cursor='%s', cursorIndex=%d where twitterID= %d"%(filteredFollowers, newFollowers[0], 0, twitterIDs[rand])
                    cur.execute(finalSql)
                    con.commit()
                else:
                    print('someth')

                currentFollower = followers[rand][currentIndex]['screen_name']
                temp = post + ' @' + currentFollower + ' '
                if len(temp) > 250:
                    break; 
                post += ' @' + currentFollower + ' ' 
                followersPerPost += 1
                indexList[rand] += 1



            cur.execute('update audience set cursorIndex="%s" where twitterID=%d'% (indexList[rand], twitterIDs[rand]))
            con.commit()
            result = api.PostUpdates(status=post)
            socketio.emit('success', {'content': chosenContent['name'], 'message':chosenMessage, 'follower':followersPerPost})
            # print(chosenContent['name'] + ' : ' + chosenMessage + ' : ' + str(i))
            time.sleep(36)

    con.close() 
    return 'invasion complete'


@app.route('/tweettest')
def tweetTest():
    sample = "something \r\n\r\n\r\n\r\n\r\n\r\n nothing"
    print(sample)
    result = api.PostUpdates(status=sample)
    # # result = api.PostUpdates(status='tweet Successful!')
    # result = api.CheckRateLimit('https://api.twitter.com/1.1/direct_messages/events/new.json')
    # print(result)
    # return 'something'
    # result = api.PostDirectMessage('something', '1165838593807376384', return_json=True)
    # print(len('fdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfdfdsasdfd'))
    # pprint(result)

    return '<div>success</div>'

@app.route('/results', methods = ['POST'])
def results():

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
    pprint(req_data)
    con.close() 
    session['userSelected'] = req_data
    return 'success'

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
