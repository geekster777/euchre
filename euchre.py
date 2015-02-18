import threading, redis
from sys import stdin, stdout

Redis = redis.StrictRedis(host='localhost', port=6379, db=0)
sessions = Redis.pubsub()
games = {}
thread = None

def handleMessage(message):
    args = message.split()
    
    if args[0] == 'join':
        print('@')
        stdout.flush()
        joinSession(args[1])
    elif args[0] == 'message':
        Redis.publish(args[1], ' '.join(args[2:]))

def joinSession(sessionName):
    global thread
    # Start subscribing to session messages
    sessions.subscribe(**{sessionName: handleSession})
    games[sessionName] = {}
    
    if thread == None:
        thread = sessions.run_in_thread(sleep_time=0.001)

def handleSession(message):
    print('$')
    stdout.flush()
    if message == None:
        return
    if message['type'] != 'message':
        return
    print(message['data'])
    stdout.flush()

handleMessage('join test')

while True:
    line = stdin.readline().strip()
    handleMessage(line)

if thread != None:
    thread.stop()

