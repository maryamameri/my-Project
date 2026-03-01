

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 12:22:06 2023

@author: el24ecov
"""

import numpy as np
# import csv
# import tkFileDialog.asksaveasfile
from flask import Flask, render_template, request, json, jsonify
from datetime import datetime
import time
import random
app = Flask(__name__)


# ###############################################
# import matplotlib.pyplot as plt
# import numpy as np
# import socket
# import time


#  # ETHERNET_UDP settings
# UDP_IP = '192.168.121.10'
# UDP_PORT = 5201
# RX_BUFFER_SIZE = 65536*4


# # Parameters
# # epsilon_r = 3.15
# epsilon_r = 1
# PRF_TX = 1000e3
# SF = 10000
# N = (SF+1)

# Range = 3e8/PRF_TX/2/np.sqrt(epsilon_r)

# adc_data = np.zeros([4, N])   # 4 adc channels
# ######################################################


tx_attenuator_value = None
x_values = np.array([0, 20, 40, 60, 80])
y_values = np.array([-1000, -500.6, 0, 500, 1000, 1500])
x_values = x_values
y_values = y_values
# new_data = 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/grid')
def grid():
    return render_template('grid.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/single_measurement', methods=['POST'])
def single_measurement():
    try:
        global x_values, y_values
        global new_data
        save_directory = request.form.get('save_directory')
        M_Sequence_len = request.form.get('m_sequence_len')
        enable_M_Sequence = request.form.get('enable_m_sequence')

        print("save directory:", save_directory)
        print("M Sequence len:", M_Sequence_len)
        print("Enable M Sequence:", enable_M_Sequence)

        # # Open socket
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.settimeout(5)
        # time.sleep(10e-6)

        # # Send data
        # cmd = 0x10  # Cmd radar image normal
        # payload = cmd.to_bytes(1, 'big')
        # print("Send UDP: ", payload)
        # s.sendto(payload, (UDP_IP, UDP_PORT))

        # # Receive adc data
        # response = []
        # for i in range(0, 4):   # 4 adc channels
        #     response.append(s.recvfrom(RX_BUFFER_SIZE)[0])
        # print("num of received packets: ", len(response))

        # for i in range(0, 4):   # 4 adc channels
        #     cmd = response[i][0]
        #     adc_channel = response[i][1]
        #     data = response[i][2:]

        #     for j in range(0, N):   # N samples
        #         adc_data[adc_channel, j] = int.from_bytes(data[(2*j):(2*j+2)], byteorder='little', signed=True)    # 1 sample = 2 bytes

        # y_values =  adc_data[1]
        # PRF_TX = 1e6
        # Range = 3e8/PRF_TX/2/np.sqrt(1)
        # x_values =  np.linspace(0, Range, 10001)

        # # Close socket
        # s.close()

        # new_data = 1

        return 'Data received on the server'
    except Exception as e:
        return f'Error: {str(e)}'


@app.route('/continuous_measurement', methods=['POST'])
def continuous_measurement():

    return 'Data received on the server'


@app.route('/stop_measurement', methods=['POST'])
def Stop_measurement():
    try:
        save_directory = request.form.get('save_directory')
        M_Sequence_len = request.form.get('m_sequence_len')
        enable_M_Sequence = request.form.get('enable_m_sequence')

        print("save directory:", save_directory)
        print("M Sequence len:", M_Sequence_len)
        print("Enable M Sequence:", enable_M_Sequence)

        return 'Data received on the server'
    except Exception as e:
        return f'Error: {str(e)}'

# @app.route('/cakes')
# def cakes():
#     return 'Yummy cakes!'


@app.route('/apply', methods=['POST'])
def apply():
    tx_attenuator = request.form.get('tx_attenuator')
    prf = request.form.get('prf')
    spreading_factor = request.form.get('spreading_factor')

    enable_rf_switch_tx = request.form.get('enable_rf_switch_tx')
    enable_rf_switch_lo = request.form.get('enable_rf_switch_lo')

    print("TX attenuator:", tx_attenuator)
    print("PRF:", prf)
    print("Spreading factor:", spreading_factor)
    print("Enable RF switch TX:", enable_rf_switch_tx)
    print("Enable RF switch LO:", enable_rf_switch_lo)

    return "nothing"


@app.route('/get_data')
def get_data():
    global x_values, y_values
    global new_data

    tom_datetime = generate_random_datetime()
    tom_str = tom_datetime.strftime("%d.%m.%Y %H:%M:%S")

    # if new_data == 1:

    x_values_1 = [random.uniform(0, 200) for _ in range(21)]
    y_values_1 = [random.uniform(-1000, 1500) for _ in range(21)]

    x_values_2 = [random.uniform(0, 200) for _ in range(21)]
    y_values_2 = [random.uniform(-1000, 1500) for _ in range(21)]

    x_values_3 = [random.uniform(0, 200) for _ in range(21)]
    y_values_3 = [random.uniform(-1000, 1500) for _ in range(21)]

    x_values_4 = [random.uniform(0, 200) for _ in range(21)]
    y_values_4 = [random.uniform(-1000, 1500) for _ in range(21)]

    x_values_list = [x_values_1, x_values_2, x_values_3, x_values_4]
    y_values_list = [y_values_1, y_values_2, y_values_3, y_values_4]

    data = {'x_values': x_values_list,
            'y_values': y_values_list, 'TOM': tom_str}
    print("Sending data:", data)
    # new_data == 0

    time.sleep(1)

    return json.dumps(data)

    # else:
    #     return


@app.route('/get_other_data', methods=['GET'])
def get_other_data():

    data = {'x_values': [1, 2, 3], 'y_values': [4, 5, 6]}
    return jsonify(data)


def generate_random_datetime():
    year = 2023
    month = random.randint(1, 12)
    day = random.randint(1, 28)

    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return datetime(year, month, day, hour, minute, second)


@app.route('/get_temperature', methods=['GET'])
def get_temperature_from_sensor():

    temperature = random.randint(0, 100)
    return jsonify({'temperature': temperature})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
