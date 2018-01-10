#!/usr/bin/python3
#coding: utf-8

import jtalk
import socket
import xml.etree.ElementTree as ET
import pigpio
import time
import threading
import random
import subprocess
import cv2
import numpy as np
import re

#sudo pigpiodをしてから実行

servo_pin = 4
servo_pin2 = 18
START_V = 500 # us
END_V = 2400 # us
list = [0, 1, 2]
ang = [60, 0, -60]

pi1 = pigpio.pi()

x0 = 170
y0 = 80
height = 400
width = 300

skinkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

start_voice = 'よろしくおねがいします'
start_voice = start_voice.encode('utf-8')
end_voice = 'おつかれさまでした'
end_voice = end_voice.encode('utf-8')
win_voice = 'わたしのかちだよ'
win_voice = win_voice.encode('utf-8')
lose_voice = 'あなたのかちだよ'
lose_voice = lose_voice.encode('utf-8')
senkou = 'あなたのたーんよ'
senkou = senkou.encode('utf-8')
koukou = 'わたしのたーんよ'
koukou = koukou.encode('utf-8')
text0 = 'いっせーのーで%s' % list[0] 
text0 = text0.encode('utf-8') #str to byte
text1 = 'いっせーのーで%s' % list[1] 
text1 = text1.encode('utf-8') #str to byte
text2 = 'いっせーのーで%sー' % list[2] 
text2 = text2.encode('utf-8') #str to byte
what = 'なんですか'
what = what.encode('utf-8')
mada = 'まだまだね'
mada = mada.encode('utf-8')
nakanaka = 'なかなかやるわね'
nakanaka = nakanaka.encode('utf-8')
goodjob = 'いいかんじー'
goodjob = goodjob.encode('utf-8')
zannen = 'ざんねんね'
zannen = zannen.encode('utf-8')
nini = 'にーたいにだよ'
nini = nini.encode('utf-8')
niiti = 'にーたいいちだよ'
niiti = niiti.encode('utf-8')
itini = 'いちたいにだよ'
itini = itini.encode('utf-8')
itiiti = 'いちたいいちだよ'
itiiti = itiiti.encode('utf-8')


human_state = 2 #number of human's thumb
robo_state = 2 #number of robot's thumb
turn = 0 #0:human turn 1:robo turn
human_point = 0
robo_point = 0
last_said = start_voice #last word robo said

def get_pulsewidth(ang):
    ang += 90.0
    if ang < 0.0:
        ang = 0.0
    if ang > 180.0:
        ang = 180.0
    w = (END_V - START_V) * (float(ang) / 180.0) + START_V
    return w

def skinMask(frame, x0, y0, width, height):
    global skinkernel
    #HSV values of skin color
    low_range = np.array([0, 50, 80])
    upper_range = np.array([30, 200, 255])
    cv2.rectangle(frame, (x0,y0),(x0+width,y0+height),(0,255,0),1)
    roi = frame[y0:y0+height, x0:x0+width] 
    #convert BGR to HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV) 
    #threshold the HSV image to get only skin colors
    mask = cv2.inRange(hsv, low_range, upper_range)
    #収縮処理(カーネルのサイズに依存して物体の境界付近の全画素が白1から黒0になる)
    mask = cv2.erode(mask, skinkernel, iterations = 1)
    #膨張処理(逆に画像中の白色領域を増やす)
    mask = cv2.dilate(mask, skinkernel, iterations = 1)
    #ガウシアンフィルタ
    mask = cv2.GaussianBlur(mask, (15,15), 1)
    #cv2.imshow("Blur", mask)
    #bitwise and mask original frame
    res = cv2.bitwise_and(roi, roi, mask = mask)
    # color to grayscale
    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    return res

def center(frame):
    hadairo = skinMask(frame, x0, y0, width, height)
    hadairo2 = skinMask(frame, x0, y0, width, int(height/2))
    mu = cv2.moments(hadairo, False)
    mu2 = cv2.moments(hadairo2, False)
    return hadairo,hadairo2,mu["m00"],mu2["m00"]

