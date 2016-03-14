# just sends a value to neighbors three times, to demonstrate synchronized steps
import numpy as np
from clustermessaging.Messager import Messager

m = Messager()

m.mynum = float(np.random.randint(100))
print('My num: %d' % m.mynum)

m.registerCallbackSync()
m.start()

for iter in range(3):
    for neighbor in m.getNeighbors().keys():
        message = {
            'num': m.mynum,
            'sync': iter
        }

        m.sendMessage(neighbor, message)
        print('sent to %s' % neighbor)

    print('Waiting on all neighbors...')
    m.waitForMessageFromAllNeighbors(iter)

    print('Printing all messages')
    for message in m.sync[iter]:
        print(message)

print('done')
