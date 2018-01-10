 #!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from skintest import skinMask
import jtalk
import socket
import xml.etree.ElementTree as ET
import pigpio
import time
import threading
import random
import subprocess
import re

x0 = 170
y0 = 180
height = 300
width = 300
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
prev_x = 0
prev_y = 0
skinkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))


def center(frame,prev_x,prev_y):

    hadairo = skinMask(frame, x0, y0, width, height)
    mu = cv2.moments(hadairo, False)
    if int(mu["m00"]) != 0:
        x = int(mu["m10"]/mu["m00"])
        y = int(mu["m01"]/mu["m00"])
    else:
        x = int(width / 2.0)
        y = int(height / 2.0)
    dif_x = x - prev_x
    dif_y = y - prev_y
    #cv2.circle(hadairo, (x,y), 4, 100, 2, 4)
    print("{} {} {}".format(dif_x,dif_y,mu["m00"]))

    return prev_x,prev_y,x,y,dif_x,dif_y,hadairo,mu["m00"]

if __name__ == '__main__':

    # 最初のフレームの処理

    while(1):
        ret, frame = cap.read()
        prev_x,prev_y,x,y,dif_x,dif_y,hadairo,area = center(frame,prev_x,prev_y)
        cv2.imshow("frame",frame)
        cv2.imshow("hadairo",hadairo)

        prev_x = x
        prev_y = y

        # ESCキー押下で終了
        if cv2.waitKey(30) & 0xff == 27:
            break

    # 終了処理
    cv2.destroyAllWindows()
    cap.release()