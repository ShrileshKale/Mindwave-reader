import time
import bluetooth
import subprocess
import os
import struct
import collections
import requests
import json
import numpy as np
import threading
import g_var
import RPi.GPIO as GPIO 
from MindwaveDataPoints import RawDataPoint
from MindwaveDataPointReader import MindwaveDataPointReader
from MindwaveMobileRawReader import MindwaveMobileRawReader
from MindwavePacketPayloadParser import MindwavePacketPayloadParser
from threading import Timer
from threading import Thread
from bl_rssi import BluetoothRSSI
Game_Time = 1
timer_1 = 40
timer_2 = 38
timer_3 = 36
threshold_1 = 32
threshold_2 = 29
threshold_3 = 26
threshold_4 = 22
play_av = 13
training = 11
startButton = 10
parking = 8
stop = 31
limit_switch_1 = 35
limit_switch_2 =37
rpm_relay = 23
direction_relay = 24
on_off_relay = 19
setupInputPins = [40,38,36,32,29,26,22,13,11,10,8,31,35,37]
setupOutputPins = [3,5,7,23,24,19]
BASE_URL = "http://192.168.1.101:8000/"
API_ENDPOINT = BASE_URL + "mind/data/player1"
#TRAINING_API_ENDPOINT = "http://192.168.1.107:7500/mind/training/data/player1"
#pingFlag = True
dummy_flag = {}
Avg_Attentation_Value = 0
Threshold = 100
Th_L3 = 0
Game_Time_Flag = 0
Training_Time_Flag = False
Avg_Attentation_Value = 0
av_flag = 0
ci = 0
bit0 = 0
bit1 = 0
bit2 = 0
bits_array = [0] * 3
ct = 0
ten_Sec_Flag = False
threshold = 50
temp_1 = 0
trap = 0
AV_trap = 0
Mode = 'Attention'
attentation_avg = [0] * 3
table = {}
startFlag = 0
l = 0
g_var.time_over = True
ct = 0
i = 0
k = 0
send_data_flag = True
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

for pin in setupInputPins:
    GPIO.setup(pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)

for pin in setupOutputPins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin,GPIO.LOW)

def audioVideoButton(self):
    global av_flag
    av_flag = 1

def startInterrupt(self):
    global startFlag 
    startFlag = 1

def trainingInterrupt(self):
    global Training_Time_Flag 
    Training_Time_Flag = True

GPIO.add_event_detect(play_av, GPIO.BOTH, callback=audioVideoButton, bouncetime=1000)   #interrupt for play video file
GPIO.add_event_detect(startButton, GPIO.BOTH, callback=startInterrupt, bouncetime=1000)   #interrupt for play video file
GPIO.add_event_detect(training, GPIO.BOTH, callback=trainingInterrupt, bouncetime=1000)   #interrupt for play video file

while True:
    try:
        global pingFlag
        pingFlag = True
        response = requests.get(url = BASE_URL + "ping/server", headers={'Content-Type':'application/json', 'Accept':'application/json'}).json()["status"]
        if (response):
            break
            pingFlag = False
    except:
        print ("Server not found")
        pingFlag = True
print 'got server'
data = {
    "type" : "wifi",
    "player_id" : "player_one",
    "connectivity" : True
}
dummy_flag = str(requests.post(url = BASE_URL + "title/controls", headers= {'Content-Type' : 'application/json', 'Accept' : 'application/json' },data = json.dumps(data)).text)
data_logs = {
    "player_id": "player_one",
    "game": "spirograph"
    }

response = requests.post(url = BASE_URL + "initialize", json =data_logs)
data = response.json()
print data
g_var.BL_Address = data['headset_id']
print('got bl add')
print (g_var.BL_Address)






