from flask import Flask, jsonify, render_template, make_response, request, json
from pymongo import MongoClient
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

app = Flask(__name__)

name = ""
date = datetime.datetime.today()
dateStr = date.strftime("%Y-%m-%d")

@app.route("/speak", methods=['GET', 'POST'])
def speak():
	request_json = request.get_json()
	key = request_json['key']
	msg = request_json['msg']

	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.exchange_declare(exchange='hw3')

	channel.basic_publish(exchange='hw3', routing_key=key, body=msg)
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
    try:
        name = request.form['name']
        return render_template('ttt.html', name=name, date=dateStr)
    except:
        return render_template('ttt.html', name="")

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
	
	client = MongoClient('localhost', 27017)
	tttDB = client['ttt']
	users = tttDB['users']
	games = []
	result = users.insert_one({"reputation": 0, "games":games, "currentGame": "null", "username": username, "password": password, "email": email, "verified": "false"})
	#result = users.insert_one({"username": "test", "password": "hello", "email": "e", "verified": "false"})

	if result.acknowledged == True:
		port = 587  # For starttls
		smtp_server = "smtp.gmail.com"
		sender_email = "cse356cloudproject@gmail.com"
		receiver_email = email
		password = "cse356cloud"
		msg = MIMEText("Please visit http://130.245.170.251/verifyEmail and enter the following key to verify your email\n validation key: <" + str(result.inserted_id) + ">")
		msg['Subject'] = "Email Verification for TTT"
		context = ssl.create_default_context()
		s = smtplib.SMTP(smtp_server, port)
		s.starttls(context=context)
		s.login(sender_email, password)
		s.sendmail(sender_email, receiver_email, msg.as_string())
		return json.dumps({'status': 'OK'})
	return json.dumps({'status': 'ERROR'})


@app.route("/verify", methods=['POST'])
def verifyUser():
	request_json = request.get_json()
	email = request_json['email']
	key = request_json['key']
        
	client = MongoClient('localhost', 27017)
	tttDB = client['ttt']
	users = tttDB['users']
	
	print(key)
	if key == 'abracadabra':
		query = {'email':email}
		result = users.find(query)
		found = False
		for x in result:
			found = True
		if found:
			users.update_one({'email':email},{'$set':{'verified':'true'}})
			return json.dumps({'status':'OK'})
	try:
		query = {'_id':ObjectId(key), 'email':email}
		result = users.find(query)
		found = False
		for x in result:
			found = True
		if found:
			users.update_one({'_id':ObjectId(key)}, {'$set':{'verified':'true'}})
			return json.dumps({'status':'OK'})
		return json.dumps({'status':'ERROR', 'error':'Invalid email or validation key'})
	except:
		return json.dumps({'status':'ERROR', 'error':'Invalid email or validation key'})

@app.route("/login", methods=['POST'])
def login():
	request_json = request.get_json()
	username = request_json['username']
	password = request_json['password']

	client = MongoClient('localhost', 27017)
	tttDB = client['ttt']
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
		return response
	
	return json.dumps({'status':'ERROR'})

@app.route("/logout", methods=['POST', 'GET'])
def logout():
	currentCookie = request.cookies.get('_id')
	response = jsonify(status='OK', cookie=str(currentCookie))
	response.set_cookie('_id', '')
	print("user " + str(currentCookie) + "logged out") 
	return response

def getUser(Id):
	client = MongoClient('localhost', 27017)
	tttDB = client['ttt']
	users = tttDB['users']

	user = users.find_one({'_id': ObjectId(Id)})
	return {'id':Id, 'username':user['username'], 'reputation':user['reputation']}

@app.route("/questions/<questionId>", methods=['GET'])
def getQuestion(questionId):
	
	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	questionsCollection = questionsDB['questions']

	print(questionId)

	query = {'_id': ObjectId(questionId)}
	question = questionsCollection.find_one(query)

	if question == None:
		return json.dumps({'status':'error', 'error':'Invalid question id'})
	
	user = getUser(question['userID'])

	print(user)

	questionJson = {'id':questionId, 'user':user, 'body':question['body'], 'title':question['title'], 'score':question['score'], 'view_count':question['view_count'], 'answer_count':question['answer_count'], 'timestamp':question['timestamp'], 'media':question['media'], 'tags':question['tags'], 'accepted_answer_id':question['accepted_answer_id']} 
	return json.dumps({'status':'OK', 'question':questionJson})

