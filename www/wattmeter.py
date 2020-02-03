#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial
import time

class ReadMsg():
	def __init__(self):
		#假设初始化成功
		self.status = True
		#初始化串口
		try:
			self.ser = serial.Serial(
			#	'/dev/ttyAMA0',					#linux系统的串口号，windows为COM1等
				'/dev/ttyUSB0',
				baudrate=2400,					#设置为电表默认波特率
				bytesize=serial.EIGHTBITS,		#8位
				parity=serial.PARITY_EVEN,		#偶校验，电表(DL/T645-2007)为偶校验
				stopbits=serial.STOPBITS_ONE,	#1位停止位
				timeout=0.5						#读超时，设置为1秒
				)
		except:
			#初始化失败标志
			self.status = False

		#初始化电表字典
		self.dianbiao = {
				'201':['091701262304','-1','-1'],
				'202':['091701262308','-1','-1'],
				'301':['091701253653','-1','-1'],
				'302':['091701253652','-1','-1'],
				'401':['091701262311','-1','-1'],
				'402':['091701262315','-1','-1'],
				'501':['091701253707','-1','-1'],
				'502':['091701253655','-1','-1'],
				'601':['091701253658','-1','-1'],
				'602':['091701253656','-1','-1'],
				'701':['091701262305','-1','-1'],
				'702':['091701253703','-1','-1'],
				'801':['091701253657','-1','-1'],
				'802':['091701253660','-1','-1'],
				'901':['091701253702','-1','-1'],
				'902':['091701262310','-1','-1'],
				'1001':['091701253662','-1','-1'],
				'1002':['091701253661','-1','-1'],
				'1101':['091701253663','-1','-1'],
				'1102':['091701253654','-1','-1'],
				'1201':['091701262313','-1','-1'],
				'1202':['091701262309','-1','-1'],
				'1301':['091701262306','-1','-1'],
				'1302':['091701262314','-1','-1'],
				'1401':['091701253659','-1','-1'],
				'1402':['091701262307','-1','-1'],
				'1501':['010097796152','-1','-1'],
				'1502':['010097796152','-1','-1']
				}

		#设置tuple，存储读取数据块命令
		self.zuheyougong = ('0x33','0x33','0x33','0x33')				#组合有功
		self.zhengxiang = ('0x33','0x33','0x34','0x33')					#正向有功
		self.zuhejiesuan1 = ('0x34','0x33','0x33','0x33')				#上1个结算日组合有功
		self.zxjiesuan1 = ('0x34','0x33','0x34','0x33')					#上1个结算日正向有功
		self.zuhejiesuan2 = ('0x35','0x33','0x33','0x33')				#上2个结算日组合有功
		self.zxjiesuan2 = ('0x35','0x33','0x34','0x33')					#上2个结算日正向有功

		self.a_voltge = ('0x33','0x34','0x34','0x35')					#A相电压XXX.X
		self.a_current = ('0x33','0x34','0x35','0x35')					#A相电流XXX.XXX0
		self.z_current = ('0x34','0x33','0xB3','0x35')					#零线电流XXX.XXX0 
		self.active_power = ('0x33','0x33','0x36','0x35')				#有功功率XX.XXXX
		self.reactive_power = ('0x33','0x33','0x37','0x35')				#无功功率XX.XXXX
		self.cos = ('0x33','0x33','0x39','0x35')						#功率因素X.XXX0
		self.temperature = ('0x3A','0x33','0xB3','0x35')				#表内温度XXX.X

	def CreatMsg(self,list,tuple):
		msg = [hex(x) for x in bytes.fromhex(list[0])]	#地址，16进制数组转为字节串
		msg.reverse()						#小端在前
		msg.insert(0,'0x68')				#68H开头
		msg.append('0x68')					#地址码后面加68H
		msg.append('0x11')					#控制字11H，表示读数据
		msg.append('0x04')					#数据域长度，0字节
		for x in tuple : msg.append(x)		#加入数据块命令
		msg.append(hex(sum([int(x,16) for x in msg])&0x00000000FF))	#校验码
		msg.append('0x16')
		msg=bytes([int(x,16) for x in msg])		#数组转为16进制字符串
		return msg

	def DecodeMsg(self,by):											#str为字节串
		msg = [x for x in bytes(by)]								#转为16进制数组
		while msg[0] != 0x68:	msg.pop(0)							#去除开头的唤醒数据
		#校验数据是否正确，若不正确，则返回False
		if msg[-2] != (sum(x for x in msg[:-2])&0x00000000FF):		#计算校验码
			return False
		
		address = msg[1:7]											#获取电表地址
		address.reverse()											#改为大端在前
		address = [(x>>4&0x0F)*10+(x&0x0F) for x in address]		#BCD码转换公式
		address = ''.join(str(x) for x in address)
		if msg[8] == 0x91 :
			dl = msg[10:-2]
			dl.reverse()
			dl = [x-0x33 for x in dl]								#接收方，减0x33处理
			dl = [(x>>4&0x0F)*10+(x&0x0F) for x in dl]				#BCD码转换公式
			result = 0.0
			for x in dl[:-4]:			
				result = result*100+x
			return address,result/100
		return address

	def send(self):
		if self.ser.isOpen():
			pass
		else:
			self.ser.open()
		#开始读表
		for k,v in self.dianbiao.items():
			#读取正向有功
			self.ser.write(self.CreatMsg(self.dianbiao[k],self.zhengxiang))
			s = self.ser.readline()
			if s == b'':
				self.dianbiao[k][1] = '失败'
			else:
				self.dianbiao[k][1] = self.DecodeMsg(s)[1]
			#读取上一个结算日正向有功
			self.ser.write(self.CreatMsg(self.dianbiao[k],self.zxjiesuan1))
			s = self.ser.readline()
			if s == b'':
				self.dianbiao[k][2] = '失败'
			else:
				self.dianbiao[k][2] = self.DecodeMsg(s)[1]
		self.ser.close()

	def achieve(self):
		#打开串口
		if self.ser.isOpen():
			pass
		else:
			self.ser.open()
		for room,data in self.dianbiao.items():
			#读取正向有功
			self.ser.write(self.CreatMsg(self.dianbiao[room],self.zhengxiang))
			s = self.ser.read()
			if s != b'':
				while(ord(s) != 0x68):
					s = self.ser.read()
				for i in range(8):
					s += self.ser.read()
				L = self.ser.read()
				s += L
				for i in range(ord(L)+2):
					s += self.ser.read()
				result = self.DecodeMsg(s)
				if result != False:
					self.dianbiao[room][1] = result[1]
				else:
					self.dianbiao[room][1] = '失败'
			else:
				self.dianbiao[room][1] = '失败'
			self.ser.reset_input_buffer()
			#读取上一个结算日正向有功
			self.ser.write(self.CreatMsg(self.dianbiao[room],self.zxjiesuan1))
			s = self.ser.read()
			if s != b'':
				while(ord(s) != 0x68):
					s = self.ser.read()
				for i in range(8):
					s += self.ser.read()
				L = self.ser.read()
				s += L
				for i in range(ord(L)+2):
					s += self.ser.read()
				result = self.DecodeMsg(s)
				if result != False:
					self.dianbiao[room][2] = result[1]
				else:
					self.dianbiao[room][2] = '失败'
			else:
				self.dianbiao[room][2] = '失败'
			self.ser.reset_input_buffer()
		#关闭串口
		self.ser.close()

	def achieve_variable_data(self,room):
		#打开串口
		if self.ser.isOpen():
			pass
		else:
			self.ser.open()
		#创建字典读取数据
		data_dict = {'room':room,
					 'number':self.dianbiao[room][0],
					 'watt':-1.00,
					 'prev_watt':-1.00,
					 'active_power':-1.00,
					 'reactive_power':-1.00,
					 'cos':-1.00,
					 'a_v':-1.00,
					 'a_i':-1.00,
					 'a_z':-1.00,
					 'temp':-1.00,
					 'time':'none'}
		#读取正向有功电量
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.zhengxiang))
		data_dict['watt'] = self.__read()
		self.ser.reset_input_buffer()
		#读取上个月正向有功电量
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.zxjiesuan1))
		data_dict['prev_watt'] = self.__read()
		self.ser.reset_input_buffer()
		#读取有功功率
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.active_power))
		dd = self.__read()
		if dd == '失败' :
			data_dict['active_power'] = dd
		else:
			data_dict['active_power'] = dd/100
		self.ser.reset_input_buffer()
		#读取无功功率
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.reactive_power))
		data_dict['reactive_power'] = self.__read()
		self.ser.reset_input_buffer()
		#读取功率因素
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.cos))
		dd = self.__read()
		if dd == '失败' :
			data_dict['cos'] = dd
		else:
			data_dict['cos'] = dd/10
		self.ser.reset_input_buffer()
		#读取电压
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.a_voltge))
		dd = self.__read()
		if dd == '失败' :
			data_dict['a_v'] = dd
		else:
			data_dict['a_v'] = dd*10
		self.ser.reset_input_buffer()
		#读取a电流
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.a_current))
		dd = self.__read()
		if dd == '失败' :
			data_dict['a_i'] = dd
		else:
			if dd > 7999.99:
				data_dict['a_i'] = (dd-8000.00)/(-10)
			else:
				data_dict['a_i'] = dd/10
		self.ser.reset_input_buffer()
		#读取零线电流
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.z_current))
		dd = self.__read()
		if dd == '失败' :
			data_dict['a_z'] = dd
		else:
			if dd > 7999.99:
				data_dict['a_z'] = (dd-8000.00)/(-10)
			else:
				data_dict['a_z'] = dd/10
		self.ser.reset_input_buffer()
		#读取温度
		self.ser.write(self.CreatMsg(self.dianbiao[room],self.temperature))
		dd = self.__read()
		if dd == '失败' :
			data_dict['temp'] = dd
		else:
			if dd > 79.99:
				data_dict['temp'] = (dd-80.00)*(-10)
			else:
				data_dict['temp'] = dd*10
		self.ser.reset_input_buffer()
		#存储时间
		data_dict['time'] = time.strftime('%Y-%m-%d %H:%M')
		#关闭串口
		self.ser.close()
		#返回字典
		return data_dict

	def __read(self):
		s = self.ser.read()
		if s != b'':
			while(ord(s) != 0x68):
				s = self.ser.read()
			for i in range(8):
				s += self.ser.read()
			L = self.ser.read()
			s += L
			for i in range(ord(L)+2):
				s += self.ser.read()
			result = self.DecodeMsg(s)
			if result != False:
				return result[1]
			else:
				return '失败'
		else:
			return '失败'

	def __del__(self):
		if self.ser.isOpen():
			self.ser.close() 
			print('串口已关闭！')

		#self.ser.write(self.CreatMsg(self.dianbiao['201'],self.zuheyougong))			#发送读数要求
		#self.dianbiao['201'][1]=self.DecodeMsg(self.ser.readline())[1]					#读数据

		#self.ser.write(self.CreatMsg(self.dianbiao['202'],self.zuheyougong))			#发送读数要求
		#self.dianbiao['202'][1]=self.DecodeMsg(self.ser.readline())[1]					#读数据