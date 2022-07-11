#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dynamixel_port import *
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import numpy as np
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

''' Variables '''
t_real = 0											# The real time
R = 22.5											# Radius of the SM wheel in mm

''' Receiving data from Arduino '''
def Arduino_port() :
	ports = list( serial.tools.list_ports.comports())
	for p in ports :
		#print(p.description)
		if "USB Serial" in p.description :
			mData = serial.Serial (p.device, 57600)
	#print (mData.is_open)
	#print (mData.name)
	return mData


dxl = DynamixelPort()
motor_ids = [1]
dxl.establish_connection(device_name = '/dev/ttyUSB0', baudrate = 57600)			# Connection to the ServoMotor
dxl.set_operating_mode(motor_ids, POSITION_CONTROL_MODE)					# Chose of the mode
dxl.set_torque_enabled(motor_ids, True)

SM_initial = dxl.get_pos(motor_ids)
SM_initial_deg = (SM_initial[0] * 180 / 2048) % 360						# SM initial degree position
SM_initial_value = SM_initial[0] 
	
for j in range(39):

	SM_GP_value = SM_initial_value + j*20							# 1 deg rotation = 11.37
	SM_GP_deg = SM_GP_value * 180 / 2048							# Value to send to the SM for the goal position
	
	dxl.set_goal_pos(motor_ids, SM_GP_value)						# Set Goal Position
	
	SM = dxl.get_pos(motor_ids)								# Read of SM Position in decimal
	SM_read_deg = (SM[0] * 180 / 2048) % 360						# Read of SM position in degree
	elongation = (math.pi) * R * (SM_read_deg - SM_initial_deg) / 180			# Length of cable pulled in mm

	Data = Arduino_port()									# Get data from arduino
	
	line1 = Data.readline()								# Read data received from arduino
	list_data = line1.strip().split()							# Delete spacing characters + data separation
	
	if len (list_data) != 0 :								# Ignore empty lines
		voltage = float (list_data[2].decode())					# Convert string to float
		#print ('U : ', voltage,'V')
		force = float (list_data[6].decode())
			
		t_mes = time.time()								# Time measure
		list_t_mes.append(t_mes)
		t_real = t_mes - list_t_mes[0]						# Redefinition of the time origin : t -> 0s
			
		list_voltage.append(voltage)							# Put all values in lists
		list_force.append(force)
		list_t.append(t_real)
		list_elongation.append(elongation)
		list_position.append(SM_read_deg-SM_initial_deg)
	Data.close()										# Stop getting data from arduino

dxl.set_torque_enabled(motor_ids, False)							# Stop the motor
dxl.disconnect()										# Disconnexion of the ServoMotor

""" Save data in a txt file"""
lines = ['U (V)\tF (N)\tpos(deg)\telongation (mm)\tt (s)\n']					# Column titles
for i in range (len(list_t)):
	line = str(list_voltage[i])+'\t'+str(list_force[i])+'\t'+str(list_position[i])+'\t'+str(list_elongation[i])+'\t'+str(list_t[i])+'\n'
	lines.append(line)
fichier = open('data_arduino.txt','w').writelines(lines)	



