#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
#from matplotlib import animation
#import keyboard
#from pynput.keyboard import Key, Listener
import numpy as np
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
P = []
t = []


''' Variables '''
t_real = 0											# The real time
R = 22.5											# Radius of the SM wheel in mm
#baudrate = 57600

dxl = DynamixelPort()
motor_ids = [1]
dxl.establish_connection(device_name = '/dev/ttyUSB0')
dxl.set_operating_mode(motor_ids, POSITION_CONTROL_MODE)
dxl.set_torque_enabled(motor_ids, True)
#dxl.set_baudrate(baudrate)

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

Data = Arduino_port()										# Get data from arduino

SM_initial = dxl.get_pos(motor_ids)
SM_initial_deg = (SM_initial[0] * 180 / 2048) % 360						# SM initial degree position

for SM_GP_deg in np.arange(SM_initial_deg, SM_initial_deg + 45, 0.5):				# SM Goal Poistion from current position (in degree)	
	SM_GP_value = SM_GP_deg * 2048 / 180							# Value to send to the SM for the goal position
	line1 = Data.readline()									# Read data received from arduino
	list_data = line1.strip().split()							# Delete spacing characters + data separation
	dxl.set_goal_pos(motor_ids, SM_GP_value)						# Set Goal Position
	
	if len (list_data) != 0 :								# Ignore empty lines
		SM = dxl.get_pos(motor_ids)							# Read of SM Position in decimal
		voltage = float (list_data[2].decode())						# Convert string to float
		print ('U : ', voltage,'V')
		force = float (list_data[6].decode())
		
		SM_read_deg = (SM[0] * 180 / 2048) % 360					# Read of SM position in degree
		#SM_read_rad = SM_read_deg * math.pi / 180					# Read of SM position in radian
		elongation = (math.pi) * R * (SM_read_deg - SM_initial_deg) / 180		# Length of cable pulled in mm
		#elongation = R * SM_rad							# Uncomment this if you are getting SM position in radian
			
		t_mes = time.time()								# Time measure
		list_t_mes.append(t_mes)
		t_real = t_mes - list_t_mes[0]							# Redefinition of the time origin : t -> 0s
			
		list_voltage.append(voltage)							# Put all values in lists
		list_force.append(force)
		list_t.append(t_real)
		list_elongation.append(elongation)
		list_position.append(SM_GP_deg)
		
		"""
		print (' ')
		print ('U : ', voltage,'V')
		print ('F : ', force,'N')
		print ('pos : ', SM_GP_deg,'°')
		print ('t : ', t_real,'s')
		print ('lecture :',SM_read_deg)
		"""

	
Data.close()											# Stop getting data from arduino
dxl.set_torque_enabled(motor_ids, False)							# Stop the motor
dxl.disconnect()										# Disconnect the SM
		
lines = ['U (V)\tF (N)\tpos(deg)\telongation (mm)\tt (s)\n']					# Column titles
for i in range (len(list_t)):
	line = str(list_voltage[i])+'\t'+str(list_force[i])+'\t'+str(list_position[i])+'\t'+str(list_elongation[i])+'\t'+str(list_t[i])+'\n'
	lines.append(line)
fichier = open('data_arduino.txt','w').writelines(lines)	


''' Plots'''
with open ('data_arduino.txt', 'r') as datafile :
	plotting = csv.reader(datafile, delimiter='\t')
	next(plotting)										# Skip the first row (Column title)
	for COLUMN in plotting:
		U.append(float(COLUMN[0]))
		F.append(float(COLUMN[1]))
		P.append(float(COLUMN[3]))
		t.append(float(COLUMN[4]))

"""
fig = plt.figure()
plt.ylabel('Voltage (V)')
subplot_1 = fig.add_subplot(2,1,1)
plt.plot(P, U)
plt.title('Voltage as a function of time and elongation')
plt.xlabel('Elongation (mm)')
plt.ylim([2, 5])
subplot_1 = fig.add_subplot(2,1,2)
plt.plot(t, U)
plt.xlabel('Time (s)')
plt.ylim([2, 5])
plt.show()"""
plt.figure(1)
plt.plot(P, U)
plt.title('Voltage as a function of elongation')
plt.xlabel('Elongation (mm)')
plt.ylabel('Voltage (V)')
plt.show()
