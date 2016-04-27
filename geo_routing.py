# Greedy Geo-Routing (async)
import math
import time
import random
from clustermessaging.LED import LED
from clustermessaging.Messager import Messager
import kazoo.recipe.watchers
from kazoo.protocol.states import EventType

led = LED()
m = Messager()

def forwardMessage(path=None):
    if not path:
        path = []

    def distanceToTarget(coords):
        target = m.getTarget()
        return math.sqrt((target[0] - coords[0]) ** 2 + (target[1] - coords[1]) ** 2)

    distances = [(distanceToTarget(m.getLocation(id)), id) for id in m.getNeighbors().keys()]
    distances.append((distanceToTarget(m.getOwnLocation()), m.getOwnName()))
    mindist = min(distances)[0]

    closest_neighbor = random.choice([neighbor for (dist, neighbor) in distances if dist == mindist])

    path.append(m.getOwnName())

    if closest_neighbor == m.getOwnName():
        led.setRedOn()
        print('I am the closest node! Path to me was %s' % '->'.join(path))
        time.sleep(3)
        m.zk.set("/routing", str(m.topo['version']).encode())
    else:
        led.setGreenOn()
        print('sending message to %s' % closest_neighbor)
        time.sleep(1)
        m.sendMessage(closest_neighbor, {'path': path})


def callback(message, name):
    print('Got message from %s: %s' % (name, message))

    forwardMessage(message['path'])

m.registerCallback(callback)
m.start()


def init():
    led.setGreenOff()
    led.setRedOff()

    if m.startIsMe():
        led.setRedOn()
        m.zk.ensure_path("/routing")
        time.sleep(1)
        forwardMessage()


@m.zk.DataWatch('/routing')
def zkCallback(data, stat, event):
    if event and event.type == EventType.CHANGED and data and data.decode() != m.topo['version']:
        print('Reloading topology!')
        m.reloadTopology()
        init()

init()

while True:
    time.sleep(1)