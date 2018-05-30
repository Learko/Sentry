#!/usr/bin/env python3.6

import sys
from serial import Serial
from time import sleep
from math import tan, atan, radians, degrees
from threading import Thread, Lock
from copy import deepcopy

import cv2


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
        self.x_acc  = 100
        self.y_acc  = 100

        self._feed_rate = 9000


    def __del__(self):
        self._serial.close()


    def jog(self, x, y):
        # self.reset()
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


    def idle(self):
        code = b''

        while not code.startswith(b'<Idle'):
            self._serial.write(b'?\r\n')
            code = b''

            while not code.endswith(b'ok\r\n'*2):
                code += self._serial.read_all()

    def reset(self):
        self._serial.write(f'{chr(0x18)}'.encode('ascii'))

        code = b''
        while code != hello:
            code += self._serial.read_all()

            if code:
                print(code)




class Camera(object):
    def __init__(self, id=1):
        self.id = id
        self.video_capture = cv2.VideoCapture(self.id)
        self.size = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH), self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self._frame = None
        # self._lock = Lock()
        self._stop = False

        self.update_thread = Thread(target=self._update, args=(), daemon=True)
        self.update_thread.start()

    def __del__(self):
        self._stop = True


    def _update(self):
        while not self._stop:
            # with self._lock:
            ret, self._frame = self.video_capture.read()


    @property
    def frame(self):
        # with self._lock:
        frame = deepcopy(self._frame)

        return frame




if __name__ == '__main__':
    if sys.version_info < (3, 6):
        sys.exit('Python 3.6 or later is required.\n')

    sentry = Sentry('/dev/ttyACM0', 115200)

    face_casc_path = 'haarcascades/haarcascade_frontalface_default.xml'
    eye_casc_path = 'haarcascades/haarcascade_eye.xml'
    left_eye_casc_path = 'haarcascades/haarcascade_lefteye_2splits.xml'
    right_eye_casc_path = 'haarcascades/haarcascade_righteye_2splits.xml'


    face_casc = cv2.CascadeClassifier(face_casc_path)
    eye_casc = cv2.CascadeClassifier(eye_casc_path)
    left_eye_casc = cv2.CascadeClassifier(left_eye_casc_path)
    right_eye_casc = cv2.CascadeClassifier(right_eye_casc_path)

    cam = Camera()
    cw, ch = cam.size

    while cam.frame is None:
        pass

    while True:
        frame = cam.frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_casc.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(40, 40),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        confirmed_faces = set()

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_frame = frame[y:y+h, x:x+w]

            eyes = right_eye_casc.detectMultiScale(
                roi_gray
            )

            if len(eyes) >= 2:
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_frame, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                confirmed_faces.add((x, y, w, h))


        cv2.imshow('Video', frame)


        if len(confirmed_faces) > 0:
            x, y, w, h = min(faces, key=lambda f: (w/2 - f[0])**2 + (h/2 - f[1])**2) # closest to center
            # x, y, w, h = max(confirmed_faces, key=lambda f: f[2]*f[3]) # biggest

            x += w/2
            y += h/2

            shift_x = cw/2 - x
            shift_y = ch/2 - y

            jx = 0
            jy = 0

            if abs(shift_x) > 10:
                jx = round(degrees(atan(2 * shift_x * tan(radians(65))/cw)) / 3.5, 4)
            if abs(shift_y) > 10:
                jy = round(degrees(atan(2 * shift_y * tan(radians(65))/ch)) / 4, 4)


            if jx != 0 or jy != 0:
                # print(jx, jy)
                sentry.jog(*map(int, (jx, jy)))
                sentry.idle()


        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            quit()
