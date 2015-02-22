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

    # initialize the game
    games[sessionName] = {}
    games[sessionName].playerId = 0
    games[sessionName].players[playerId] = data.username

    # Start listening on Redis if this is your first game
    if thread == None:
        thread = sessions.run_in_thread(sleep_time=0.001)
    
    # Tell other players in the game that you joined
    Redis.public(sessionName, json.dumps({type:'join',username:username}))

def handleSession(message):
    if message == None:
        return
    if message['type'] != 'message':
        return

    handleGame(message['data'], message['channel'])

def handleGame(message, session):
    data = json.loads(message)
    game = games[session]

    # send your name and player id when you join, and store their username
    if data.type == 'join':
        for i in range(0,4):
            if i not in game.players:
                game.players[i] = data.username
                break

        Redis.publish(session, json.dumps({
            id:game.playerId,
            username:username
        }))

    # Tell new players that you're in the game
    elif data.type == 'player':
        # Check if there's already a play with my id
        if data.id == game.playerId and data.username != username:
            while game.playerId in game.players:
                game.playerId = game.playerId + 1

        if not data.id in game.players:
            game.players[data.id] = data.username

    elif data.type == 'dealer' and data.player == game.playerId:
        game.dealing = true
        game.deck = shuffleDeck()
        dealCards()

    elif data.type == 'suit':
        game.trump = data.suit

    elif data.type == 'deal' and data.player == game.playerId:
        game.hand.append(data.card)
        sendMessage({type:'deal', card:data.card})

    elif data.type == 'topCard':
        game.topCard = data.card
        sendMessage({type:'topCard', card:data.card})

    elif data.type == 'turn':
        sendMessage({type:'turn'})

    elif data.type == 'pickItUp' and game.dealing:
        sendMessage({type:'pickItUp', card:data.card})
        Redis.publish(session, json.dumps({
            type:'suit',
            suit:data.card.suit
        }))

    elif data.type == 'playCard':
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

