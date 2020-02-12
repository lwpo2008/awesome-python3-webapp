#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
import wattmeter
import config
import time

app = Flask(__name__)

wm = wattmeter.ReadMsg()

def get_data_from_db():
	cfg = config.Config()
	ROOM_DATA = cfg.get()
	ROOM_DATA2 = [[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
	for i in range(14):
		ROOM_DATA2[i].append(ROOM_DATA[2*i][1])
		ROOM_DATA2[i].append(ROOM_DATA[2*i][3])
		ROOM_DATA2[i].append(ROOM_DATA[2*i][4])
		ROOM_DATA2[i].append(ROOM_DATA[2*i][6])
		ROOM_DATA2[i].append(ROOM_DATA[2*i+1][1])
		ROOM_DATA2[i].append(ROOM_DATA[2*i+1][3])
		ROOM_DATA2[i].append(ROOM_DATA[2*i+1][4])
		ROOM_DATA2[i].append(ROOM_DATA[2*i+1][6])

	del cfg
	return ROOM_DATA2

def get_variable_data_from_meter(room):
	#等待串口空闲
	if wm.ser.isOpen():
		return 	{'room':room,
				'number':-1.00,
				'meter_date':'none',
				'meter_time':'none',
				'watt':-1.00,
				'prev_watt':-1.00,
				'frezon_active_power':-1.00,
				'frezon_time':'none',
				'active_power':-1.00,
				'reactive_power':-1.00,
				'cos':-1.00,
				'a_v':-1.00,
				'a_i':-1.00,
				'a_z':-1.00,
				'temp':-1.00,
				'time':'接口正在使用，请稍后再试！'}
	else:
		return wm.achieve_variable_data(room)

def update_time():
	#等待串口空闲
	if wm.ser.isOpen():
		return '接口正在使用，请稍后再试！'
	else:
		#更新时间
		wm.broadcasting_time()
		return '已更新电表时间'

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html',room_data=get_data_from_db())

@app.route('/page/<string:page>', methods=['GET'])
def room_detail(page):
    return render_template('page_detail.html', data_dict = get_variable_data_from_meter(page))

@app.route('/page/<string:page>', methods=['POST'])
def update_meter_time(page):
    return render_template('page_detail.html',message = update_time(), data_dict = get_variable_data_from_meter(page))

if __name__ == '__main__':
    app.run(host='192.168.1.77',port=1717,debug=False)