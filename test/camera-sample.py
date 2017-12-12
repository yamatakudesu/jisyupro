# -*- coding: UTF-8 -*-

import cv2
import numpy as np

# カメラからキャプチャー
cap = cv2.VideoCapture(0)

cap.set(3, 640)
cap.set(4, 480)

color = (255, 255, 255) #白 

while(True):

    # 動画ストリームからフレームを取得
    ret, frame = cap.read()

    if ret == False:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
     # 表示
    cv2.imshow("Show FLAME Image", gray) 

    # qを押したら終了。
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

