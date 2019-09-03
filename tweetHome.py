from flask import Flask, render_template, redirect, url_for
import tweepy as tw
import sqlite3 as sql
import json
consumer_key = ''
app = Flask(__name__)

@app.route('/')
def tweetInvasion():
    # results = api.GetSearch(raw_query="q=twitter%20&result_type=recent&since=2014-07-19&count=100")
    # consumer_key='sXlA0jXvqwoSJR24eaOQB5dJm'
    # consumer_secret='9Ghq9lyO9zxKBnokLYzF6C8e32vHQi3Qy10HA6PdQTLPcZ7d6Z'
    # access_token = 'nrMwpla5LKEerjyAxzYidAaxZG3eaIAcPxI5crJ'
    # access_token_secret='q7NOhA84xPUrGAk1K8V5uxwu1DpSyi3eFpvm9EMolvcz7'

    # auth = tw.OAuthHandler(consumer_key, consumer_secret)

    # api = tw.API(auth)
    # search_words = "#wildfires"
    # date_since = "2018-11-16"
    
    # tweets = tw.Cursor(api.search,
    #           q=search_words,
    #           lang="en",
    #           since=date_since).items(5)

    return render_template('tweetInvasion.html')

@app.route('/messages/<id>')
def messages(id=None):
    if id is None:
        id = 1
    with sql.connect("TWIdatabase.db") as con:
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("select * from messages as m join content as c on c.cID = m.cID where c.cID = %s"% id)
        rows = cur.fetchall()
        cur.execute('select title, cID from content')
        content = cur.fetchall()
        cur.execute('select title from content where cID=%s'%id)
        title = cur.fetchone()
    return render_template('messages.html', rows=rows, content=content, id=id, title=title)
    con.close()

@app.route('/audiences')
def audiences():
    return render_template('audiences.html')