from flask import Flask, jsonify, render_template, Response, make_response, request, json
from pymongo import MongoClient
import gridfs
import pymongo
from bson.objectid import ObjectId
import datetime
import time
import re
import dns.resolver
import socket
import smtplib, ssl
from email.mime.text import MIMEText
from http import cookies
import pika
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import SimpleStatement
import requests
import uuid
import os

app = Flask(__name__)

name = ""
date = datetime.datetime.today()
dateStr = date.strftime("%Y-%m-%d")


@app.route("/deposit", methods=['POST'])
def deposit():
	filename = request.form['filename']
	contents = request.form['contents']

	cluster = Cluster(contact_points = ['192.168.122.10'])
	session = cluster.connect('hw5')
	strCQL = "INSERT INTO imgs (filename,contents) VALUES (?,?)"
	pStatement = session.prepare(strCQL)
	session.execute(pStatement,[fileName,contents])

	return json.dumps({'status':'OK'})

@app.route("/speak", methods=['GET', 'POST'])
def speak():
	#request_json = request.get_json()
	#key = request_json['key']
	#msg = request_json['msg']

	#connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.122.8'))
	#channel = connection.channel()

	#channel.exchange_declare(exchange='hw3')

	#channel.basic_publish(exchange='hw3', routing_key=key, body=msg)
	#connection.close()
	credentials = pika.PlainCredentials('cloudUser', 'password')
	parameters = pika.ConnectionParameters(host='192.168.122.8',credentials=credentials)
	connection = pika.BlockingConnection(parameters)
	channel = connection.channel()

	channel.queue_declare(queue='hello')

	channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
	print(" [x] Sent 'Hello World!'")
	connection.close()



	return json.dumps({'status':'OK'})

response = None
@app.route("/listen", methods=['GET', 'POST'])
def listen():
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.exchange_declare(exchange='hw3')

	result = channel.queue_declare()
	queue_name = result.method.queue

	request_json = request.get_json()
	keys = request_json['keys']

	for key in keys:
		channel.queue_bind(exchange='hw3',queue=queue_name,routing_key=key)

	while True:	
		msg = channel.basic_get(queue=queue_name,no_ack=True)
		if msg[2] != None:
			toReturn = json.dumps({'msg':msg[2].decode()})
			print(toReturn)
			return toReturn

def callback(ch, method, properties, body):
	print(body)
	
	return json.dumps({'msg':str(body)})
@app.route("/")
def hello():
    #print("HEREEEEE")
    return render_template('searchUser.html')
    #try:
    #    name = request.form['name']
    #    return render_template('ttt.html', name=name, date=dateStr)
    #except:
    #    return render_template('ttt.html', name="")

@app.route("/renderSearchU")
def renderSearchU():
	return render_template('searchUser.html')

@app.route("/renderAddQ")
def renderAddQ():
	currentCookie = request.cookies.get('_id')
	if isLoggedIn(currentCookie) == False:
		render_template('addQuestion.html', loggedIn='false')
	return render_template('addQuestion.html', loggedIn='true')

@app.route("/renderAddA")
def renderAddA():
	return render_template('addAnswer.html')

@app.route("/renderSearchQ")
def renderSearchQ():
	return render_template('searchQuestion.html')

@app.route("/renderSearchA")
def renderSearchA():
	return render_template('searchAnswer.html')


@app.route("/signUp")
def renderSignUp():
	return render_template('signUp.html')

@app.route("/verifyEmail")
def renderVerify():
	return render_template('verify.html')

@app.route("/userLogin")
def renderLogin():
	return render_template('login.html')

@app.route("/loggedOut")
def renderLoggedOut():
	return render_template('loggedOut.html')

@app.route("/listGamesView", methods=['POST', 'GET'])
def renderListGames():
	listGames = request.args.get('games')
	return render_template('listGames.html', gamesList=listGames)

@app.route("/gameScoreView", methods=["GET"])
def renderGameScore():
	score = request.args.get('response')
	humanIndex = score.find("human")
	nextComma = score.find(",", humanIndex)
	human = ""
	if nextComma != -1:
		human = score[humanIndex+8:nextComma]
	else:
		human = score[humanIndex+8:]
	
	compIndex = score.find("wopr")
	nextComma = score.find(",", compIndex)
	comp = ""
	if nextComma != -1:
		comp = score[compIndex+7:nextComma]
	else:
		comp = score[compIndex+7:]

	tieIndex = score.find("tie")
	nextComma = score.find(",", tieIndex)
	tie = ""
	if nextComma != -1:
		tie = score[tieIndex+6:nextComma]
	else:
		tie = score[tieIndex+6:]

	

	print(human)
	return render_template('viewGameScores.html', comp=comp, tie=tie, human=human)

@app.route("/adduser", methods=['POST'])
def addUser():
	request_json = request.get_json()
	username = request_json['username']
	password = request_json['password']
	email = request_json['email']
	
	client = MongoClient('mongodb://192.168.122.15:27017/', 27017)
	tttDB = client['usersDB']
	users = tttDB['users']
	query = {'email':email}
	result = users.find_one(query)
	if result != None:
		return json.dumps({'status':'error', 'error':'User with email already exists'}), 401
	result   = users.find_one({'username':username})
	if result != None:
		return json.dumps({'status':'error', 'error':'Username already taken'}), 403
	#games = []

	credentials = pika.PlainCredentials('cloudUser', 'password')
	parameters = pika.ConnectionParameters(host='192.168.122.15',credentials=credentials)
	connection = pika.BlockingConnection(parameters)
	channel = connection.channel()

	channel.queue_declare(queue='hello')
