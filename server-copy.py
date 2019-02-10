from flask import Flask, render_template, request, Response, make_response
from flask import redirect, url_for 
from flask import jsonify
import requests
import os
import re
import html
import SentimentAnalyzer
import sqlite3
import datetime
from functools import wraps

app = Flask(__name__)

now = datetime.datetime.now()

####SQL CONNETION####
connection = sqlite3.connect('data/twitter.db')

c = connection.cursor()

#c.execute('''DROP TABLE IF EXISTS tweets''')
#c.execute('''DROP TABLE IF EXISTS users''')
# Create table
c.execute('''CREATE TABLE IF NOT EXISTS tweets 
			 (id INTEGER PRIMARY KEY AUTOINCREMENT, tweet text NOT NULL, date_posted default CURRENT_DATE, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS users
			 (id INTEGER PRIMARY KEY AUTOINCREMENT, username text NOT NULL, password VARCHAR(12) NOT NULL, fname text, lname text, birthday date)''')

# Insert a row of data
#c.execute("INSERT INTO tweets VALUES (9223372036854775807, 'i like burgers', CURRENT_DATE, 1, 'polygloter')")
# c.execute("INSERT INTO tweets VALUES(?, ?, ?,?);", ("tweet", now, 2, 'polygloter'))

c.execute("SELECT * FROM tweets")
	 
rows = c.fetchall()

print(rows)


connection.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
connection.close()

####SQL CONNETION####

@app.route("/register")
def registerTwitter():
	return render_template('register.html')

@app.route("/register", methods=['POST'])
def registerUser():
	username = request.form.get('username')
	password = request.form.get('pword')

	status = ""
	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()

	userFound = True

	c.execute("SELECT username FROM users WHERE username=?",(username,))
	username_in_db = c.fetchall()
	#print(username_in_db)

	if len(username_in_db) != 0:
		if username_in_db[0][0] != username:
			userFound = False
			c.execute("INSERT INTO users(username, password) VALUES(?,?);", (username, password))
			status = "Succesfully created your account!"
		else:
			userFound = True
			status = "'" + username + "' already exists"
	else:
		userFound = False
		c.execute("INSERT INTO users(username, password) VALUES(?,?);", (username, password))
		status = "Succesfully created your account!"

	connection.commit()
	connection.close()

	return render_template('register.html', status_CreateUser=status)

@app.route("/login")
def loginTwitter():
	return render_template('login.html')

@app.route("/login-user", methods=['POST'])
def loginUser():
	username = request.form.get('username')
	password = request.form.get('pword')
	#print(username)

	status = ""
	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()

	userFound = False

	print('login GET')
	# query = "SELECT * FROM users WHERE username='{}'".format(username)
	# print(query)

	c.execute("SELECT username FROM users WHERE username='{}'".format(username))
	# query = "SELECT username FROM users WHERE username='{}'".format(username)
	# print(query)

	fetch = c.fetchone()
	print(type(fetch))
	if type(fetch) is tuple:
		#print("Object exists")
		username_in_db = fetch[0]
		if username_in_db == username:
			userFound = True
			c.execute("SELECT password FROM users WHERE username=?",(username,))
			password_in_db = c.fetchone()[0]
			print(password_in_db)
			if password == password_in_db:
				status = "Succesfully logged in"
				resp = make_response(redirect('/dashboard'))
				resp.set_cookie('userID', username)
			else:
				status = "Wrong password"
	else:
		#print("Object doesn't exist")
		status = "'" + username + "' doesn't exist"

	connection.commit()
	connection.close()

	return resp

@app.route('/dashboard')
def dashboard():
	username = request.cookies.get('userID')
	#print("cookies", request.cookies)
		
	connection = sqlite3.connect('data/twitter.db')
	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()

	userFound = False
	status = ""

	user_tweets_list = []

	c.execute("SELECT tweet FROM tweets, users WHERE users.id = user_id and username=?",(username,))
	user_tweets = c.fetchall()
	print(user_tweets)

	for user_tweet in user_tweets:
		user_tweets_list.append(user_tweet[0])

	connection.commit()
	connection.close()
	return render_template('dashboard.html', userTweets=user_tweets_list,username=username)

