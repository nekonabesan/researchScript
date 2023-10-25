import csv
import json
import math
import time
import control
import requests
import datetime
import threading
import numpy as np
import pandas as pd
import sympy as sp
import matplotlib.pyplot as plt


from control.matlab import *
from scipy.integrate import odeint

V_MAX = 100
V_MIN = -100

url = 'http://127.0.0.1:8000'
g = 9.8
l = 0.23
M = 1.2
mu = 1.5e-2
J = 1.0e-2

P = tf([0, 1], [J, mu, M*g*l])

Kp = 0.1
ref = 0

# APIのパスを設定
url = 'http://192.168.1.129:8000'
# モーターの絶対位置を返すメソッド
get_aposition = '/motors/get_aposition/get/'
# リセット位置を基準としたモーターの位置を返すメソッド
get_position = '/motors/get_position/get/'
# モータの角速度を返すメソッド
get_dps = '/motors/dps/get/'
# モータにデューティ比を指示するメソッド
set_motor_pwm_value = '/motors/pwm_value/set/'#{motor_id}/{pwm_value}
#モータ２基に同時にデューティ比を設定するメソッド
set_motors_pwm_value = '/motors/pwm_value/set/pare/'#{pwm_value}
# モータへ回転角度を指示
set_run_for_degree = '/motors/run_for_degrees/set/'#{motor_id}/{degree}/{pwm_value}/{blocking}/
# モータ2基へ回転角度を指示
set_pare_run_for_degree = '/motors/run_for_degrees/set/pare/'#{degree}/{pwm_value}/{blocking}


def getAposition():
    r = requests.get(url + get_aposition + '', params={})
    aposition = json.loads(r.text)
    return aposition[0]

def getPosition():
    r = requests.get(url + get_position + '', params={})
    position = json.loads(r.text)
    return position[0]

def getDps():
    r = requests.get(url + get_dps + '', params={})
    dps = json.loads(r.text)
    return dps[0]

def setMotorsPwmValue(pwm_value):
    r = requests.get(url + set_motors_pwm_value + str(pwm_value), params={})
    motors_pwm_value = json.loads(r.text)
    return motors_pwm_value[0]

result = [['pwm_value', 'gyro_angle' ,'gyro_dps'
            ,'motor_a_dps', 'motor_b_dps'
            ,'befor_motor_a_count_per_m', 'after_motor_a_count_per_m'
            ,'befor_motor_b_count_per_m', 'after_motor_b_count_per_m'
            ,'befor_motor_a_full_travel_count', 'after_motor_a_full_travel_count'
            ,'befor_motor_b_full_travel_count', 'after_motor_b_full_travel_count'
            ,'befor_motor_a_position', 'after_motor_a_position'
            ,'befor_motor_b_position', 'after_motor_b_position'
            ,'delta']]
#dt_now = datetime.datetime.now()
#file_name = 'data_' + str(dt_now.year) + str(dt_now.month) + str(dt_now.day) + str(dt_now.hour) + str(dt_now.min) + str(dt_now.microsecond) + '.csv'
#fp = open(file_name, 'w')
#writer = csv.writer(fp)



dt = 0
pre_dt = 0
now = time.time()
pre = None
pwm_value = 20
for index in range(100):
    #----------------------------------#
    pre = now
    aposition = getAposition()
    position = getPosition()
    dps = getDps()
    #motors_pwm_value = setMotorsPwmValue(pwm_value)
    pwm_value = -1 * pwm_value 
    print(dt)
    #
    index = index + 1
    pre_dt = dt
    now = time.time()
    dt = now - pre
    #----------------------------------#
#writer.writerows(result)
#fp.close()