if __name__ == '__main__':

    try:
        mindwaveDataPointReader = MindwaveDataPointReader()
        mindwaveDataPointReader.start()
        BL_strength = BluetoothRSSI(g_var.BL_Address)
        print BL_strength
        print 'connected successfull'
    
    except Exception as e:
        print 'Not connected'
    data = {
        "type" : "bluetooth",
        "player_id" : "player_one",
        "connectivity" : True
    }
    dummy_flag = str(requests.post(url = BASE_URL + "title/controls", headers= {'Content-Type' : 'application/json', 'Accept' : 'application/json' },data = json.dumps(data)).text)

    while(True):
        av_flag = 1
        while(av_flag):
            print "inside waiting for Av or shutdown"
            av_flag  = 0
            if (GPIO.input(play_av) == 0):    #IF AV IS PRESEED
                time.sleep(0.01)
                if(GPIO.input(play_av) == 0):
                    # AV_Flag = 1
                    data_logs = {
                                "type" : "control",
                                "message" : "turn on av",
                                "turn_on_av" : True
                            }
                    print("in AV")
                    response = requests.post(url = BASE_URL + "title/controls", json = data_logs)
                    print response
                    trap = 1
            elif(GPIO.input(stop) == GPIO.LOW):     # IF STOP IS PRESSED FOR SHUTDOWN
                time.sleep(3)
                if(GPIO.input(stop) == GPIO.LOW):
                    subprocess.call(['sudo','shutdown', '-h', 'now'])

        while(trap):
            global trap, ct, i ,k
            print('in trap')
            Bts_1_Vl = BL_strength.get_rssi()
             
            data_logs = {
                "bts_1_vl" : Bts_1_Vl + 100,
                "player" : "player1"
            }
            response = requests.post(url = BASE_URL + "ready/data/player1", json = data_logs)
            print response

            g_var.time_over = True
            for ct in range(3):
                attentation_avg[ct] = 0  

            if(GPIO.input(40) == GPIO.LOW):
                 Game_Time = 1
            elif(GPIO.input(38) == GPIO.LOW):
                 Game_Time = 2
            elif(GPIO.input(36) == GPIO.LOW):
                 Game_Time = 3
            else:
                Game_Time = 4

            if(GPIO.input(limit_switch_1) == 1):
                print "Attention"
                Mode = "Concentration"
            elif(GPIO.input(limit_switch_2) == 1):
                print "Meditatio"
                Mode = "Relaxation"

            ct = 0
            i = 0
            k = 0
            l = 0
            
            
            for ct in range(3):
                attentation_avg[ct] = 0            
            Avg_Attentation_Value = 0

            if (GPIO.input(training) == 0 ):
                data = {
                        "type" : "control",
                        "mode" : "training",
                        "set_timer_at" : 1
                    }
                response = requests.post(url = BASE_URL + "ready/controls", json = data)


                ten_Sec_Flag = False    
                while(not ten_Sec_Flag):
                    print "inside Counter Flag"
                    Flag_json = str(requests.get(url = BASE_URL + "timerstatus", headers= {'Content-Type' : 'application/json', 'Accept' : 'application/json' }).text)
                    Flag_json = json.loads(Flag_json)
                    ten_Sec_Flag = Flag_json["training_flag"]
                    time.sleep(0.5)
                
                send_data_flag = True
                print('got Training Start flag')
                mindwaveDataPointReader.go()
                while send_data_flag:  
                    Bts_1_Vl = BL_strength.get_rssi()  
                    dataPoint1 = mindwaveDataPointReader.readNextDataPoint()
                    if (not dataPoint1.__class__ is RawDataPoint):
                        k += 1
                        if (k== 4):
                            k = 0
                            print "inside Training Mode"

                            if Mode == "Concentration":
                                print Mode
                                attentation_avg[i] = g_var.attentation_val 
                            elif Mode == "Relaxation":
                                print Mode
                                attentation_avg[i] = g_var.meditation_val 
                            i += 1
                            if (i == 3):
                                i = 0
                            Avg_Attentation_Value = sum(attentation_avg) / len(attentation_avg)
                            print("player1 = ", Avg_Attentation_Value)
                            data_logs = {
                                        "value_of" : Mode,
                                        "bts_1_vl" : Bts_1_Vl + 100,
                                        "atn_1_vl" : Avg_Attentation_Value,
                                        "psl_1_vl" : g_var.PSL,
                                        "skin_contact_1" : g_var.skin_contact_error_flag
                                    }
                            response = requests.post(url = BASE_URL + "training/data", json=data_logs)
                            print response.json()
                            res = response.json()
                            send_data_flag = res["training_flag"]
                            print "PLAYER 1: ",Avg_Attentation_Value

            elif (startFlag and GPIO.input(startButton) == 0 ):
                trap = 0 
                startFlag = 0
                data = {
                        "type" : "control",
                        "message" : "turn on timer",
                        "mode" : "Timer",
                        "turn_on_timer" : True,
                        "set_timer_at" : Game_Time
                    }
                response = requests.post(url = BASE_URL + "ready/controls", json = data)


                ten_Sec_Flag = False    
                while(not ten_Sec_Flag):
                    print "inside Counter Flag"
                    Flag_json = str(requests.get(url = BASE_URL + "timerstatus", headers= {'Content-Type' : 'application/json', 'Accept' : 'application/json' }).text)
                    Flag_json = json.loads(Flag_json)
                    ten_Sec_Flag = Flag_json["timer_flag"]
                    time.sleep(0.5)
                
                send_data_flag = True
                print('got Start flag')
                mindwaveDataPointReader.go()
                while send_data_flag:  
                    Bts_1_Vl = BL_strength.get_rssi()  
                    dataPoint1 = mindwaveDataPointReader.readNextDataPoint()
                    if (not dataPoint1.__class__ is RawDataPoint):
                        k += 1
                        if (k== 4):
                            k = 0  
                            if Mode == "Concentration":
                                print Mode
                                attentation_avg[i] = g_var.attentation_val 
                            elif Mode == "Relaxation":
                                print Mode
                                attentation_avg[i] = g_var.meditation_val 
                            i += 1
                            if (i == 3):
                                i = 0
                            Avg_Attentation_Value = sum(attentation_avg) / len(attentation_avg)
                            print("player1 = ", Avg_Attentation_Value)
                            data_logs = {
                                        "value_of" : Mode,
                                        "bts_1_vl" : Bts_1_Vl + 100,
                                        "atn_1_vl" : Avg_Attentation_Value,
                                        "psl_1_vl" : g_var.PSL,
                                        "skin_contact_1" : g_var.skin_contact_error_flag
                                    }
                            response = requests.post(url = BASE_URL + "data", json=data_logs)
                            print response.json()
                            res = response.json()
                            send_data_flag = res["timer_flag"]
                            print "PLAYER 1: ",Avg_Attentation_Value

                GPIO.output(19, GPIO.LOW)
                print("exited")
                print(g_var.time_over)
                #GPIO.output(23, GPIO.HIGH)
                time.sleep(0.01)
                GPIO.output(24, GPIO.HIGH)
                time.sleep(0.01)
                GPIO.remove_event_detect(31)
                
                
                while(GPIO.input(31) == GPIO.HIGH):
                    time.sleep(0.01)
                    print "inside wait for parking"
                
                #GPIO.output(23, GPIO.HIGH)
                #GPIO.output(24, GPIO.HIGH)
                GPIO.output(19, GPIO.HIGH)
                time.sleep(1)
                
                data = {
                            "type" : "control",
                            "message" : "parking",
                            "parking" : True                        
                        }
                dummy_flag = requests.post(url = BASE_URL + "analysis/controls", headers= {'Content-Type' : 'application/json', 'Accept' : 'application/json' }, data = json.dumps(data))
                print("parking")
        











        

                    


       
       


    
