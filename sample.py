# Demo of Messager class.
# run with: DEVICE_ID=1 python sample.py
import os
import time
from clustermessaging.Messager import Messager

m = Messager()

def callback(message):
    print('Message Received! %s' % message)

if os.environ['DEVICE_ID'] == '2':
    print('registering callback')
    m.registerCallback(callback)
    m.start()
else:
    print('sending message')
    m.sendMessage('2', 'hello, 2, i am %s' % m.getOwnName())
    m.start()