@app.route("/logout")
def logoutTwitter():
	print("attempting to delete cookie")
	resp = make_response(redirect('/login'))
	resp.set_cookie('userID', '', expires=0)
	# print(resp.set_cookie('userID', '', expires=0))
	# print("type")
	# print(type(resp.set_cookie('userID', '', expires=0)))
	# print("delete cookie")
	resp.set_cookie('userID', '', expires=0)
	 
	return resp

#######################
@app.route("/twitter_clone")
def twitterClone():
	return render_template('tweets_in_db.html')

@app.route("/tweet-posted", methods=['POST'])
def tweetPosted():

	tweet = request.form.get('tweetPost')
	username = request.form.get('username')
	connection = sqlite3.connect('data/twitter.db')

	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()

	userFound = False
	status = ""

	user_tweets_list = []

	print("tweet-posted" + str(userFound))

	c.execute("SELECT username FROM users WHERE username=?",(username,))
	username_in_db = c.fetchone()[0]
	print(username_in_db)

	c.execute("SELECT id FROM users WHERE username=?",(username,))
	userID_in_db = c.fetchone()[0]
	#print(userID_in_db[0][0])

	if username_in_db!= "" and len(c.fetchAll()) != 0:
		userFound = True
		c.execute("INSERT INTO tweets(user_id, tweet) VALUES(?,?);", (userID_in_db, tweet))
	else:
		userFound = False
		status = "'" + username + "' doesn't exist"

	c.execute("SELECT tweet FROM tweets, users WHERE users.id = user_id and username=?",(username,))
	user_tweets = c.fetchone()[0]
	print(user_tweets)

	for user_tweet in user_tweets:
		user_tweets_list.append(user_tweet)

	connection.commit()
	connection.close()

	return render_template('tweets_in_db.html', status_PostTweet=status, userTweets=user_tweets_list, username=username+"'s")

@app.route("/create-new-user", methods=['POST'])
def new_user():
	username = request.form.get('username')
	password = request.form.get('pword')
	# fname = request.form.get('fname')
	# lname = request.form.get('lname')
	# bday = request.form.get('bday')

	status = ""
	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()

	userFound = True

	c.execute("SELECT username FROM users WHERE username=?",(username,))
	username_in_db = c.fetchall()
	print(username_in_db)
	#print(username_in_db[0][0])
	if len(username_in_db) != 0:
		if username_in_db[0][0] != username:
			userFound = False
			c.execute("INSERT INTO users(username, password) VALUES(?,?);", (username, password))
			status = "Succesfully created your account!"
		else:
			userFound = True
			status = "'" + username + "' already exists"
	else:
		userFound = False
		c.execute("INSERT INTO users(username, password) VALUES(?,?);", (username, password))
		status = "Succesfully created your account!"

	connection.commit()
	connection.close()

	return render_template('tweets_in_db.html', status_CreateUser=status)


@app.route("/getusername")
def index():
	if not twitter.authorized:
		return redirect(url_for("twitter.login"))
	resp = twitter.get("account/settings.json")
	assert resp.ok
	return "You are @{screen_name} on Twitter".format(screen_name=resp.json()["screen_name"])


@app.route('/')
def homepage():
	return render_template('twitter_sa.html')

def get_tweets(searchitem):
	url = 'https://api.twitter.com/1.1/search/tweets.json?q=%23{}&result_type=recent'.format(searchitem)
	headers = {'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAC%2BR9QAAAAAAskoYJ290Ra9xcYfT6rp9e%2FJ7K2s%3DOgraEDCcAd6D6cCEmAtZSSql5B0uXlJ7oOCXsThCt5WxBr57yh'}
	res = requests.get(url, headers=headers)
	return res.json()

#print(get_tweets("hello"))


listOfPostedTweets = []