#
	qID = ObjectId()
	content = json.dumps({"_id":str(qID), "reputation": 1, "username": username, "password": password, "email": email, "verified": "false"})
	channel.basic_publish(exchange='', routing_key='hello', body=content)

	#result = users.insert_one({"reputation": 1, "games":games, "currentGame": "null", "username": username, "password": password, "email": email, "verified": "false"})
	#result = users.insert_one({"username": "test", "password": "hello", "email": "e", "verified": "false"})

	#client.close()

	#if result.acknowledged == True:
	#	key = str(result.inserted_id)
	#
	#	url = "http://192.168.122.15:5000"
	#	response = requests.post(url, json={"email":email, "key":key})
	
	#	msg = MIMEText("Please visit http://130.245.170.251/verifyEmail and enter the following key to verify your email\n validation key: <" + str(result.inserted_id) + ">")
	#	msg['From'] = "ubuntu@userdb.cloud.compas.cs.stonybrook.edu"
	#	msg['To'] = email
	#	msg['Subject'] = "Email Verification for SBStackOverflow"
	#	msg.attach()
	#	smtp = smtplib.SMTP("userdb.cloud.compas.cs.stonybrook.edu", 25)
	#	smtp.sendmail("ubuntu@userdb.cloud.compas.cs.stonybrook.edu", email, msg.as_string() )
	#	smtp.close()
	return json.dumps({'status': 'OK'})
	 
	#return json.dumps({'status': 'error', 'error':'Failed to add user'}), 400

	#if result.acknowledged == True:
	#	port = 587  # For starttls
	#	smtp_server = "smtp.gmail.com"
	#	sender_email = "cse356cloudproject@gmail.com"
	#	receiver_email = email
	#	password = "cse356cloud"
	#	msg = MIMEText("Please visit http://130.245.170.251/verifyEmail and enter the following key to verify your email\n validation key: <" + str(result.inserted_id) + ">")
	#	msg['Subject'] = "Email Verification for TTT"
	#	context = ssl.create_default_context()
	#	s = smtplib.SMTP(smtp_server, port)
	#	s.starttls(context=context)
	#	s.login(sender_email, password)
	#	s.sendmail(sender_email, receiver_email, msg.as_string())
	#	return json.dumps({'status': 'OK'})
	#return json.dumps({'status': 'error', 'error':'Failed to add user'}), 400


@app.route("/verify", methods=['POST'])
def verifyUser():
	request_json = request.get_json()
	email = request_json['email']
	key = request_json['key']
        
	client = MongoClient('mongodb://192.168.122.15:27017/', 27017)
	tttDB = client['usersDB']
	users = tttDB['users']
	
	#print(key)
	if key == 'abracadabra':
		query = {'email':email}
		result = users.find(query)
		found = False
		for x in result:
			found = True
		#if not found:
		#	#time.sleep(10)
		#	result = users.find(query)
		#for x in result:
		#	found = True
		#	print('success')
		if found:
			users.update_one({'email':email},{'$set':{'verified':'true'}})
			return json.dumps({'status':'OK'})
	try:
		query = {'_id':ObjectId(key), 'email':email}
		result = users.find(query)
		found = False
		for x in result:
			found = True
		#if not found:
		#	result = users.find(query)
		#for x in result:
		#	found = True
		#	print('success')
		if found:
			users.update_one({'_id':ObjectId(key)}, {'$set':{'verified':'true'}})
			return json.dumps({'status':'OK'})
		return json.dumps({'status':'error', 'error':'Invalid email or validation key'}), 403
	except:
		return json.dumps({'status':'error', 'error':'Invalid email or validation key'}), 403

@app.route("/login", methods=['POST'])
def login():
	request_json = request.get_json()
	username = request_json['username']
	password = request_json['password']

	client = MongoClient('mongodb://192.168.122.15:27017/')
	tttDB = client['usersDB']
	users = tttDB['users']
	
	query = {'username':username, 'password':password}
	result = users.find(query)
	found = False
	ID = ""
	for x in result:
		verified = x['verified']
		if verified == 'true':
			found = True
			ID = x['_id']
	if found:
		print("user " + str(ID) + " logged in")
		response = jsonify(status='OK', cookie=str(ID))
		response.set_cookie('_id', str(ID))
		response.set_cookie('username', username)
		return response
	
	return json.dumps({'status':'error', 'error':'User not verified, or invalid username/password'}), 401

@app.route("/logout", methods=['POST', 'GET'])
def logout():
	currentCookie = request.cookies.get('_id')
	response = jsonify(status='OK', cookie=str(currentCookie))
	response.set_cookie('_id', '')
	print("user " + str(currentCookie) + "logged out") 
	return response

@app.route("/user/<username>", methods=["GET"])
def getUserInfo(username):
	print("Getting user info for user: ", username)
	user = getUserByName(username)

	if user == None:
		return json.dumps({'status':'error', 'error':'No user with given username exists'}), 400
	
	userInfo = {'email':user['email'], 'reputation':user['reputation']}
	print("returning the following info: ", userInfo)
	return json.dumps({'status':'OK', 'user':userInfo})

@app.route("/user/<username>/questions", methods=["GET"])
def getUsersQuestions(username):
	user = getUserByName(username)

	if user == None:
		return json.dumps({'status':'error', 'error':'No user with given username exists'}), 400	

	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	questionsCollection = questionsDB['questions']

	query = {'userID':str(user['_id'])}
	questions = questionsCollection.find(query)

	questionIDs = []
	for question in questions:
		questionIDs += [str(question['_id'])]
	return json.dumps({'status':'OK', 'questions':questionIDs})

@app.route("/user/<username>/answers", methods=["GET"])
def getUsersAnswers(username):
	user = getUserByName(username)

	if user == None:
		return json.dumps({'status':'error', 'error':'No user with given username exists'}), 400
	
	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	answersCollection = questionsDB['answers']

	query = {'user':username}
	answers = answersCollection.find(query)

	answersIDs = []
	for answer in answers:
		answersIDs += [str(answer['_id'])]
	return json.dumps({'status':'OK', 'answers':answersIDs})


def getUserByName(username):
	client = MongoClient('mongodb://192.168.122.15:27017/')
	userDB = client['usersDB']
	users = userDB['users']

	user = users.find_one({'username':username})
	return user

def getUser(Id):
	client = MongoClient('mongodb://192.168.122.15:27017/')
	tttDB = client['usersDB']
	users = tttDB['users']

	user = users.find_one({'_id': ObjectId(Id)})
	if user == None:
		return None
	return {'username':user['username'], 'reputation':user['reputation']}

@app.route("/questions/<questionId>", methods=['GET', 'DELETE'])
def getQuestion(questionId):
	
	if request.method == "GET":
		client = MongoClient('mongodb://192.168.122.8:27017/')
		questionsDB = client['questionsDB']
		questionsCollection = questionsDB['questions']
		viewersCollection = questionsDB['questionViewers']

		print("viewing question:")
		print(questionId)
		try:
			oID = ObjectId(questionId)
		except:
			return json.dumps({'status':'error', 'error':'Invalid question id'}), 400
			
		query = {'_id': ObjectId(questionId)}
		question = questionsCollection.find_one(query)

		if question == None:
			return json.dumps({'status':'error', 'error':'Invalid question id'}), 400

		currentCookie = request.cookies.get('_id')
		newViewCount = question['view_count']
		identifier = currentCookie
		if isLoggedIn(currentCookie) == False:	
			# get IP
			identifier = request.remote_addr
		
		viewers = question['viewers']
		if not identifier in viewers:
			print('here')
			#query = {'IP':IP, 'questionID':questionId}
			#result = viewersCollection.find_one(query)
			#if result == None:
			
			credentials = pika.PlainCredentials('cloudUser', 'password')
			parameters = pika.ConnectionParameters(host='192.168.122.8',credentials=credentials)
			connection = pika.BlockingConnection(parameters)
			channel = connection.channel()

			channel.queue_declare(queue='hello')
