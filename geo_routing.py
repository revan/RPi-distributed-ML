# Greedy Geo-Routing (async)
import math
import time
from clustermessaging.Messager import Messager

m = Messager()

def forwardMessage(path=[]):
    def distanceToTarget(coords):
        target = m.getTarget()
        return math.sqrt((target[0] - coords[0]) ** 2 + (target[1] - coords[1]) ** 2)

    distances = [(distanceToTarget(m.getLocation(id)), id) for id in m.getNeighbors().keys()]
    distances.append((distanceToTarget(m.getOwnLocation()), m.getOwnName()))
    closest_neighbor = min(distances)[1]

    path.append(m.getOwnName())

    if closest_neighbor == m.getOwnName():
        print('I am the closest node! Path to me was %s' % '->'.join(path))
    else:
        print('sending message to %s' % closest_neighbor)
        m.sendMessage(closest_neighbor, {'path': path})


def callback(message, name):
    print('Got message from %s: %s' % (name, message))

    forwardMessage(message['path'])

m.registerCallback(callback)
m.start()

if m.startIsMe():
    time.sleep(1)
    forwardMessage()

while True:
    time.sleep(1)