@app.route('/twittersentiment', methods=['GET', 'POST'])
def tweet_sentiment():	

	listOfTweets = []
	tweetSentimentPercentage = []
	tweet_sentiment_dict = {}
	listOfTweetsInfo = []
	tweets_dict = {}
	tweetCount = 0

	if request.method == 'GET':
		text = request.args.get('text')
		tweets_dict = get_tweets(text)
		#print(tweets_dict.keys()) #to check the keys names of tweets_dict 
		listOfTweets = []
		tweetSentimentPercentage = []
		tweet_sentiment_dict = {}
		listOfTweetsInfo = []

		#words_set = set()
		#word_freq_dict = {}

		for t in tweets_dict['statuses']:
			listOfTweets.append(t['text'])

		for tweet in listOfTweets:
			tweetToAnalyze = SentimentAnalyzer.SentimentToAnalyze(tweet)
			tweetSentiment = tweetToAnalyze.analyzeSentiment()
			#print(tweetToAnalyze.getInfo())
			tweetInfo = tweetToAnalyze.getInfo()
			#print(type(tweetInfo['positivePercentage']))
			listOfTweetsInfo.append(tweetInfo)
		
		#for word in words_set:
		#	word_freq_dict['word'] = 


		print("len of list: " )
		print(len(listOfTweets))

		return render_template('twitter_sa.html', text=text, tweets=listOfTweets, tweetsInfo=listOfTweetsInfo)
	tweetCount += 1
	if request.method == 'POST':
		tweetPost = request.form.get('tweetPost')

		print(tweetPost)
		print(type(tweetPost))
		lasttweetIDindex = len(listOfPostedTweets)
		
		tweets_dict["tweetCount"] = lasttweetIDindex
		tweets_dict["tweet"] = tweetPost
		listOfPostedTweets.append(tweets_dict)
	
		return render_template('twitter_sa.html', postedTweet=tweetPost, tweets_dict=listOfPostedTweets)
	tweetCount += 1


@app.route('/newtweets')
def new_tweets_homepage():
	new_tweets_txtfile = os.path.realpath("data/new-tweets.txt") #get address of sentiment analysis
	with open(new_tweets_txtfile, "r") as f:
		text_list = []
		for everyLine in f:
			text_list.append(everyLine)

	return render_template('new_tweets.html', tweets=text_list)

@app.route('/posttweets', methods=['POST'])
def post_tweets():
	newTweet = request.form.get('tweetPost')
	new_tweets_txtfile = os.path.realpath("data/new-tweets.txt") #get address of sentiment analysis
	with open(new_tweets_txtfile, "a+") as newTweetsf:
		newTweetsf.write(newTweet + "\n")
	
	with open(new_tweets_txtfile, "r") as f:
		text_list = []
		for everyLine in f:
			text_list.append(everyLine)

	return render_template('new_tweets.html', tweets=text_list)

@app.route('/gettext', methods=['POST'])
def my_form_post():
	text = request.form['text']
	processed_text = text.upper()
	return render_template('/')


#print(get_tweets("tweet"))
		
if __name__ == '__main__':
   app.run()

#token : {"token_type":"bearer","access_token":"AAAAAAAAAAAAAAAAAAAAAC%2BR9QAAAAAAskoYJ290Ra9xcYfT6rp9e%2FJ7K2s%3DOgraEDCcAd6D6cCEmAtZSSql5B0uXlJ7oOCXsThCt5WxBr57yh"}


#curl -u 'cW0YXg9qtZkpR7n35QEt6TE4l:uEmz0ElHJcqbkQ18cqlTzLRoW8CsH04xHYvcxHNWDQgeD5nuIM' \
#  --data 'grant_type=client_credentials' \
#  'https://api.twitter.com/oauth2/token'




# def check_auth(username, password):
# 	username_in_db = ""

# 	connection = sqlite3.connect('data/twitter.db')
# 	c = connection.cursor()
# 	c.execute("SELECT username FROM users WHERE username='{}'".format(username))
# 	fetch = c.fetchone()

# 	if type(fetch) is tuple:
# 		username_in_db = fetch[0]
# 		if username_in_db == username:
# 			userFound = True
# 			c.execute("SELECT password FROM users WHERE username=?",(username,))
# 			password_in_db = c.fetchone()[0]
# 	else:
# 		status = "'" + username + "' doesn't exist"
# 	connection.commit()
# 	connection.close()

# 	return username_in_db == username and password_in_db == password

# def authenticate():
# 	"""Sends a 401 response that enables basic auth"""
# 	return Response('Could not verify your access level for that URL.\n''You have to login with proper credentials', 401,{'WWW-Authenticate': 'Basic realm="Login Required"'})

# def requires_auth(f):
# 	@wraps(f)
# 	def decorated(*args, **kwargs):
# 		auth = request.authorization
# 		# print("input username " + auth.username)
# 		# print("input password " + auth.password)

# 		if not auth or not check_auth(auth.username, auth.password):
# 			return authenticate()
# 		return f(*args, **kwargs)
# 	return decorated
