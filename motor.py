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
DELTA = 1.0

url = 'http://127.0.0.1:8000'
g = 9.8
l = 0.23
M = 1.2
mu = 1.5e-2
J = 1.0e-2

P = tf([0, 1], [J, mu, M*g*l])

Kp = 0.1
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

##def send_pulse(wait: float, pwm_value: int, motors: list):
#    r = requests.get(url + motor_pare_set_pwm_value_path + motors['motor_a'] + "/" + motors['motor_b'] + "/1", params={})
#    time.sleep(0.05)
#    r = requests.get(url + motor_pare_set_pwm_value_path + motors['motor_a'] + "/" + motors['motor_b'] + "/5", params={})
#    time.sleep(0.05)
#    r = requests.get(url + motor_pare_set_pwm_value_path + motors['motor_a'] + "/" + motors['motor_b'] + "/" + str(pwm_value), params={})
#    time.sleep(wait)
#    r = requests.get(url + motor_pare_set_pwm_value_path + motors['motor_a'] + "/" + motors['motor_b'] + '/0', params={})

def get_parameters(gyro, motors):
    r_parms = requests.get(url + get_parameter_path + gyro + "/" + motors['motor_a'] + "/" + motors['motor_b'], params={})
    parameters = json.loads(r_parms.text)
    parameters = parameters[0]
    return parameters

def get_experimental_result(pwm_value, gyro, motors, result):
    # init param's
    response = requests.get(url + motor_pare_set_pwm_value_path + motors['motor_a'] + "/" + motors['motor_b'] + "/0", params={})
    befor_parameters = get_parameters(gyro, motors)
    befor_gyro_angle = befor_parameters['gyro_angle']
    befor_gyro_dps = befor_parameters['gyro_dps']
    befor_motor_a_dps = befor_parameters['motor_a_dps']
    befor_motor_b_dps = befor_parameters['motor_b_dps']
    befor_motor_a_count_per_m = befor_parameters['motor_a_count_per_m']
    befor_motor_b_count_per_m = befor_parameters['motor_b_count_per_m']
    befor_motor_a_full_travel_count = befor_parameters['motor_a_full_travel_count']
    befor_motor_b_full_travel_count = befor_parameters['motor_b_full_travel_count']
    befor_motor_a_position = befor_parameters['motor_a_position']
    befor_motor_b_position = befor_parameters['motor_a_position']
    # send request
    response = requests.get(url + motor_pare_set_pwm_value_path + motors['motor_a'] + "/" + motors['motor_b'] + "/" + str(pwm_value), params={})
    start = time.perf_counter()
    time.sleep(DELTA)
    end = time.perf_counter()
    after_parameters = get_parameters(gyro, motors)
    gyro_angle = after_parameters['gyro_angle']
    gyro_dps = after_parameters['gyro_dps']
    motor_a_dps = after_parameters['motor_a_dps']
    motor_b_dps = after_parameters['motor_b_dps']
    after_motor_a_count_per_m = after_parameters['motor_a_count_per_m']
    after_motor_b_count_per_m = after_parameters['motor_b_count_per_m']
    after_motor_a_full_travel_count = after_parameters['motor_a_full_travel_count']
    after_motor_b_full_travel_count = after_parameters['motor_b_full_travel_count']
    after_motor_a_position = after_parameters['motor_a_position']
    after_motor_b_position = after_parameters['motor_a_position']
    delta = end - start
    (motor_a_dps, motor_b_dps) = get_motor_dps(motors, motor_a_cpr ,motor_b_cpr)
    print("pwm_value : " + str(pwm_value)
            + "\tangle : " + str(gyro_angle) + "[deg]\t" + "speed : " + str(gyro_dps) + "[deg/s]"        
            + "\tmotor_a_dps : " + str(motor_a_dps) + "\tmotor_b_dps : " + str(motor_b_dps) + "\tdelta : " + str(delta))
    result.append([str(pwm_value), str(gyro_angle), str(gyro_dps)
                   ,str(motor_a_dps), str(motor_b_dps)
                   ,str(befor_motor_a_count_per_m), str(after_motor_a_count_per_m)
                   ,str(befor_motor_b_count_per_m), str(after_motor_b_count_per_m)
                   ,str(befor_motor_a_full_travel_count), str(after_motor_a_full_travel_count)
                   ,str(befor_motor_b_full_travel_count), str(after_motor_b_full_travel_count)
                   ,str(befor_motor_a_position), str(after_motor_a_position)
                   ,str(befor_motor_b_position), str(after_motor_b_position)
                   ,str(delta)])
    response = requests.get(url + motor_pare_set_pwm_value_path + motors['motor_a'] + "/" + motors['motor_b'] + "/0", params={})
    return True

dt_now = datetime.datetime.now()


fp = open(file_name, 'w')
writer = csv.writer(fp)
start = time.perf_counter()
result = [['pwm_value', 'gyro_angle' ,'gyro_dps'
            ,'motor_a_dps', 'motor_b_dps'
            ,'befor_motor_a_count_per_m', 'after_motor_a_count_per_m'
            ,'befor_motor_b_count_per_m', 'after_motor_b_count_per_m'
            ,'befor_motor_a_full_travel_count', 'after_motor_a_full_travel_count'
            ,'befor_motor_b_full_travel_count', 'after_motor_b_full_travel_count'
            ,'befor_motor_a_position', 'after_motor_a_position'
            ,'befor_motor_b_position', 'after_motor_b_position'
            ,'delta']]
#----------------------------------#
for i in range(10):
    pwm_value = 10
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 15
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 20
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 30
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 40
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 50
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 60
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 70
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 80
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 90
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#
for i in range(10):
    pwm_value = 100
    get_experimental_result(pwm_value, gyro, motors, result)
#----------------------------------#

writer.writerows(result)
fp.close()
