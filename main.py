# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import logging
import subprocess
import sys
import time
from enum import Enum
from threading import Thread


class LedState(Enum):
    INIT = -1
    OK = 0
    ERROR = 200
    BUSY = 500


class Led:
    def __init__(self, pin: int):
        self._pin = pin
        self._logger = logging.getLogger()
        self._logger.debug(f"Led {self._pin} init")
        self.state: LedState = LedState.INIT
        self.run: bool = True
        self.thread = Thread(target=self.worker)
        self.thread.start()

    def __del__(self):
        self.run = False
        self.thread.join()

    def worker(self):
        while self.run:
            if self.state is not LedState.INIT:
                self._logger.debug(f"LED {self._pin} toggle")
            if self.state.value < LedState.ERROR.value:
                time.sleep(0.1)
            else:
                time.sleep(self.state.value/1000)


class Recorder:
    def __init__(self, device: str, mount_led: Led, rec_led: Led):
        self._dev = f"/dev/{device}"
        self._mount = f"/media/{device}"
        self._logger = logging.getLogger()
        self._mount_led = mount_led
        self._rec_led = rec_led

    def start(self):
        self._mount_led.state = LedState.BUSY
        try:
            subprocess.check_call(["/usr/sbin/fsck", "-p", self._dev])
            subprocess.check_call(["/usr/bin/mkdir", self._mount])
            subprocess.check_call(["/usr/bin/mount", self._dev, self._mount])
        except Exception as e:
            self._mount_led.state = LedState.ERROR
            raise e

        try:
            filename = f"{self._mount}/{time.strftime('%d.%m.%Y_%H:%M')}.wav"
            rec = subprocess.Popen(["/usr/bin/rec", "-d", filename])
            time.sleep(0.5)
            self._rec_led.state = LedState.BUSY
        except Exception as e:
            self._rec_led.state = LedState.ERROR
            raise e


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise AttributeError("Block device name is expected as the only argument")
    dev = sys.argv[1]
    l1 = Led(23)
    l2 = Led(24)
    r = Recorder(dev, l1, l2)
    r.start()

