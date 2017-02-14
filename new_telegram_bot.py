# -*- coding: utf-8 -*-
import threading, httplib, requests, json, random, psycopg2
API = "https://api.telegram.org/bot"

# Dictionary filling
##################################################################################
dictionary = ["kbtu", "dota", "four"]
dictionary2 = ["kbtu", "room", "dude", "goal", "cafe", "dota", "ball", "baby", "edge", 
"fire", "hair", "kiwi", "meat", "ruby", "shop", "swag", "zone", "toad", "grid", "slim", "tomb", "wolf", 
"mask", "bone", "game", "page", "tail", "book", "coma", "dank", "boar", "rank", "four"]
f2 = open('words.txt', 'r')
for i in f2:
	for j in i.split():
		dictionary.append(j) 
f2.close()
offset = 0
####################################################################################
userData = {}
# Connection to the DB
###################################################################################
try:
    conn = psycopg2.connect("dbname='' user='' host='' password=''")
    cur = conn.cursor()
except Exception,e:
	print(e)
###################################################################################

def long_polling():
	print 'Send Request'
	#########################################################################
	#f = open('update_id.txt', 'r+')
	#a = f.read()
	#update_id = int(a)
	#########################################################################
	global offset
	params = {'offset' : (offset+1)}
	data = json.loads(requests.get(API+'getUpdates', params=params).content)
	result = data['result']
	print(offset)
	for i in result:
		message = i['message']
		offset = i['update_id']
		user = {}
		if (offset != 0):
			try:
				msg = saveUserData(message)
				processing(message['chat']['id'], msg)
			except Exception,e:
				#print(str(message)+" - ")
				print(e)
				#send_message(message['chat']['id'], "Я могу читать только слова из 4 букв на английском")
	
	#########################################################################
	thread = threading.Timer(3,long_polling)
	thread.start()

def send_message(chat_id, text):
	row = [{'text': "Новая игра"},{'text': "Закончить"}, {'text': "Рейтинг"}]
	arrOfRow = [row]
	keyboard = {'keyboard':arrOfRow, 'resize_keyboard':True}
	#keyboard = {'inline_keyboard':arrOfRow}
	#keyboard = json.dumps(keyboard)
	params = {'chat_id':chat_id, 'text': text, 'reply_markup': json.dumps(keyboard)}
	requests.post(API+'sendMessage', params=params)

def processing(chat_id, message):
	print(message)
	msg = (message['message_text']).encode('utf8')
	text = ""
	if msg == "/new" or msg == "Новая игра":
		print("New Game")	
		if chat_id in userData:
			text = gameEnd(chat_id,0)
			send_message(chat_id,text)
		text = newGame(chat_id, message)
	elif (msg == "/end" or msg == "Закончить") and chat_id in userData:
		print("Game End")
		text = gameEnd(chat_id, 0)
	elif msg == "/top" or msg == "Рейтинг":
		print("Ranking")
		text = show_leaderboard()
	elif chat_id in userData:
		print("Game Process")
		text = gameProcess(chat_id, msg)
	else:
		text="Если хотите начать новую игру введите '/new' или '/end', чтобы закончить игру. /top - рейтинг лучших игроков"
		#text="If you want start a new game type '/new' or finish type '/end'"
	send_message(chat_id, text)

def newGame(chat_id, message):
	k = random.randint(0,len(dictionary2))
	tmp = {}
	tmp['answer'] = dictionary2[k]
	tmp['username'] = message['username']
	tmp['steps'] = 0
	tmp['first_name'] = message['first_name']
	tmp['last_name'] = message['last_name']
	# userData[chat_id]['answer'] = dictionary2[k]
	# userData[chat_id]['username'] = message['username'] 
	# userData[chat_id]['steps'] = 0
	# userData[chat_id]['first_name'] = message['first_name']
	# userData[chat_id]['last_name'] = message['last_name']
	userData[chat_id] = tmp
	print(userData[chat_id])
	#return "New Game started! Give me your word:"
	return "Новая игра началась! Напишите слово:"

def gameEnd(chat_id, status):
	userInfo = userData[chat_id]
	userData.pop(chat_id,None)
	if status == 1:
		update_stats(chat_id,userInfo,userInfo['steps'])
		return win(userInfo['answer'], chat_id)
	elif status == 0:
		return lose(userInfo['answer'], chat_id)

