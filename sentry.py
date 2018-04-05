#!/usr/bin/env python3.6

import sys
from serial import Serial
from time import sleep


hello = b'''\r\nGrbl 1.1f ['$' for help]\r\n'''
ok = b'''ok\r\nok\r\n'''


class Sentry(object):
    def __init__(self, tty, baudrate):
        self._serial = Serial(tty, baudrate)

        b = b''
        while b != hello:
            b += self._serial.read_all()

        self.x_rate = 5000
        self.y_rate = 4000
        self.x_acc  = 1000
        self.y_acc  = 1000

        self._feed_rate = 9000


    def __del__(self):
        self._serial.close()


    def jog(self, x, y):
        self.send(f'$J=G91 G21 X{x} Y{y} F{self._feed_rate}')


    def send(self, cmd):
        self._serial.write(f'{cmd}\r\n'.encode('ascii'))


        code = b''
        while code != ok:
            code += self._serial.read_all()


    def recv(self):
        return self._serial.read_all()


    @property
    def x_rate(self):
        return self._x_rate

    @x_rate.setter
    def x_rate(self, rate):
        self._x_rate = rate
        self.send(f'$110={rate}')


    @property
    def y_rate(self):
        return self._y_rate

    @y_rate.setter
    def y_rate(self, rate):
        self._y_rate = rate
        self.send(f'$111={rate}')


    @property
    def x_acc(self):
        return self._x_acc

    @x_acc.setter
    def x_acc(self, acc):
        self._x_acc = acc
        self.send(f'$120={acc}')


    @property
    def y_acc(self):
        return self._y_acc

    @y_acc.setter
    def y_acc(self, acc):
        self._y_acc = acc
        self.send(f'$121={acc}')




if __name__ == '__main__':
    if sys.version_info < (3, 6):
        sys.exit('Python 3.6 or later is required.\n')

    sentry = Sentry('/dev/ttyACM0', 115200)

    for _ in range(5):
        for _ in range(50):
            sentry.jog(1, 1)

        for _ in range(50):
            sentry.jog(-1, -1)

