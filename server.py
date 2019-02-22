from flask import Flask, render_template, request, Response, make_response
from flask import redirect, url_for 
from flask import jsonify
import requests
import os
import re
import html
import sqlite3
import datetime

app = Flask(__name__)

now = datetime.datetime.now()

####SQL CONNETION####
connection = sqlite3.connect('data/twitter.db')
c = connection.cursor()
# c.execute('''DROP TABLE IF EXISTS tweets''')
# c.execute('''DROP TABLE IF EXISTS users''')

c.execute('''CREATE TABLE IF NOT EXISTS tweets 
			 (id INTEGER PRIMARY KEY AUTOINCREMENT, tweet VARCHAR(120) NOT NULL, date_posted default CURRENT_DATE, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))''')
c.execute('''CREATE TABLE IF NOT EXISTS users
			 (id INTEGER PRIMARY KEY AUTOINCREMENT, username text NOT NULL, password VARCHAR(12) NOT NULL, fname text, lname text, birthday date)''')
connection.commit()
connection.close()
####SQL CONNETION####

@app.route('/')
def homepage():
	return redirect('/login')

@app.route("/register")
def registerPage():
	return render_template('register.html')


@app.route("/register", methods=['POST'])
def registerTwitter():
	username = request.form.get('username')
	password = request.form.get('pword')

	status = ""
	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()

	userFound = True

	c.execute("SELECT username FROM users WHERE username=?",(username,))
	
	if c.fetchone() is not None:
		c.execute("SELECT username FROM users WHERE username=?",(username,))
		username_in_db = c.fetchone()[0]
		print(username_in_db)
		if username_in_db != username:
			userFound = False
			c.execute("INSERT INTO users(username, password) VALUES(?,?);", (username, password))
			connection.commit()
			connection.close()
			status = "Succesfully created your account!"
			print("New User: ")
			print(username)
			resp = make_response(redirect('/dashboard'))
			resp.set_cookie('sessionID', username)
			# loggedInAs = request.cookies.get('sessionID')
			return resp
		else:
			userFound = True
			status = "'" + username + "' already exists"
			return render_template('register.html', status_CreateUser=status)
	else:
		userFound = False
		c.execute("INSERT INTO users(username, password) VALUES(?,?);", (username, password))
		connection.commit()
		connection.close()
		status = "Succesfully created your account!"
		print("New User: ")
		print(username)
		resp = make_response(redirect('/dashboard'))
		resp.set_cookie('sessionID', username)
		return resp
		# return redirect('/dashboard')



@app.route("/login")
def loginTwitter():
	return render_template('login.html')

@app.route("/login-user", methods=['POST'])
def loginUser():
	username = request.form.get('username')
	password = request.form.get('pword')

	status = ""
	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()

	userFound = False

	print('login GET')
	c.execute("SELECT username FROM users WHERE username='{}'".format(username))

	# fetch = c.fetchone()
	# print(type(fetch))
	if c.fetchone() is not None:
		#print("Object exists")
		c.execute("SELECT username FROM users WHERE username='{}'".format(username))
		username_in_db = c.fetchone()[0]
		resp = ''
		if username_in_db == username:
			userFound = True
			c.execute("SELECT password FROM users WHERE username=?",(username,))
			password_in_db = c.fetchone()[0]
			connection.commit()
			connection.close()
			if password == password_in_db:
				status = "Succesfully logged in"
				resp = make_response(redirect('/dashboard'))
				resp.set_cookie('sessionID', username)
				return resp
			else:
				status = "Wrong password"
				resp = make_response(render_template('login.html', status_LogIn=status))
				return resp
	else:
		status = "'" + username + "' doesn't exist"
		resp = make_response(render_template('login.html', status_LogIn=status))
		return resp


@app.route('/dashboard')
def dashboard():
	username = request.cookies.get('sessionID')

	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()
	userFound = False
	status = ""

	user_tweets_list = []

	c.execute("SELECT tweet FROM tweets, users WHERE users.id = user_id and username=?",(username,))
	user_tweets = c.fetchall()

	for user_tweet in user_tweets:
		user_tweets_list.append(user_tweet[0])
		print(user_tweet[0])

	connection.commit()
	connection.close()
	return render_template('dashboard.html', userTweets=user_tweets_list,username=username)

@app.route("/logout")
def logoutTwitter():
	print("attempting to delete cookie")
	resp = make_response(redirect('/login'))
	resp.set_cookie('userID', '', expires=0)

	return resp

#######################
@app.route("/twitter_clone")
def twitterClone():
	return render_template('tweets_in_db.html')

@app.route("/tweet-posted", methods=['POST'])
def tweetPosted():
	username = request.cookies.get('sessionID')
	tweet = request.form.get('tweetPost')

	connection = sqlite3.connect('data/twitter.db')
	c = connection.cursor()

	c.execute("SELECT id FROM users WHERE username=?",(username,))
	userID_in_db = c.fetchone()[0]

	c.execute("INSERT INTO tweets(user_id, tweet) VALUES(?,?);", (userID_in_db, tweet))
	connection.commit()
	connection.close()

	return redirect('/dashboard')

@app.route("/create-new-user", methods=['POST'])
def new_user():
	username = request.form.get('username')
	password = request.form.get('pword')
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
		
if __name__ == '__main__':
   app.run()
