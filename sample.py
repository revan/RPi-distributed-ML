# Demo of Messager class.
# run with: DEVICE_ID=1 python sample.py
import os
import time
from clustermessaging.Messager import Messager

m = Messager()

def callback(message, name):
    print('Message Received from %s! %s' % (name, message))

if os.environ['DEVICE_ID'] == '2':
    print('registering callback')
    m.registerCallback(callback)
else:
    print('sending message')
    m.sendMessage('2', 'hello, 2, i am %s' % m.getOwnName())

m.start()
