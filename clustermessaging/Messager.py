import json
import zmq
import time
import sys
import os
import pickle
import threading

import logging
logging.basicConfig(level=logging.WARNING)

from kazoo.client import KazooClient

from zmq.eventloop import ioloop, zmqstream

class Messager:
    def __init__(self):
        self.loop = ioloop.IOLoop.instance()
        # load topography from file
        self._loadTopography()

        self.context = zmq.Context()

        self.zk = KazooClient()
        self.zk.start(timeout=1000)

        # send own address to zookeeper
        self.zk.ensure_path("/addr")
        self.zk.create(("/addr/%s" % self.getOwnName()), bytes(self.getOwnAddr(), "UTF-8"))

        # get IP addresses from zookeeper
        neighbor_names = self.topo[self.getOwnName()]
        self.addresses = {}
        for name in neighbor_names:
            cv = threading.Condition()
            cv.acquire()

            def wakeup_watch(stat):
                cv.acquire()
                cv.notify()
                cv.release()

            ex = self.zk.exists(("/addr/%s" % name), wakeup_watch)
            if not ex:
                cv.wait()
            (addr, _) = self.zk.get("/addr/%s" % name)
            self.addresses[name] = addr.decode("UTF-8")

        print('Got all neighboring addresses.')

        # create PAIR connections for each network link
        self.neighbors = {}
        for name in neighbor_names:
            # lower device establishes connection to avoid duplicate
            socket = self.context.socket(zmq.PAIR)
            if int(name) > int(self.getOwnName()):
                socket.connect(self.getAddr(name))
            else:
                socket.bind('tcp://*:%d' % self._findPortFor(name))

            self.neighbors[name] = socket

    def _loadTopography(self):
        with open('topo.json') as data_file:
            self.topo = json.load(data_file)

    def _findPortFor(self, name):
        a = min(int(self.getOwnName()), int(name))
        b = max(int(self.getOwnName()), int(name))
        # Cantor pairing function
        return 9000 + (a + b) * (a + b + 1) / 2 + a

    def getOwnName(self):
        if not 'DEVICE_ID' in os.environ:
            raise RuntimeError('var DEVICE_ID not defined')

        return os.environ['DEVICE_ID']

    def getOwnAddr(self):
        # uncomment when running locally
        # return 'tcp://localhost'

        # oh god why
        import socket
        return 'tcp://%s' % [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for\
                s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]


    def getNeighbors(self):
        """
        Iterate over names with getNeighbors().keys()
        :return: the dict of names to sockets
        """
        return self.neighbors

    def getAddr(self, name):
        """
        :raises RuntimeError if network topology forbids this link
        :param name: the name to query
        :return: the address of the specified node
        """
        if name in self.addresses:
            addr = '%s:%d' % (self.addresses[name], self._findPortFor(name))
            return addr
        else:
            raise RuntimeError('No link between me and %s in topology!' % name)

    def getSocket(self, name):
        """
        :raises RuntimeError if network topology forbids this link
        :param name: the name to query
        :return: the socket between self and other node
        """
        if name in self.neighbors:
            return self.neighbors[name]
        else:
            raise RuntimeError('No link between me and %s in topology!' % name)

    def sendMessage(self, name, message):
        """
        Sends a message to a node.
        :param name: node to send to
        :param message: arbitrary python object to be sent
        """
        self.getSocket(name).send_pyobj(message)

    def registerCallbackIndividual(self, callbackFunction, name):
        """
        Register an async callback on a specific neighbor. Use registerCallback() to register on all neighbors.
        :param callbackFunction: function taking two parameters, message and name.
        :param name: neighbor we're registering on
        """
        def decorator(data):
            message = pickle.loads(b''.join(data))
            callbackFunction(message, name)

        socket = self.getSocket(name)

        self.stream = zmqstream.ZMQStream(socket, self.loop)
        self.stream.on_recv(decorator, copy=True)

    def registerCallback(self, callbackFunction):
        """
        Register an async callback on every neighbor.

        :param callbackFunction: function taking two parameters, message (arbitrary python object) and
                                 name (name of node who sent this message)
        """
        for name in self.neighbors:
            if name is not self.getOwnName():
                self.registerCallbackIndividual(callbackFunction, name)

    def start(self):
        """
        Starts the event loop in a background thread. Call this once, after having set the callback.
        """
        threading.Thread(target=self.loop.start).start()

