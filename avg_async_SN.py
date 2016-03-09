# Async averaging (gossip)
# SensorNetwork implementation
import time
import numpy as np
from threading import Lock
import random
from clustermessaging.SensorNetwork import SensorNetwork

m = SensorNetwork()
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

def sensor():
    lock.acquire()
    num = m.mynum
    lock.release()
    return num

def process(sensorValue):
    neighbor = random.choice(list(m.getNeighbors().keys()))
    message = {
        'num': sensorValue,
        'rsvp': True
    }
    print('Contacting neighbor %s wih message %s...' % (neighbor, message))
    m.sendMessage(neighbor, message)

m.startProcessing(
    processingFunction=process,
    callbackFunction=callback,
    sensorFunction=sensor,
    stopConditionFunction=lambda: False,
    delay=lambda: np.random.poisson(5))