#
			newViewCount = newViewCount + 1
			content = json.dumps({'_id':questionId,'identifier':identifier, 'newViewCount':newViewCount})
			channel.basic_publish(exchange='', routing_key='hello', body=content)
#	print(" [x] Sent 'Hello World!'")
#	after = time.time()
#	print(after - before)
			connection.close()
			
			#newViewCount = newViewCount + 1
			#questionsCollection.update_one({'_id':ObjectId(questionId)},{'$set':{'view_count':newViewCount}})
			#viewersCollection.insert_one({'IP':IP, 'questionID':questionId})
		#else:
		#	query = {'userID':currentCookie, 'questionID':questionId}
		#	result = viewersCollection.find_one(query)
		#	if result == None:
		#		newViewCount = newViewCount + 1
		#		questionsCollection.update_one({'_id':ObjectId(questionId)},{'$set':{'view_count':newViewCount}})
		#		viewersCollection.insert_one({'userID':currentCookie, 'questionID':questionId})
	
		user = getUser(question['userID'])

		print("user who posted question:", user)

		questionJson = {'id':questionId, 'user':user, 'body':question['body'], 'title':question['title'], 'score':question['score'], 'view_count':newViewCount, 'answer_count':question['answer_count'], 'timestamp':question['timestamp'], 'media':question['media'], 'tags':question['tags'], 'accepted_answer_id':question['accepted_answer_id']} 
		print("returning the following question: ", questionJson)
		return json.dumps({'status':'OK', 'question':questionJson})
	else:
		print("deleting question ", questionId)
		currentCookie = request.cookies.get('_id')
		if isLoggedIn(currentCookie) == False:
			return Response(status=405)
		else:
			client = MongoClient('mongodb://192.168.122.8:27017/')
			questionsDB = client['questionsDB']
			questionsCollection = questionsDB['questions']
			viewersCollection = questionsDB['questionViewers']
			answersCollection = questionsDB['answers']
			try:
				oId = ObjectId(questionId)
			except:
				return json.dumps({'status':'error', 'error':'Invalid question id'}), 400

			query = {'_id': ObjectId(questionId)}
			question = questionsCollection.find_one(query)
			
			if question == None:
				return Response(status=400)
			
			qPosterID = question['userID']
			mediaToDelete = question['media']
			if qPosterID != currentCookie:
				return Response(status=401)
						
			questionsCollection.delete_one(query)
		
			query = {'questionID':questionId}
			answers = answersCollection.find(query)

			for answer in answers:
				mediaToDelete += answer['media']
			answersCollection.delete_many(query)
		
			db = MongoClient('mongodb://192.168.122.8:27017/').gridfs_example
			fs = gridfs.GridFS(db)
			for itemId in mediaToDelete:
				fs.delete(ObjectId(itemId))

			#url = 'http://130.245.171.38/delete'

			#response = requests.post(url, json={"mediaToDelete":mediaToDelete})

			return Response(status=200)

@app.route("/answers/<answerId>/accept", methods=['POST'])
def acceptAnswer(answerId):
	currentCookie = request.cookies.get('_id')
	if isLoggedIn(currentCookie) == False:
		return make_response(json.dumps({'status':'error', 'error':'Must be logged in to accept an answer'}), 401)

	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	answersCollection = questionsDB['answers']
	questionsCollection = questionsDB['questions']
	try:
		oid = ObjectId(answerId)
	except:
		return make_response(json.dumps({'status':'error', 'error':'Invalid answer ID'}), 400)

	query = {'_id':ObjectId(answerId)}
	answer = answersCollection.find_one(query)

	if answer == None:
		return make_response(json.dumps({'status':'error', 'error':'Invalid answer ID'}), 400)

	questionID = answer['questionID']
	query = {'_id':ObjectId(questionID)}
	question = questionsCollection.find_one(query)
	userID = question['userID']
		

	if userID != currentCookie:
		return make_response(json.dumps({'status':'error', 'error':'Must question poster to accept an answer'}), 401)

	if question['accepted_answer_id'] != None:
		return make_response(json.dumps({'status':'error', 'error':'There already exists an accepted answer for this question'}), 400)
	
	questionsCollection.update_one({'_id':question['_id']}, {"$set": {'accepted_answer_id':answerId}})
	answersCollection.update_one({'_id':ObjectId(answerId)}, {"$set": {"is_accepted":True}})	

	return json.dumps({'status':'OK'})