def main():
    global x0,y0,width,height,skinkernel
    global human_state,robo_state,turn,human_point,robo_point,last_said
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    host = '127.0.0.1' #IPaddress
    port = 10500 #default
    p = subprocess.Popen(["bash start-julius.sh"], stdout=subprocess.PIPE, shell=True)
    pid = str(p.stdout.read().decode('utf-8'))
    time.sleep(2)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port)) #音声認識待ち状態になって認識結果をXMLで投げる

    #XML解析
    try:
        data = ''
        while(1):
            ret, frame = cap.read()
            hadairo,hadairo2,area,area2 = center(frame)
            #cv2.imshow("frame",frame)
            cv2.imshow("hadairo",hadairo)
            cv2.imshow("hadairo2",hadairo2)
            cv2.waitKey(1)
            print("{} {}".format(area,area2))

            if '</RECOGOUT>\n.' in data:
                r_data = data.replace('\n', '@@@')
                r = re.compile("(.*)(/RECOGOUT)(.*)")
                m = r.match(r_data)
                if m != None:
                    a = m.group(1)
                    data = a.replace('@@@', '\n') + '/RECOGOUT>\n.'
                root = ET.fromstring('\n' + data[data.find('<RECOGOUT>'):].replace('\n.', ''))
                print(root)
                for whypo in root.findall('./SHYPO/WHYPO'):
                    command = whypo.get('WORD') #認識した単語
                    score = float(whypo.get('CM')) #信頼度
                    if command == u'いきます' and score >= 0.95 and turn == 0:
                        time.sleep(1.0)
                        if robo_state == 2:
                            n = random.randint(0,4)
                        elif robo_state == 1:
                            n = random.randint(0,2)

                        if n == 3 or n == 4:
                            print ("two robo-fingers are raised")
                            pi1.set_servo_pulsewidth(servo_pin, get_pulsewidth(ang[0]))
                            pi1.set_servo_pulsewidth(servo_pin2, get_pulsewidth(ang[0]))
                            time.sleep(2)
                            pi1.set_servo_pulsewidth(servo_pin, get_pulsewidth(ang[2]))
                            pi1.set_servo_pulsewidth(servo_pin2, get_pulsewidth(ang[2]))
                        elif n == 1:
                            print ("one robo-finger is raised")
                            pi1.set_servo_pulsewidth(servo_pin, get_pulsewidth(ang[0]))
                            time.sleep(2)
                            pi1.set_servo_pulsewidth(servo_pin, get_pulsewidth(ang[2]))
                        elif n == 2:
                            print ("one robo-finger is raised")
                            pi1.set_servo_pulsewidth(servo_pin2, get_pulsewidth(ang[0]))
                            time.sleep(2)
                            pi1.set_servo_pulsewidth(servo_pin2, get_pulsewidth(ang[2]))
                        else:
                            print ("robo-finger is not raised")    
                        time.sleep(2)
                        

                    elif command == u'どうぞ' and score >= 0.95 and turn == 1:
                        time.sleep(1)
                        jtalk.jtalk(koukou)
                        time.sleep(2)
                        if human_state == 2:
                            n = random.randint(0,2)
                        elif human_state == 1:
                            n = random.randint(0,1)

                        if n == 2:
                            jtalk.jtalk(text2)
                            last_said = text2
                            #time.sleep(2)
                            continue
                        elif n == 1:
                            jtalk.jtalk(text1)
                            last_said = text1
                            #time.sleep(2)
                            continue
                        else:
                            jtalk.jtalk(text0)
                            last_said = text0
                            #time.sleep(2)
                            continue

                    elif command == u'はんていして' and score >= 0.95:
                        if turn == 0:
                            #human turn 終了時
                            if (area>5000000 and human_state==2) or (area>100000 and human_state==1): 
                                jtalk.jtalk(mada)
                                time.sleep(2)
                                jtalk.jtalk(nini)
                            elif (area<=5000000 and human_state==2):
                                jtalk.jtalk(nakanaka)
                                human_state = 1
                                time.sleep(2)
                                if robo_state==2:
                                    jtalk.jtalk(niiti)
                                elif robo_state==1:
                                    jtalk.jtalk(itiiti)
                            else:
                                jtalk.jtalk(lose_voice)
                                human_state = 0
                            turn = 1
                            continue
                        else:
                            #robo turn 終了時
                            if robo_state==2:
                                if last_said==text2:
                                    if area2>=1500000:
                                        jtalk.jtalk(goodjob)
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(itini)
                                        robo_state = 1
                                    else:
                                        jtalk.jtalk(zannen)
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(nini)
                                        elif human_state==1:
                                            jtalk.jtalk(niiti)
                                elif last_said==text1:
                                    if area2>=500000 and area2<1500000:
                                        jtalk.jtalk(goodjob)
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(itini)
                                        elif human_state==1:
                                            jtalk.jtalk(itiiti)
                                        robo_state = 1
                                    else:
                                        jtalk.jtalk(zannen)
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(nini)
                                        elif human_state==1:
                                            jtalk.jtalk(niiti)
                                elif last_said==text0:
                                    if area2<500000:
                                        jtalk.jtalk(goodjob)
                                        robo_state = 1
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(itini)
                                        elif human_state==1:
                                            jtalk.jtalk(itiiti)
                                    else:
                                        jtalk.jtalk(zannen)
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(nini)
                                        elif human_state==1:
                                            jtalk.jtalk(niiti)
                            elif robo_state==1:
                                if last_said==text2:
                                    if area2>=1500000:
                                        jtalk.jtalk(win_voice)
                                        robo_state = 0
                                    else:
                                        jtalk.jtalk(zannen)
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(itini)
                                        elif human_state==1:
                                            jtalk.jtalk(itiiti)
                                elif last_said==text1:
                                    if area2>=500000 and area2<1500000:
                                        jtalk.jtalk(win_voice)
                                        robo_state = 0
                                    else:
                                        jtalk.jtalk(zannen)
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(itini)
                                        elif human_state==1:
                                            jtalk.jtalk(itiiti)
                                elif last_said==text0:
                                    if area2<500000:
                                        jtalk.jtalk(win_voice)
                                        robo_state = 0
                                    else:
                                        jtalk.jtalk(zannen)
                                        time.sleep(2)
                                        if human_state==2:
                                            jtalk.jtalk(itini)
                                        elif human_state==1:
                                            jtalk.jtalk(itiiti)
                        
                            turn = 0
                            continue

                    elif command == u'ねーねー' and score >= 0.95:
                        jtalk.jtalk(what)
                    elif command == u'よろしく' and score >= 0.95:
                        jtalk.jtalk(start_voice)
                    elif command == u'おしまい' and score >= 0.95:
                        jtalk.jtalk(end_voice)
                        #time.sleep(2)
                        #p.kill()
                        #client.close()
                    time.sleep(2)
                data = ''

            else:
                byte_recv = client.recv(1024)
                data = data + byte_recv.decode('utf-8')
                print(data)
                

            print("turn:{} human_state:{} robo_state:{}".format(turn,human_state,robo_state))
            
            if robo_state==0 or human_state==0:
                time.sleep(2)
                jtalk.jtalk(end_voice)
                p.kill()
                client.close()
                
    except KeyboardInterrupt:
        p.kill()
        subprocess.call(["kill "+pid], shell=True)
        client.close()

    pi1.stop()

     # 終了処理
    cv2.destroyAllWindows()
    cap.release()

if __name__ == '__main__':
    main()