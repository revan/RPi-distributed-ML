import subprocess
import os

class LED:
    """
    Class for managing LEDs on the raspberry pi. On construction, it overloads the CPU and SD
    access indicator lights.
    """
    def __init__(self):
        if LED._onDevice():
            subprocess.call("echo gpio | sudo tee /sys/class/leds/led0/trigger", shell=True)
            subprocess.call("echo gpio | sudo tee /sys/class/leds/led1/trigger", shell=True)

    def setGreenOn(self):
        if LED._onDevice():
            LED._set(0, 1)
        else:
            print('Setting Green LED ON')

    def setGreenOff(self):
        if LED._onDevice():
            LED._set(0, 0)
        else:
            print('Setting Green LED OFF')

    def setRedOn(self):
        if LED._onDevice():
            LED._set(1, 1)
        else:
            print('Setting Red LED ON')

    def setRedOff(self):
        if LED._onDevice():
            LED._set(1, 0)
        else:
            print('Setting Red LED OFF')

    @staticmethod
    def _onDevice():
        return 'ON_DEVICE' in os.environ

    @staticmethod
    def _set(led, value):
        command = "echo %d | sudo tee /sys/class/leds/led%d/brightness" % (value, led)
        subprocess.call(command,shell=True)