@app.route("/answers/<answerId>/upvote", methods=['POST'])
def upvoteAnswers(answerId):
	request_json = request.get_json()
	upvote = request_json['upvote']

	currentCookie = request.cookies.get('_id')
	if isLoggedIn(currentCookie) == False:
		return make_response(json.dumps({'status':'error', 'error':'Must be logged in to upvote'}), 401)

	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	upvotesCollection = questionsDB['answerUpvotes']
	answersCollection = questionsDB['answers']

	client = MongoClient('mongodb://192.168.122.15:27017/')
	tttDB = client['usersDB']
	users = tttDB['users']

	changeValue = -1
	if upvote:
		changeValue = 1

	query = {"userID":currentCookie, "answerID":answerId}
	results = upvotesCollection.find_one(query)

	query =  {"_id":ObjectId(answerId)}
	answer = answersCollection.find_one(query)

	if answer == None:
		return make_response(json.dumps({'status':'error', 'error':'Invalid answer ID'}), 400)

	username = answer['user']

	user = getUserByName(username)
	userID = str(user['_id'])
	rep = user['reputation']
	if results == None:
		print("no upvotes for this user/question combo")
		if upvote:
			users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": changeValue}})
			upvotesCollection.insert_one({"userID":currentCookie, "answerID":answerId, "upvote":upvote, "changed":True})
		else:
			if rep > 1:
				users.update_one({'_id':ObjectId(userID), 'reputation':{"$ne":1}}, { "$inc": {"reputation": changeValue}})
				upvotesCollection.insert_one({"userID":currentCookie, "answerID":answerId, "upvote":upvote, "changed":True})
			else:	
				upvotesCollection.insert_one({"userID":currentCookie, "answerID":answerId, "upvote":upvote, "changed":False})
	else:
		previousVote = results['upvote']
		changed = results['changed']
		if previousVote and upvote:
			print("prevVote = true, vote = true")
			changeValue = -1
			users.update_one({'_id':ObjectId(userID), 'reputation':{"$ne":1}}, { "$inc": {"reputation": changeValue}})
			upvotesCollection.delete_one({"userID":currentCookie, "answerID":answerId})
		elif not previousVote and not upvote:
			print("prevVote = false, vote = false")
			changeValue = 1
			if changed:
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": changeValue}})
			upvotesCollection.delete_one({"userID":currentCookie, "answerID":answerId})
		elif previousVote and not upvote:
			print("prevVote = true, vote = false")
			changeValue = -2
			upvotesCollection.update_one({"userID":currentCookie, "answerID":answerId},{'$set':{'upvote':upvote}})
			if user['reputation'] >= 3:
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": changeValue}})
			if user['reputation'] == 2:
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": -1}})
		else:
			print("prevVote = false, vote = true")
			changeValue = 2
			if changed:
				upvotesCollection.update_one({"userID":currentCookie, "answerID":answerId},{'$set':{'upvote':upvote}})
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": changeValue}})
			else:
				upvotesCollection.update_one({"userID":currentCookie, "answerID":answerId},{'$set':{'upvote':upvote}})
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": 1}})
				
	answersCollection.update_one({'_id':ObjectId(answerId)},{ "$inc": {"score": changeValue}})

	return json.dumps({'status':'OK'})
	
@app.route("/questions/<questionId>/upvote", methods=['POST'])
def upvoteQuestions(questionId):
	request_json = request.get_json()
	upvote = request_json['upvote']

	print("question ID: ", questionId)
	print("upvote :", upvote)
	currentCookie = request.cookies.get('_id')
	if isLoggedIn(currentCookie) == False:
		return make_response(json.dumps({'status':'error', 'error':'Must be logged in to upvote'}), 401)

	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	upvotesCollection = questionsDB['upvotes']
	questionsCollection = questionsDB['questions']

	client = MongoClient('mongodb://192.168.122.15:27017/')
	tttDB = client['usersDB']
	users = tttDB['users']	

	changeValue = -1
	if upvote:
		changeValue = 1


	query = {"userID":currentCookie, "questionID":questionId}
	results = upvotesCollection.find_one(query)

	query =  {"_id":ObjectId(questionId)}
	question = questionsCollection.find_one(query)
	if question == None:
		return make_response(json.dumps({'status':'error', 'error':'Invalid question ID'}), 400)
	userID = question['userID']

	query = {"_id":ObjectId(userID)}
	user = users.find_one(query)
	rep = user['reputation']
	if results == None:
		print("no upvotes for this user/question combo")
	# results == none, there are no upvotes or downvotes, so just add one or subtract one as needed
		if upvote:
			print("1 upvote ", userID)
			users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": changeValue}})
			upvotesCollection.insert_one({"userID":currentCookie, "questionID":questionId, "upvote":upvote, "changed":True})
		else:
			print("-1 upvote ", userID)
			print(changeValue)
			if rep > 1:	
				users.update_one({'_id':ObjectId(userID), 'reputation':{"$ne":1}}, { "$inc": {"reputation": changeValue}})
				upvotesCollection.insert_one({"userID":currentCookie, "questionID":questionId, "upvote":upvote, "changed":True})
			else:
				upvotesCollection.insert_one({"userID":currentCookie, "questionID":questionId, "upvote":upvote, "changed":False})
				
	else:
		previousVote = results['upvote']
		changed = results['changed']
		print("upvote: userID ", userID)
		if previousVote and upvote:
			print("prevVote = true, vote = true, -1")
			changeValue = -1
			users.update_one({'_id':ObjectId(userID), 'reputation':{"$ne":1}}, { "$inc": {"reputation": changeValue}})
			upvotesCollection.delete_one({"userID":currentCookie, "questionID":questionId})
		elif not previousVote and not upvote:
			print("prevVote = false, vote = false, 1")
			changeValue = 1
			if changed:
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": changeValue}})
			upvotesCollection.delete_one({"userID":currentCookie, "questionID":questionId})
		elif previousVote and not upvote:
			print("prevVote = true, vote = false, -2")
			changeValue = -2
			upvotesCollection.update_one({"userID":currentCookie, "questionID":questionId},{'$set':{'upvote':upvote}}) 
			if user['reputation'] >= 3:
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": changeValue}})
			if user['reputation'] == 2:
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": -1}})
		else:
			print("prevVote = false, vote = true, 2")
			changeValue = 2
			if changed:
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": changeValue}})
				upvotesCollection.update_one({"userID":currentCookie, "questionID":questionId},{'$set':{'upvote':upvote}}) 
			else:
				users.update_one({'_id':ObjectId(userID)}, { "$inc": {"reputation": 1}})
				upvotesCollection.update_one({"userID":currentCookie, "questionID":questionId},{'$set':{'upvote':upvote}}) 
	questionsCollection.update_one({'_id':ObjectId(questionId)},{ "$inc": {"score": changeValue}})

	return json.dumps({'status':'OK'}) 

@app.route("/questions/<questionId>/answers", methods=['GET'])
def getAnswers(questionId):
	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	answersCollection = questionsDB['answers']

	query = {'questionID':questionId}
	results = answersCollection.find(query)
	answersArray = []
	if results == None:
		print("Invalid question id, or question has no answers for questionID", questionId)
		return json.dumps({'status':'error', 'error':'Invalid question id, or question has no answers'}), 400
	else:
		for answer in results:
			currentAnswer = {'user':answer['user'], 'body':answer['body'], 'score':answer['score'], 'is_accepted':answer['is_accepted'], 'timestamp':int(answer['timestamp']), 'id':str(answer['_id']), 'media':answer['media']}
			answersArray.append(currentAnswer)
		print("returning answers array:")
		print(answersArray)
		
		return json.dumps({'status':'OK', 'answers':answersArray})

