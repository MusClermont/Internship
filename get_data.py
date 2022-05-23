#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
#from matplotlib import animation
#import keyboard
#from pynput.keyboard import Key, Listener
#import numpy as np
from dynamixel_port import *
import math
import time
import csv


''' Initialization of the different lists '''
list_elongation = []
list_position = []
list_voltage = []
list_force = []
list_t_mes = []
list_t = []

SM = []
U = []
F = []
t = []


''' Variables '''
t_acquisition = 5.0										# Acquisition time
t_real = 0											# The real time
R = 4												# Radius of the SM wheel
i = 0


''' Receiving arduino data '''
def Arduino_port() :
	ports = list( serial.tools.list_ports.comports())
	for p in ports :
		#print(p.description)
		if "USB Serial" in p.description :
			mData = serial.Serial (p.device, 57600)
	#print (mData.is_open)
	#print (mData.name)
	return mData


#Data = Arduino_port()
dxl = DynamixelPort()

motor_ids = [1, 2, 3]
dxl.establish_connection(device_name = '/dev/ttyUSB0')
dxl.set_operating_mode(motor_ids, POSITION_CONTROL_MODE)
dxl.set_torque_enabled(motor_ids, True)


while i < 512:
#while t_real < t_acquisition :
	Data  = Arduino_port()
	ard = Data.readline()									# Reading arduino data
	list_data = ard.strip().split()								# Delete spacing characters + data separation
	
	dxl.set_goal_pos(motor_ids, i)
	
	if len (list_data) != 0 :								# Ignore empty lines
		SM = dxl.get_pos(motor_ids)							# SM Position in decimal
		#print(SM[0])								
		
		voltage = float (list_data[2].decode())
		force = float (list_data[6].decode())
		SM_deg = SM[0] * 180.0 / 2048.0							# SM Position in degree
		SM_rad = SM_deg * math.pi / 180							# SM Poistion in radian
		elongation = math.pi * R * SM_rad / 180						# Length of cable pulled
			
		t_mes = time.time()
		list_t_mes.append(t_mes)
		t_real = t_mes - list_t_mes[0]							# Redefinition of the time origin : t -> 0s
			
		list_voltage.append(voltage)
		list_force.append(force)
		list_t.append(t_real)
		list_elongation.append(elongation)
		list_position.append(SM_deg)
		'''
		print (' ')
		print ('U : ', voltage,'V')
		print ('F : ', force,'N')
		print ('pos : ', position,'°')
		print ('t : ', t_real,'s')
		'''
	i = i+5
	
Data.close()
dxl.set_torque_enabled(motor_ids, False)
dxl.disconnect()	
		
lines = ['U(V) \tF(N) \tpos \t        elongation \t        t(s)\n']					# Column titles
for i in range (len(list_t)):
	line = str(list_voltage[i])+'\t'+str(list_force[i])+'\t'+str(list_position[i])+'\t'+str(list_elongation[i])+'\t'+str(list_t[i])+'\n'
	lines.append(line)
fichier = open('data_arduino_test.txt','w').writelines(lines)	


''' Plots'''
with open ('data_arduino_test.txt', 'r') as datafile :
	plotting = csv.reader(datafile, delimiter='\t')
	next(plotting)										# Skip the first row (Column title)
	for ROWS in plotting:
		U.append(float(ROWS[0]))
		F.append(float(ROWS[1]))
		t.append(float(ROWS[4]))


fig = plt.figure()

subplot_1 = fig.add_subplot(2,1,1)
plt.plot(t, F)
plt.title('Force and Voltage as a function of time')
plt.ylabel('Force (N)')

subplot_1 = fig.add_subplot(2,1,2)
plt.plot(t, U)
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.ylim((2,4.5))
plt.show()

