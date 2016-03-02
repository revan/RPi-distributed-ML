# Async averaging (gossip)
import time
import numpy as np
from threading import Lock
import random
from clustermessaging.Messager import Messager

m = Messager()
lock = Lock()

m.mynum = float(np.random.randint(100))
print('My num: %d' % m.mynum)

def callback(message, name):
    print('Got message from %s: %s' % (name, message))
    lock.acquire()

    if message['rsvp']:
        print('Replying...')
        reply = {
            'num': m.mynum,
            'rsvp': False
        }
        m.sendMessage(name, reply)

    print('old avg: %f' % m.mynum)
    m.mynum = (m.mynum + float(message['num'])) / 2
    print('new avg: %f' % m.mynum)

    lock.release()

m.registerCallback(callback)
m.start()

while True:
    sleep = np.random.poisson(5)
    print('sleeping for %d seconds...' % sleep)
    time.sleep(sleep)

    neighbor = random.choice(list(m.getNeighbors().keys()))
    message = {
        'num': m.mynum,
        'rsvp': True
    }
    print('Contacting neighbor %s wih message %s...' % (neighbor, message))
    m.sendMessage(neighbor, message)