@app.route("/search", methods=['POST'])
def search():
	request_json = request.get_json()
	timestamp = int(time.time())
	limit = 25
	accepted = False
	searchPhrase = ""
	sort_by = "score"
	tags = None
	hasMedia = False
	try:
		timestamp = request_json['timestamp']
		print("Setting timestamp to %d", timestamp)
	except KeyError:
		print("Setting timestamp to default = current time")
	try:
		limit = request_json['limit']
		if limit > 100:
			return json.dumps({'status':'error', 'error':'Cannot have limit higher than 100'}), 401
		print("Setting limit to %d", limit)
	except KeyError:
		print("Setting limit to default = 25")
	try:
		accepted = request_json['accepted']
		print("Setting accepted to $s", accepted)
	except KeyError:
		print("Setting accepted to default = false")
	
	try:
		sort_by = request_json['sort_by']
	except KeyError:
		print("Setting sort_by to default")

	try:
		tags = request_json['tags']
	except KeyError:
		print("Setting tags to default")
	try:
		hasMedia = request_json['has_media']
	except KeyError:
		print("Setting hasMedia to default")

	objectIDArray = []
	try:
		searchPhrase = request_json['q']
		if searchPhrase != "":
			searchPhrase = searchPhrase.lower()
			print("searchPhrase found")
			searchWords = searchPhrase.split(" ")
			print("Setting search phrase to: ", searchPhrase)
			searchClient = MongoClient('mongodb://192.168.122.12:27017/')
			searchDB = searchClient['questionsIndex']
			searchCollection = searchDB['questionsIndex']
		
			qContainsWord = []
			start = True
			results = searchCollection.find({"words":{"$in":searchWords}})
			for item in results:
				qContainsWord += item['ids']
			#for word in searchWords:
			#	query = {'word':word}
			#	qsWithWord = searchCollection.find_one(query)
			#	if qsWithWord == None:
			#		print("word not found: ", word)
			#		continue
			#	qIDs = qsWithWord['ids']
			#	if start:
			#		qContainsWord = qIDs
			#		print(qContainsWord)
			#		start = False
			#	else:
			#		#print("contains ", word)
			#		for qID in qIDs:
			#			if not (qID in qContainsWord):
			#				qContainsWord.append(qID)
						
					#for qID in qContainsWord:
					#	if not (qID in qIDs):
					#		print(qContainsWord)
					#		qContainsWord.remove(qID)
					#		print(qContainsWord)
			for ID in qContainsWord:
				objectIDArray.append(ObjectId(ID))
			#print("IDS:", objectIDArray)
	except KeyError:
		print("Setting search phrase to nothing")
	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	questionsCollection = questionsDB['questions']
	print("matching qs", objectIDArray)
	query = {'timestamp':{'$lte': timestamp}}
	if len(objectIDArray) > 0:
		query['_id'] = {'$in':objectIDArray}
	if accepted:
		query['accepted_answer_id'] = {'$ne':None}
	if hasMedia:
		query['media'] = {'$ne':[]}
	if tags != None:
		query['tags'] = {'$all':tags}
	print(query)
	results = None
	if sort_by == "timestamp":
		results = questionsCollection.find(query).sort("timestamp", pymongo.DESCENDING)
	else:
		results = questionsCollection.find(query).sort("score", pymongo.DESCENDING)
	questionsArray = []
	count = 0
	for question in results:
		if count >= limit:
			break
		if searchPhrase in question['title'].lower() or searchPhrase in question['body'].lower():
			user = getUser(question['userID'])
			questionJson = {'id':str(question['_id']), 'title':question['title'], 'user':user, 'body':question['body'], 'score':question['score'], 'view_count':question['view_count'], 'answer_count':question['answer_count'], 'timestamp':question['timestamp'], 'media':question['media'], 'tags':question['tags'], 'accepted_answer_id':question['accepted_answer_id']}
			questionsArray.append(questionJson)
			count = count + 1
	#print("count ", count)
	searchWords = searchPhrase.split(" ")
	if (count < limit):
		print("looking for not exact matches")
		matchesDictionary = {}	
		print("finding matches")
		results = questionsCollection.find(query).sort("timestamp", pymongo.DESCENDING)
		for question in results:
			numMatches = 0
			for word in searchWords:
				if word in question['title'].lower() or word in question['body'].lower():
					numMatches = numMatches + 1
			matchesDictionary[str(question['_id'])] = numMatches
		print(matchesDictionary)
		lookingFor = len(searchWords)
		while (count < limit and lookingFor > 0):
			print("looking for matches with ", lookingFor, " words matching the phrase")
			results = questionsCollection.find(query).sort("timestamp", pymongo.DESCENDING)
			for question in results:
				if count >= limit:
					break
				if searchPhrase in question['title'].lower() or searchPhrase in question['body'].lower():
					break
				if matchesDictionary[str(question['_id'])] == lookingFor:
					user = getUser(question['userID'])
					questionJson = {'id':str(question['_id']), 'title':question['title'], 'user':user, 'body':question['body'], 'score':question['score'], 'view_count':question['view_count'], 'answer_count':question['answer_count'], 'timestamp':question['timestamp'], 'media':question['media'], 'tags':question['tags'], 'accepted_answer_id':question['accepted_answer_id']}
					questionsArray.append(questionJson)
					count = count + 1
			lookingFor = lookingFor - 1
	print("Returning the following:")
	print(questionsArray)
	client.close()
	return json.dumps({'status':'OK', 'questions':questionsArray})


def findMatches(results, searchWords):
	matchesDictionary = {}
	print("finding matches")
	for question in results:
		#print("here")
		numMatches = 0
		for word in searchWords:
			#print(word)
			if word in question['title'].lower() or word in question['body'].lower():
				numMatches = numMatches + 1
		matchesDictionary[str(question['_id'])] = numMatches
	return matchesDictionary

