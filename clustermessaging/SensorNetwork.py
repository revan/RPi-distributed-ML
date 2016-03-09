import time

from clustermessaging.Messager import Messager

class SensorNetwork(Messager):
    """
    An extension of Messager for tasks involving sensors.
    To use, call startProcessing() and supply a processing function,
    a callback function, a sesnor function, an optional stop function,
    and an optional
    """
    def registerSensor(self, sensorFunction):
        """
        Register
        :param sensorFunction: function taking no parameters
        :param delay: function returning delay in seconds between calls. defaults to only running once.
        :return: sensor value (type agnostic)
        """
        self.sensorFunction = sensorFunction

    def registerStopCondition(self, stopConditionFunction):
        self.stopConditionFunction = stopConditionFunction

    def startProcessing(
            self,
            processingFunction,
            callbackFunction,
            sensorFunction,
            stopConditionFunction=lambda: True,
            delay=None):
        """
        :param processingFunction: (sensorValue)->()
        :param callbackFunction:  (message, name)->()
        :param sensorFunction: ()->(sensorValue) called once per process,
            returns a value (type agnostic)
        :param stopConditionFunction: ()->(boolean) called once per process
            to determine whether to continue. Defaults to run only once.
        :param delay: ()->(int) called once per process to determine how
            long to sleep in seconds. Defaults to no sleeping.
        """
        self.registerCallback(callbackFunction)
        self.registerSensor(sensorFunction)
        self.registerStopCondition(stopConditionFunction)
        self.start()
        while True:
            if delay:
                sleep = delay()
                print('sleeping for %d seconds...' % sleep)
                time.sleep(sleep)

            processingFunction(self.sensorFunction())

            if self.stopConditionFunction():
                break