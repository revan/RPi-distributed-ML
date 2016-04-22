import random
from clustermessaging.Messager import Messager
from clustermessaging.LED import LED

led = LED()
m = Messager()

m.registerCallbackSync()
m.start()


def setState(state):
    m.lifeState = state
    if state:
        led.setRedOn()
    else:
        led.setRedOff()

setState(random.randint(0, 1) == True)

i = 0
while True:
    i += 1
    for neighbor in m.getNeighbors().keys():
        message = {
            'state': m.lifeState,
            'sync': i
        }

        m.sendMessage(neighbor, message)

    m.waitForMessageFromAllNeighbors(i)

    c = sum(n['state'] for n in m.sync[i])
    if c <= 1 or c >= 4:
        setState(False)
    if c == 3:
        setState(True)