@app.route("/questions/<questionId>/answers/add", methods=['POST'])
def addAnswer(questionId):
	currentCookie = request.cookies.get('_id')
	if isLoggedIn(currentCookie) == False:
		return json.dumps({'status':'error', 'error':'User is not logged in'}), 401

	request_json = request.get_json()
	try:
		body = request_json['body']
	except KeyError:
		return json.dumps({'status':'error', 'error':'Missing answer body'}), 400
	try:	
		media = request_json['media']
	except KeyError:
		media = []
	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	questionsCollection = questionsDB['questions']
	answersCollection = questionsDB['answers']

	try:
		oid =  ObjectId(questionId)
	except:
		return json.dumps({'status':'error', 'error':'Invalid quetion id'}), 400

	query = {'_id': ObjectId(questionId)}
	question = questionsCollection.find_one(query)

	if question == None:
		client.close()
		return json.dumps({'status':'error', 'error':'Invalid quetion id'}), 400

	if media != []:
		db = MongoClient('mongodb://192.168.122.8:27017/').gridfs_example
		fs = gridfs.GridFS(db)
		for mediaId in media:
			doc = fs.get(ObjectId(mediaId))
			poster = doc.poster
			if poster != currentCookie:
				return json.dumps({'status':'error', 'error':'media does not belong to user'}), 401
		
		print("probably not supposed to be here")
		client = MongoClient('mongodb://192.168.122.8:27017/')
		questionsDB = client['questionsDB']
		questionsCollection = questionsDB['questions']
		answersCollection = questionsDB['answers']
		
		client2 = MongoClient('mongodb://192.168.122.15:27017/')
		questionsDB2 = client2['questionsDB']
		questionsCollection2 = questionsDB2['questions']
		
		questionsWithMedia2 = questionsCollection2.find_one({"media":{"$in":media}})
		if questionsWithMedia2 != None:
			client2.close()		
			client.close()
			return json.dumps({'status':'error', 'error':'question with given media already exists'}), 400

		questionsWithMedia = questionsCollection.find_one({"media":{"$in":media}})
		if questionsWithMedia != None:
			client2.close()		
			client.close()
			return json.dumps({'status':'error', 'error':'question with given media already exists'}), 400

		answersWithMedia = answersCollection.find_one({"media":{"$in":media}})
		if answersWithMedia != None:
			client2.close()		
			client.close()
			return json.dumps({'status':'error', 'error':'answer with given media already exists'}), 400

	username = request.cookies.get('username')	
	#username = (getUser(currentCookie))['username']
	score = 0
	is_accepted = False
	timestamp = int(time.time())

	aID = ObjectId()
	answerCount = question['answer_count'] + 1

	credentials = pika.PlainCredentials('cloudUser', 'password')
	parameters = pika.ConnectionParameters(host='192.168.122.8',credentials=credentials)
	connection = pika.BlockingConnection(parameters)
	channel = connection.channel()

	channel.queue_declare(queue='hello')
#
	content = json.dumps({'answerCount': answerCount, 'aID':str(aID), 'questionID': str(question['_id']), 'user':username, 'body':body, 'timestamp':timestamp, 'media':media})
	channel.basic_publish(exchange='', routing_key='hello', body=content)
#       print(" [x] Sent 'Hello World!'")
#       after = time.time()
#       print(after - before)
	connection.close()
	return json.dumps({'status':'OK', 'id': str(aID)})


	#result = answersCollection.insert_one({'aID':str(aID), 'questionID': str(question['_id']), 'user':username, 'body':body, 'score':score, 'is_accepted':is_accepted, 'timestamp':timestamp, 'media':media})
	#if result.acknowledged == True:
	#	answerCount = question['answer_count'] + 1
	#	questionsCollection.update_one({'_id':ObjectId(questionId)},{'$set':{'answer_count':answerCount}})
	#	print("answer ", str(aID), " submitted by user ", username)
	#	return json.dumps({'status':'OK', 'id': str(aID)})
	#else:
	#	return json.dumps({'status':'error', 'error':'Failed to add answer'}), 400

def isLoggedIn(currentId):
	if currentId == "" or currentId == None:
		return False
	return True   
	
	#client = MongoClient('mongodb://192.168.122.15:27017/')
	#tttDB = client['usersDB']
	#users = tttDB['users']

	#query = {'_id':ObjectId(currentId)}
	#result = users.find_one(query)

	#if result == None:
	#	return False
	#return True

@app.route("/addmedia",methods=['POST'])
def addMedia():
	currentCookie = request.cookies.get('_id')
	if isLoggedIn(currentCookie) == False:
		return make_response(json.dumps({'status':'error', 'error':'Must be logged in to add media'}), 401)
	#print("adding media")
	f = request.files['content']
	#fileType = magic.from_file(f, mime=True)
	fType = f.mimetype
	fName = f.filename
	toInsert = f.read()
	db = MongoClient('mongodb://192.168.122.8:27017/').gridfs_example
	fs = gridfs.GridFS(db)
	a = fs.put(toInsert, fileType=fType, poster=currentCookie)
	return json.dumps({"status":"OK", "id":str(a)})
	#return fs.get(a).read(), 201, {'Content-Type':fType}
	#questionsDB = client['questionsDB']
	#mediaCollection = questionsDB['media']


	#filename, file_extension = os.path.splitext(fName)
	#print("filetype", fileType)
	#print("hererrreee")	
	mediaId = uuid.uuid1()
	#try:
	#	requests.post('http://130.245.171.38/deposit', files={'contents': (fName, f, fileType)})
		#print(response.json())
	#
	#except requests.exceptions.Timeout:	
	#	return json.dumps({"status":"OK", "id":str(mediaId)})

	return json.dumps({"status":"OK", "id":str(mediaId)})

@app.route("/media/<mediaId>", methods=['GET'])
def getMedia(mediaId):
	print('hereeeee')
	db = MongoClient('mongodb://192.168.122.8:27017/').gridfs_example
	try:
		fs = gridfs.GridFS(db)
		doc = fs.get(ObjectId(mediaId))
		return doc.read(), 201, {'Content-Type': doc.fileType}
	except:
		return json.dumps({'status':'error', 'error':'media doesnt exist'}), 401
	
	#url = 'http://130.245.171.38/retrieve?mediaID=' + mediaId
	
	#response = requests.get(url)
	#contents = response.content
	#headers = response.headers
	#fileType = str(headers['Content-Type'])
	#return contents, 201, {'Content-Type': fileType}

