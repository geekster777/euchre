import threading, redis, json
from sys import stdin, stdout

Redis = redis.StrictRedis(host='localhost', port=6379, db=0)
sessions = Redis.pubsub()
games = {}
username = 'user'
thread = None

def sendMessage(messageObj):
    print(json.dumps(messageObj))
    stdout.flush()

def handleMessage(message):
    args = message.split()

    if args[0] == 'login':
        global username
        username = args[1]
    elif args[0] == 'join':
        stdout.flush()
        joinSession(args[1])
    elif args[0] == 'message':
        Redis.publish(args[1], ' '.join(args[2:]))

def joinSession(sessionName):
    global thread
    # Start subscribing to session messages
    sessions.subscribe(**{sessionName: handleSession})
    games[sessionName] = {}
    Redis.public(sessionName, json.dumps({type:'join',username:username}))
    
    if thread == None:
        thread = sessions.run_in_thread(sleep_time=0.001)

def handleSession(message):
    stdout.flush()
    if message == None:
        return
    if message['type'] != 'message':
        return

    handleGame(message['data'], message['channel'])

def handleGame(message, session):
    data = json.loads(message)
    game = games[session]

    if data.type == 'join':
        playerId = len(game.players)
        game.players[playerId] = data.username
    if data.type == 'player':
        game.players[data.id] = data.username
    if data.type == 'dealer':
        game.dealing = true
    if data.type == 'trump':
        game.trump = data.suit
    if data.type == 'dealtCard':
        game.hand.append(data.card)
    if data.type == 'playCard':
        game.gameCards.append(data.card)
        sendMessage({type:'playCard', user:data.username, card:data.card})
        
        if len(game.gameCards) == 4:
            winner = calcWinner(game.gameCards)
            sendMessage({type:'winner', winner:game.players[winner]})

while True:
    line = stdin.readline().strip()
    handleMessage(line)

if thread != None:
    thread.stop()

