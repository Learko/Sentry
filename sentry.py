#!/usr/bin/env python3

import sys
from serial import Serial
from time import sleep


class Sentry(object):
    def __init__(self, tty, baudrate):
        self._serial = Serial(tty, baudrate)

        self.x_rate = 1000
        self.y_rate = 1000
        self.x_acc  = 40
        self.y_acc  = 40

        self._feed_rate = 9000


    def __del__(self):
        self._serial.close()


    def jog(self, x, y):
        self.send(f'$J=G91 G21 X{x} Y{y} F{self._feed_rate}')


    def send(self, cmd):
        while not self._serial.in_waiting:
            print('1'*80)

        self._serial.write(f'{cmd}\r\n'.encode('ascii'))

        while not self._serial.in_waiting:
            print('2'*80)

        self._serial.write(f'$$\r\n'.encode('ascii'))

        while not self._serial.in_waiting:
            print('3'*80)

        for l in self._serial.read_all().decode().split('\r\n'):
            print(l)

    def recv(self):
        return self._serial.read_all()


    @property
    def x_rate(self):
        return self._x_rate

    @x_rate.setter
    def x_rate(self, rate):
        self._x_rate = rate
        self.send(f'$110={rate}')

        print(f'Setting x_rate: {rate}')


    @property
    def y_rate(self):
        return self._y_rate

    @y_rate.setter
    def y_rate(self, rate):
        self._y_rate = rate
        self.send(f'$111={rate}')

        print(f'Setting y_rate: {rate}')


    @property
    def x_acc(self):
        return self._x_acc

    @x_acc.setter
    def x_acc(self, acc):
        self._x_acc = acc
        self.send(f'$120={acc}')

        print(f'Setting x_acc: {acc}')


    @property
    def y_acc(self):
        return self._y_acc

    @y_acc.setter
    def y_acc(self, acc):
        self._y_acc = acc
        self.send(f'$121={acc}')

        print(f'Setting y_acc: {acc}')




if __name__ == '__main__':
    if sys.version_info < (3, 6):
        sys.exit('Python 3.6 or later is required.\n')

    sentry = Sentry('/dev/ttyACM0', 115200)
    sentry.jog(50, 0)
    sentry.jog(-50, 0)