@app.route("/questions/add", methods=['POST'])
def addQuestion():
	before = time.time()
	#print("in question method")
	currentCookie = request.cookies.get('_id')
	print(currentCookie)
	if isLoggedIn(currentCookie) == False:
		return json.dumps({'status':'error', 'error':'User is not logged in'}), 401	

	request_json = request.get_json()
	#print(request_json)
	try:
		title = request_json['title']
		body = request_json['body']
		tagsArray = request_json['tags']
	except KeyError:
		return json.dumps({'status':'error', 'error':'Missing input data'}), 400
	try:
		media = request_json['media']
		print(media)
	except KeyError:
		media = []
	

	if media != []:
		db = MongoClient('mongodb://192.168.122.8:27017/').gridfs_example
		fs = gridfs.GridFS(db)
		for mediaId in media:
			doc = fs.get(ObjectId(mediaId))
			poster = doc.poster
			if poster != currentCookie:
				return json.dumps({'status':'error', 'error':'media does not belong to user'}), 401
		
		print("probably not supposed to be here")
		client = MongoClient('mongodb://192.168.122.8:27017/')
		questionsDB = client['questionsDB']
		questionsCollection = questionsDB['questions']
		answersCollection = questionsDB['answers']
		
		client2 = MongoClient('mongodb://192.168.122.15:27017/')
		questionsDB2 = client2['questionsDB']
		questionsCollection2 = questionsDB2['questions']
		
		questionsWithMedia2 = questionsCollection2.find_one({"media":{"$in":media}})
		if questionsWithMedia2 != None:
			client2.close()		
			client.close()
			return json.dumps({'status':'error', 'error':'question with given media already exists'}), 400

		questionsWithMedia = questionsCollection.find_one({"media":{"$in":media}})
		if questionsWithMedia != None:
			client2.close()		
			client.close()
			return json.dumps({'status':'error', 'error':'question with given media already exists'}), 400

		answersWithMedia = answersCollection.find_one({"media":{"$in":media}})
		if answersWithMedia != None:
			client2.close()		
			client.close()
			return json.dumps({'status':'error', 'error':'answer with given media already exists'}), 400
#	client.close()
#
#	before = time.time()
	credentials = pika.PlainCredentials('cloudUser', 'password')
	parameters = pika.ConnectionParameters(host='192.168.122.8',credentials=credentials)
	connection = pika.BlockingConnection(parameters)
	channel = connection.channel()

	channel.queue_declare(queue='hello')
#
	qID = ObjectId()
	content = json.dumps({"title": title, "body": body, "tags":tagsArray, "userID":currentCookie, 'timestamp':int(time.time()), 'media':media, '_id':str(qID)})
	channel.basic_publish(exchange='', routing_key='hello', body=content)
#	print(" [x] Sent 'Hello World!'")
#	after = time.time()
#	print(after - before)
	connection.close()
	indexQuestion(str(qID), title, body)
	print(time.time() - before)
	return json.dumps({'status':'OK', 'id': str(qID)})

#	return json.dumps({'status':'OK', 'id': str(qID)})	
#	qid = ObjectId()
#	string = str(qid)
#	print(string)
#	if string[-1] in ["1", "2", "3", "4", "5", "6", "7", "8"]:
#		print(1)
#		client.close()
#		client = MongoClient('mongodb://192.168.122.15:27017/')
#		questionsDB = client['questionsDB']
#		questionsCollection = questionsDB['questions']
#	else:
#		print(0)
#	result = questionsCollection.insert_one({"_id":qid, "title": title, "body": body, "tags": tagsArray, "userID":currentCookie, 'score': 0, 'view_count':0, 'answer_count':0, 'timestamp':int(time.time()), 'media': media, 'accepted_answer_id':None})
#	if result.acknowledged == True:
	#	after = time.time()
	#	print("time: ", after - before)
#		indexQuestion(str(result.inserted_id), title, body)
#		client.close()
		
#		return json.dumps({'status':'OK', 'id': str(result.inserted_id)})
#	else:
#		client.close()
#		return json.dumps({'status':'error', 'error':'Failed to add question'}), 400

def indexQuestion(questionID, title, body):
	credentials = pika.PlainCredentials('cloudUser', 'password')
	parameters = pika.ConnectionParameters(host='192.168.122.12',credentials=credentials)
	connection = pika.BlockingConnection(parameters)
	channel = connection.channel()

	channel.queue_declare(queue='hello')
#
	title = title.lower()
	body = body.lower()
	titleWords = title.split(" ")
	bodyWords = body.split(" ")
	
	contents = titleWords + bodyWords
	content = json.dumps({"contents": contents, "questionID": questionID})
	channel.basic_publish(exchange='', routing_key='hello', body=content)
#       print(" [x] Sent 'Hello World!'")
#       after = time.time()
#       print(after - before)
	connection.close()



	#tInit = time.time()
	#client = MongoClient('mongodb://192.168.122.12:27017/')
	#searchIndexDB = client['questionsIndex']
	#searchIndexCollection = searchIndexDB['questionsIndex']

	#title = title.lower()
	#body = body.lower()
	#titleWords = title.split(" ")
	#bodyWords = body.split(" ")
	#print('here')
	#contents = titleWords + bodyWords
	#for word in contents:
	#	searchIndexCollection.update_one({"word":word}, {'$addToSet': {"ids":questionID}}, upsert=True)
	#searchIndexCollection.update_many({"word": {"$in": contents}}, {'$addToSet': {"ids":questionID}}, upsert=True)
	#client.close()
	#tEnd = time.time()
	#print(tEnd - tInit)

@app.route("/cookieTest", methods=['POST'])
def testCookie():
	request_json = request.get_json()
	cookie = request.cookies.get('_id')
	return json.dumps({'newPage': "<h1>Cookie: " + cookie + "</h1>"})

@app.route("/listgames", methods=['POST', 'GET'])
def listGames():
	cookie = request.cookies.get('_id')

	if cookie == None:
		return json.dumps({'status':'ERROR'})
	
	client = MongoClient('localhost', 27017)
	tttDB = client['ttt']
	users = tttDB['users']
	gamesCol = tttDB['games']

	query = {'_id':ObjectId(cookie)}
	result = users.find(query)

	games = []
	gamesList = []
	for x in result:
		games = x['games']
	for game in games:
		gameId = game
		gameRecord = gamesCol.find_one({'_id':ObjectId(gameId)})
		startDate = gameRecord['start_date']
		gamesList.append({"id":str(gameId), "start_date":startDate})
		

	return json.dumps({'games':gamesList, 'status':'OK'})
	

@app.route("/getgame", methods=['POST'])
def getGame():
	cookie = request.cookies.get('_id')
	
	if cookie == None:
		return json.dumps({'status':'ERROR'})

	gameId = (request.get_json())['id']

	client = MongoClient('localhost', 27017)
	tttDB = client['ttt']
	users = tttDB['users']
	games = tttDB['games']

	user = users.find_one({'_id':ObjectId(cookie)})
	gamesArray = user['games']
	found = False
	print("GamesArray: " + str(gamesArray))
	for game in gamesArray:
		if str(game) == gameId:
			found = True
	
	grid = []
	winner = ''
	if found:
		gameRecord = games.find_one({'_id':ObjectId(gameId)})
		grid = gameRecord['grid']
		winner = gameRecord['winner']
		return json.dumps({'status':'OK', 'grid':grid, 'winner':winner})
	else:
		return json.dumps({'status':'ERROR'})
