from flask import Flask, jsonify, render_template, make_response, request, json
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import re
import dns.resolver
import socket
import smtplib, ssl
from email.mime.text import MIMEText
from http import cookies

app = Flask(__name__)

name = ""
date = datetime.datetime.today()
dateStr = date.strftime("%Y-%m-%d")

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
	result = users.insert_one({"games":games, "currentGame": "null", "username": username, "password": password, "email": email, "verified": "false"})
	#result = users.insert_one({"username": "test", "password": "hello", "email": "e", "verified": "false"})

	if result.acknowledged == True:
		port = 587  # For starttls
		smtp_server = "smtp.gmail.com"
		sender_email = "cse356cloudproject@gmail.com"
		receiver_email = "s.n.belliveau@gmail.com"
		password = "Samiam5678!"
		msg = MIMEText("Please visit http://130.245.170.251/verifyEmail and enter the following key to verify your email: " + str(result.inserted_id))
		msg['Subject'] = "Email Verification for TTT"
		context = ssl.create_default_context()
		s = smtplib.SMTP(smtp_server, port)
		s.starttls(context=context)
		s.login(sender_email, password)
#		s.sendmail(sender_email, receiver_email, msg.as_string())
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
		return json.dumps({'status':'ERROR'})
	except:
		return json.dumps({'status':'ERROR'})

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
