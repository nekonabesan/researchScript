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
WAIT_TIME = 0.0

url = 'http://127.0.0.1:8000'
g = 9.8
l = 0.23
M = 1.2
mu = 1.5e-2
J = 1.0e-2

P = tf([0, 1], [J, mu, M*g*l])

Kp = 9
ref = 0


list_path = "/motors/list"
r = requests.get(url + list_path, params={})
motors = json.loads(r.text)
motors = motors[0]
print(motors)

init_path = "/motors/init/"
r = requests.get(url + init_path + motors['motor_a'], params={})
print(r.text)
r = requests.get(url + init_path + motors['motor_b'], params={})
print(r.text)

get_polarity_value_path = "/motors/polarity/get/"
r = requests.get(url + get_polarity_value_path + motors['motor_a'], params={})
print(r.text)
r = requests.get(url + get_polarity_value_path + motors['motor_b'], params={})
print(r.text)

sensors_list_path = "/sensors/list"
gyro = None
r = requests.get(url + sensors_list_path, params={})
sensors = json.loads(r.text)
sensors = sensors[0]
print(sensors)

type_path = "/sensors/type/"
gyro = None
touch = None
for key in sensors:
    if sensors[key] != '' and key != 'done':
        r = requests.get(url + type_path + sensors[key], params={})
        sensor = json.loads(r.text)
        if sensor[0]['type'] == "lego-ev3-gyro":
            gyro = sensors[key]
        elif sensor[0]['type'] == "lego-ev3-touch":
            touch = sensors[key]
print(gyro)

set_mode_path = "/sensors/gyro/set/mode/"
r = requests.get(url + set_mode_path + gyro, params={})
result = json.loads(r.text)
print(result)


# 速度取得
get_pwm_value_path = "/motors/pwm_value/get/"
r = requests.get(url + get_pwm_value_path + motors['motor_a'], params={})
print(r.text)
r = requests.get(url + get_pwm_value_path + motors['motor_b'], params={})
print(r.text)

path = "/motors/count_per_rot/get/"
r = requests.get(url + path + motors['motor_a'], params={})
motor_a_cpr = json.loads(r.text)
motor_a_cpr = motor_a_cpr[0]['cpr']
print(motor_a_cpr)
r = requests.get(url + path + motors['motor_b'], params={})
motor_b_cpr = json.loads(r.text)
motor_b_cpr = motor_b_cpr[0]['cpr']
print(motor_b_cpr)

# ジャイロセンサ指示角度取得
gyro_angle_data_path = '/sensors/gyro/get/angle/'

# ジャイロセンサ指示速度取得
gyro_speed_data_path = '/sensors/gyro/get/speed/'

# 速度設定
motor_set_pwm_value_path = "/motors/pwm_value/set/"
motor_pare_set_pwm_value_path = "/motors/pwm_value/set/pare/"

# モータの角速度を取得
motor_get_dps_path = "/motors/dps/get/"

# パラメータを取得
get_parameter_path = '/sensors/parameter/get/'

def get_gyro_angle(gyro: str):
    r_angle = requests.get(url + gyro_angle_data_path + gyro, params={})
    result_angle = json.loads(r_angle.text)
    result_angle = result_angle[0]
    return result_angle['angle']

def get_gyro_speed(gyro: str):
    r_speed = requests.get(url + gyro_speed_data_path + gyro, params={})
    result_speed = json.loads(r_speed.text)
    result_speed = result_speed[0]
    return result_speed['speed']

def get_motor_dps(motors, motor_a_cpr ,motor_b_cpr):
    r_dps = requests.get(url + motor_get_dps_path + motors['motor_a'] + "/" + motors['motor_b'], params={})
    result_dps = json.loads(r_dps.text)
    result_dps = result_dps[0]
    motor_a_dps = int(result_dps['motor_a_dps'])
    motor_b_dps = int(result_dps['motor_b_dps'])
    return motor_a_dps,motor_b_dps

def get_parameters(gyro, motors):
    r_parms = requests.get(url + get_parameter_path + gyro + "/" + motors['motor_a'] + "/" + motors['motor_b'], params={})
    parameters = json.loads(r_parms.text)
    parameters = parameters[0]
    return parameters

def worker():
    #print(time.time())
    time.sleep(WAIT_TIME)

def schedule(interval, f, wait=True):
    m_a = 0
    m_a1 = 0
    m_b = 0
    m_b1 = 0
    motor_a = [0]
    err_a = 0
    err_a1 = 0 
    err_a2 = 0
    motor_b = [0]
    err_b = 1
    err_b1 = 1
    err_b2 = 1
    array_t = [0]
    base_time = time.time()
    next_time = 0
    t_time = 0
    Kp = 0.3
    Ki = 0.0
    Kd = 0.0
    Zc = 30
    index = 1
    pwm_value = -20
    #response = requests.get(url + motor_pare_set_pwm_value_path + motors['motor_a'] + "/" + motors['motor_b'] + "/" + str(pwm_value), params={})
    time.sleep(0.05)
    while True:
        t = threading.Thread(target=f)
        t.start()
        if wait:
            #----------------------------------#
            m_a1 = m_a
            m_b1 = m_b
            err_a2 = err_a1
            err_b2 = err_b1
            err_a1 = err_a
            err_b1 = err_b
            #pwm_value = -1 * pwm_value
            parameters = get_parameters(gyro, motors)
            gyro_angle = parameters['gyro_angle']
            gyro_dps = parameters['gyro_dps']
            motor_a_dps = parameters['motor_a_dps']
            motor_b_dps = parameters['motor_b_dps']
            motor_a_position = parameters['motor_a_position']
            motor_b_position = parameters['motor_a_position']
            t_time = t_time + next_time
            print(str(t_time) + "\tpwm_value : " + str(pwm_value)
                #+ "\tangle : " + str(gyro_angle) + "[deg]\t" + "speed : " + str(gyro_dps) + "[deg/s]"
                + "\tmotor_a_dps : " + str(motor_a_dps)
                + "\tmotor_b_dps : " + str(motor_b_dps)
                + "\tmotor_a_position : " + str(motor_a_position)
                + "\tmotor_b_position : " + str(motor_b_position)
                #+ "\terr_a : " + str(err_a)
                #+ "\terr_b : " + str(err_b)
                #+ "\tm_a : " + str(m_a)
                #+ "\tm_b : " + str(m_b)
            )
            # 差分を配列に格納
            #err_a = Zc - (int(motor_a_position) % 360)
            #err_b = Zc - (int(motor_b_position) % 360)
            #err_a = Zc - motor_a[index - 1]
            #err_b = Zc - motor_b[index - 1]
            # 
            #m_a = int(m_a1 + Kp * (err_a - err_a1) + Ki * err_a + Kd * ((err_a - err_a1) - (err_a1 - err_a2)))
            #m_b = int(m_b1 + Kp * (err_b - err_b1) + Ki * err_b + Kd * ((err_b - err_b1) - (err_b1 - err_b2)))
            #
            pwm_value = -1 * pwm_value
            response = requests.get(url + motor_set_pwm_value_path + motors['motor_a'] + "/" + str(pwm_value))
            response = requests.get(url + motor_set_pwm_value_path + motors['motor_b'] + "/" + str(pwm_value))
            motor_a.append(m_a)
            motor_b.append(m_b)
            index = index + 1
            #----------------------------------#
            t.join()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)

schedule(0.2, worker)

    