@app.route('/getscore', methods=['GET', 'POST'])
def getScore():
	cookie = request.cookies.get('_id')

	if cookie == None:
		return json.dumps({'status':'ERROR'})
	
	client = MongoClient('localhost', 27017)
	tttDB = client['ttt']
	users = tttDB['users']
	gamesCol = tttDB['games']

	query = {'_id':ObjectId(cookie)}
	result = users.find(query)

	games = []
	gamesList = []
	for x in result:
		games = x['games']

	humanWins = 0
	compWins = 0
	ties = 0
	for game in games:
		gameId = game
		gameRecord = gamesCol.find_one({'_id':ObjectId(gameId)})
		winner = gameRecord['winner']
		if (winner == 'X'):
			humanWins = humanWins + 1
		if (winner == 'O'):
			compWins = compWins + 1
		if (winner == ' '):
			ties = ties + 1
	
	return json.dumps({'human':humanWins, 'wopr':compWins, 'tie':ties, 'status':'OK'})
	
@app.route("/ttt/", methods=['GET', 'POST'])
def ttt():
    try:
        name = request.form['name']
        date = datetime.datetime.today()
        dateStr = date.strftime("%Y-%m-%d")
        return render_template('ttt.html', name=name, date=dateStr, grid="")
    except:
        return render_template('ttt.html', name="", grid="")

@app.route("/ttt/play", methods=['GET', 'POST'])
def play():
	request_json = request.get_json()
	move = None
	if request_json != None:
		move = request_json['move']
	
	cookie = request.cookies.get('_id')	
	print("user id: " + str(cookie))

	if cookie == None:
		return json.dumps({'status':'ERROR'})

	client = MongoClient('localhost', 27017)
	tttDB = client['ttt']
	users = tttDB['users']
	games = tttDB['games']

	query = {'_id':ObjectId(cookie)}
	result = users.find(query)


	currentGrid = ""
	currentGame = "null"
	for x in result:
		currentGame = x['currentGame']
	print("Move: " + str(move))
	if move == None:
		currentGrid = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
		winner = ' '
		if currentGame != "null":
			game = games.find_one({'_id':ObjectId(currentGame)})
			currentGrid = game['grid']
			winner = game['winner']
		json_string = json.dumps({'grid':currentGrid, 'winner':winner})
		return json_string

	print(str(currentGame));
	if currentGame == "null":
		print("current game == null")
		currentGrid = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
		date = datetime.datetime.today()
		dateStr = date.strftime("%Y-%m-%d")
		result = games.insert_one({'grid': currentGrid, 'winner':' ', 'start_date':dateStr})
		print("New Game Started: " + str(result.inserted_id))
		currentGame = result.inserted_id
		users.update_one({'_id':ObjectId(cookie)}, {'$set':{'currentGame':result.inserted_id}})
		users.update_one({'_id':ObjectId(cookie)}, {'$push':{'games':result.inserted_id}})
	else:
		game = games.find({'_id':ObjectId(currentGame)})
		for x in game:
			currentGrid = x['grid']
	currentGrid[int(move)] = 'X'

	winner = getWinner(currentGrid)
	compMove = -1
	if winner == ' ':
		compMove = AIMove(currentGrid)
	if compMove != -1:
		currentGrid[compMove] = "O"
	winner = getWinner(currentGrid)
	games.update_one({'_id':ObjectId(currentGame)}, {'$set':{'grid':currentGrid}})
	games.update_one({'_id':ObjectId(currentGame)}, {'$set':{'winner':winner}})

	if winner != ' ':
		users.update_one({'_id':ObjectId(cookie)},{'$set':{'currentGame':'null'}})
	json_string = json.dumps({'grid':currentGrid, 'winner':winner})
	print(json_string)
	return json_string

def getWinner(grid):
    for i in range(0, 3):
        if grid[i*3] == 'X' and grid[i*3+1] == 'X' and grid[i*3+2] == 'X':
            return 'X'
        if grid[i] == 'X' and grid[i+3] == 'X' and grid [i+6] == 'X':
            return 'X'
    if grid[0] == 'X' and grid[8] == 'X' and grid[4] == 'X':
        return 'X'
    if grid[2] == 'X' and grid[6] == 'X' and grid[4] == 'X':
        return 'X'

    for i in range(0, 3):
        if grid[i*3] == 'O' and grid[i*3+1] == 'O' and grid[i*3+2] == 'O':
            return 'O'
        if grid[i] == 'O' and grid[i+3] == 'O' and grid [i+6] == 'O':
            return 'O'
    if grid[0] == 'O' and grid[8] == 'O' and grid[4] == 'O':
        return 'O'
    if grid[2] == 'O' and grid[6] == 'O' and grid[4] == 'O':
        return 'O'
    return ' '

def AIMove(grid):
	for i in range(0, 3):
		if grid[i*3] == 'X' and grid[i*3+1] == ' ' and grid[i*3+2] == 'X':
			return i*3+1
		if grid[i*3] == 'X' and grid[i*3+1] == 'X' and grid[i*3+2] == ' ':
			return i*3+2
		if grid[i*3] == ' ' and grid[i*3+1] == 'X' and grid[i*3+2] == 'X':
			return i*3
		if grid[i] == ' ' and grid[i+3] == 'X' and grid [i+6] == 'X':
			return i
		if grid[i] == 'X' and grid[i+3] == ' ' and grid [i+6] == 'X':
			return i+3
		if grid[i] == 'X' and grid[i+3] == 'X' and grid [i+6] == ' ':
			return i+6
	if grid[0] == 'X' and grid[8] == 'X' and grid[4] == ' ':
		return 4
	if grid[0] == 'X' and grid[8] == ' ' and grid[4] == 'X':
		return 8
	if grid[0] == ' ' and grid[8] == 'X' and grid[4] == 'X':
		return 0
	if grid[2] == 'X' and grid[6] == 'X' and grid[4] == ' ':
		return 4
	if grid[2] == 'X' and grid[6] == ' ' and grid[4] == 'X':
		return 6
	if grid[2] == ' ' and grid[6] == 'X' and grid[4] == 'X':
		return 2
	for i in range(0, 9):
		if grid[i] == ' ':
			return i
	return -1



	    
        













if __name__ == "__main__":
    app.run(host='0.0.0.0')