def gameProcess(chat_id, message):
	text = ""
	msg = message.lower()
	res = 0
	word = userData[chat_id]['answer']
	if msg in dictionary:
		userData[chat_id]['steps'] += 1
		if msg == word:
			print("Game End")
			return gameEnd(chat_id,1)
		a = list(word)
		b = list(msg)
		for i in range(0,4):
			for j in range(0,4):
				if a[i] == b[j] and a[i]!='@':
					res += 1
					a[i] = '@'
					b[j] = '@'
		text = str(res)
	#if (len(msg) != 4 or msg[0]=='@' or msg[1]=='@' or msg[2]=='@' or msg[3]=='@'):
	elif len(msg)!=4:
		text = "Нужно слова из 4 букв на английском."
	else:
		text = "Такого слова я не знаю."
	
	return msg + " - " + text

def lose(word, chat_id):
	#return "You lose. Answer: "+ word +"\n If you like this bot, please subscribe us in Instagram https://goo.gl/oYIXE6"
	return "Вы проиграли! Ответ: "+ word +"\n Если вам понравилась игра, подпишитесь пожалуйста в Instagram https://goo.gl/oYIXE6\n"

def win(word, chat_id):
	#return "You win!!! Steps: " + str(steps[chat_id]) +"\n If you like this bot, please subscribe us in Instagram https://goo.gl/oYIXE6"
	return "Вы выиграли! Количество шагов: " + str(userData[chat_id]['steps']) +"\n Если вам понравилась игра, подпишитесь пожалуйста в Instagram https://goo.gl/oYIXE6\n"

def saveUserData(message):
	cur.execute("SELECT * from users Where chat_id="+str(message['chat']['id'])+";")
	a = cur.fetchall()
	#print(a)
	chat_id = str(message['chat']['id'])
	username = "Null"
	first_name = "Null"
	last_name = "Null"
	message_text = "Null"
	date_time = "Null"
	if 'username' in message['chat']:
		username = str(message['chat']['username'])
	if 'first_name' in message['chat']:
		first_name = str(message['chat']['first_name'])
	if 'last_name' in message['chat']:
		last_name = str(message['chat']['last_name'])
	if 'date' in message:
		date_time = str(message['date'])
	if 'text' in message:
		message_text = str(message['text'].encode('utf8'))
	c = "'"''
	if len(a) is 0:
		cur.execute("Insert into users (chat_id, username, first_name, last_name, best_result) Values ("+str(chat_id)+","+c+str(username)+c+","+c+str(first_name)+c+","+c+str(last_name)+c+",Null);")
		conn.commit()
	cur.execute("Insert into history (chat_id, username, first_name, last_name, message, date_time) Values ("+str(chat_id)+","+c+str(username)+c+","+c+str(first_name)+c+","+c+str(last_name)+c+","+c+str(message_text)+c+","+str(date_time)+");")
	conn.commit()
	user = {}
	user['username'] = username
	user['first_name'] = first_name
	user['last_name'] = last_name
	user['message_text'] = message_text
	user['date'] = date_time	
	return user

def update_stats(chat_id, userInfo, best_result):
	c = "'"
	username = userInfo['username']
	f_name = userInfo['first_name']
	l_name = userInfo['last_name']
	#print(best_result)
	res = "UPDATE users SET username="+c+username+c+",first_name="+c+f_name+c+",last_name="+c+l_name+c+",best_result="+str(best_result)+" WHERE chat_id="+str(chat_id)+" and (best_result is Null or best_result>"+str(best_result)+ ");"
	cur.execute(res)
	global conn
	conn.commit()
	print("Updated result"+str(best_result))

def show_leaderboard():
	text = ""
	try:
		global cur
		cur.execute("""SELECT * from users""")
		rows = cur.fetchall()
		board = []
		for row in rows:
			tmp = {}
			if row[2] is not None:
				tmp['username'] = row[2]
			elif (row[3] is not None and row[4] is not None):
				tmp['username'] = str(row[3])+" "+str(row[4])
			elif row[3] is not None:
				tmp['username'] = str(row[3])
			elif row[4] is not None:
				tmp['username'] = str(row[4])
			else:
				tmp['username'] = "unknown username"
			if row[5] is not None and row[5] != 0:
				tmp['steps'] = row[5]
				board.append(tmp)
		newlist = sorted(board, key=lambda x: x['steps'])
		for i in range(0,min(len(newlist),10)):
			text += str(i+1) + ". " + newlist[i]['username']+" - "+str(newlist[i]['steps'])+"\n"
	except Exception,e:
				text = str(e)
	return text

t = threading.Timer(3, long_polling)
t.start()