@app.route("/questions/<questionId>/answers", methods=['GET'])
def getAnswers(questionId):
	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	answersCollection = questionsDB['answers']

	query = {'questionID':questionId}
	results = answersCollection.find(query)
	answersArray = []
	if results == None:
		return json.dumps({'status':'error', 'error':'Invalid question id, or question has no answers'})
	else:
		for answer in results:
			currentAnswer = {'user':answer['user'], 'body':answer['body'], 'score':answer['score'], 'is_accepted':answer['is_accepted'], 'timestamp':answer['timestamp'], 'media':answer['media']}
			answersArray.append(currentAnswer)
		return json.dumps({'status':'OK', 'answers':answersArray})

@app.route("/search", methods=['POST'])
def search():
	request_json = request.get_json()
	timestamp = time.time()
	limit = 25
	accepted = False
	try:
		timestamp = request_json['timestamp']
	except KeyError:
		print("Setting timestamp to default = current time")
	try:
		limit = request_json['limit']
		if limit > 100:
			return json.dumps({'status':'error', 'error':'Cannot have limit higher than 100'})
	except KeyError:
		print("Setting limit to default = 25")
	try:
		accepted = request_json['accepted']
	except KeyError:
		print("Setting accepted to default = false")

	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	questionsCollection = questionsDB['questions']

	query = {'timestamp':{'$lte': timestamp}}
	if accepted:
		query = {'timestamp':{'$lte': timestamp}, 'accepted_answer_id':{'$ne':None}}

	results = questionsCollection.find(query).sort("timestamp", pymongo.DESCENDING)
	questionsArray = []
	count = 0
	for question in results:
		if count >= limit:
			break
		user = getUser(question['userID'])
		questionJson = {'id':str(question['_id']), 'title':question['title'], 'user':user, 'body':question['body'], 'score':question['score'], 'view_count':question['view_count'], 'answer_count':question['answer_count'], 'timestamp':question['timestamp'], 'media':question['media'], 'tags':question['tags'], 'accepted_answer_id':question['accepted_answer_id']}
		questionsArray.append(questionJson)

	return json.dumps({'status':'OK', 'questions':questionsArray})


@app.route("/questions/<questionId>/answers/add", methods=['POST'])
def addAnswer(questionId):
	currentCookie = request.cookies.get('_id')
	if currentCookie == '':
		return json.dumps({'status':'error', 'error':'User is not logged in'})

	request_json = request.get_json()
	body = request_json['body']
	try:	
		media = request_json['media']
	except KeyError:
		media = ""
	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	questionsCollection = questionsDB['questions']
	answersCollection = questionsDB['answers']

	query = {'_id': ObjectId(questionId)}
	question = questionsCollection.find_one(query)

	if question == None:
		return json.dumps({'status':'error', 'error':'Invalid quetion id'})

	username = (getUser(question['userID']))['username']
	score = 0
	is_accepted = False
	timestamp = time.time()

	result = answersCollection.insert_one({'questionID': str(question['_id']), 'user':username, 'body':body, 'score':score, 'is_accepted':is_accepted, 'timestamp':timestamp, 'media':media})
	if result.acknowledged == True:
		return json.dumps({'status':'OK', 'id': str(result.inserted_id)})
	else:
		return json.dumps({'status':'error', 'error':'Failed to add answer'})


@app.route("/questions/add", methods=['POST'])
def addQuestion():
	currentCookie = request.cookies.get('_id')
	if currentCookie == '':
		return json.dumps({'status':'error', 'error':'User is not logged in'})
	

	request_json = request.get_json()
	title = request_json['title']
	body = request_json['body']
	tagsArray = request_json['tags']
	
	client = MongoClient('mongodb://192.168.122.8:27017/')
	questionsDB = client['questionsDB']
	questionsCollection = questionsDB['questions']

	result = questionsCollection.insert_one({"title": title, "body": body, "tags": tagsArray, "userID":currentCookie, 'score': 0, 'view_count':0, 'answer_count':0, 'timestamp':time.time(), 'media': "", 'accepted_answer_id':None})
	if result.acknowledged == True:
		return json.dumps({'status':'OK', 'id': str(result.inserted_id)})
	else:
		return json.dumps({'status':'error', 'error':'Failed to add question'})

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
    app.run()
