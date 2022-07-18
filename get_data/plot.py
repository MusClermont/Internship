#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from numpy import arange
import numpy as np
import csv


''' Initialization of the different lists '''
U, U1, U2, U3 = [], [], [], []
P, P1, P2, P3 = [], [], [], []
F, F1, F2, F3 = [], [], [], []
t, t1, t2, t3 = [], [], [], []

''' Getting date from txt files'''
with open ('all_data.txt', 'r') as datafile :							# All data
	plotting = csv.reader(datafile, delimiter='\t')
	next(plotting)										# Skip the first row (Column title)
	for COLUMN in plotting:
		U.append(float(COLUMN[0]))
		F.append(float(COLUMN[1]))
		P.append(float(COLUMN[3]))
		t.append(float(COLUMN[4]))

with open ('data_arduino1.txt', 'r') as datafile :						# 1st measure
	plotting = csv.reader(datafile, delimiter='\t')
	next(plotting)										# Skip the first row (Column title)
	for COLUMN in plotting:
		U1.append(float(COLUMN[0]))
		F1.append(float(COLUMN[1]))
		P1.append(float(COLUMN[3]))
		t1.append(float(COLUMN[4]))

with open ('data_arduino2.txt', 'r') as datafile :						# 2nd measure
	plotting = csv.reader(datafile, delimiter='\t')
	next(plotting)										# Skip the first row (Column title)
	for COLUMN in plotting:
		U2.append(float(COLUMN[0]))
		F2.append(float(COLUMN[1]))
		P2.append(float(COLUMN[3]))
		t2.append(float(COLUMN[4]))
		
with open ('data_arduino3.txt', 'r') as datafile :						# 3rd measure
	plotting = csv.reader(datafile, delimiter='\t')
	next(plotting)										# Skip the first row (Column title)
	for COLUMN in plotting:
		U3.append(float(COLUMN[0]))
		F3.append(float(COLUMN[1]))
		P3.append(float(COLUMN[3]))
		t3.append(float(COLUMN[4]))
		


def function_V(P, a, b, c):									# Define the objective function for the voltage
	return (a * P) - (b * P**2) + c
	
def function_F(P, d, e, f):									# Define the objective function for the force
	return (d * P) - (e * P**2) + f
	


""" Curve Fitting """
popt, _ = curve_fit(function_V, P, U, maxfev=2000)						# popt contains the coefficients a, b and c in list
#print(popt)											# a = 0.01121689   b = 0.00686325   c = 3.14069579
a, b, c = popt											# Summarize the parameter values
P_line = arange(min(P), max(P), 0.2)								# Define a sequence of inputs between the smallest and largest known inputs
U_line = function_V(P_line, a, b, c)								# Calculate the output for the range

popt, _ = curve_fit(function_F, P, F, maxfev=2000)						
#print(popt)											# a = 0.61470511   b = 0.04835269   c = 0.05451149
d, e, f = popt											
P_line = arange(min(P), max(P), 0.2)								
F_line = function_F(P_line, d, e, f)


U_mean = np.mean(U)										# Avg  = 3.047 V
U_std = np.std(U)										# SD   = O.O69 V
U_max = max(U)											# Vmax = 3.160 V
U_min = min(U)											# Vmin = 2.920 V

F_mean = np.mean(F)										# Avg  = 2.138 N
F_std = np.std(F)										# SD   = 1.253 N
F_max = max(F)											# Vmax = 4.269 N
F_min = min(F)											# Vmin = 0.031 N

R = (U_line * 1000) / (5 - U_line)
R_max = max(R)											# Rmax = 1689.178 Ω
R_min = min(R)											# Rmin = 1413.972 Ω


""" Plotting """
plt.subplot(2, 3, 1)
plt.scatter(P1, U1, s=12, c='b', label='1st measure')
plt.scatter(P2, U2, s=12, c='g', label='2nd measure')
plt.scatter(P3, U3, s=12, c='r', label='3rd measure')
plt.title('Voltage as a function of the elongation')
plt.ylabel('Voltage (V)')
plt.legend(loc='best')

plt.subplot(2, 3, 2)
plt.scatter(P1, F1, s=12, c='b', label='1st measure')
plt.scatter(P2, F2, s=12, c='g', label='2nd measure')
plt.scatter(P3, F3, s=12, c='r', label='3rd measure')
plt.title('Force as a function of the elongation')
plt.ylabel('Force (N)')
plt.legend(loc='best')

plt.subplot(2, 3, 4)
plt.scatter(P, U, s=12, c='c', label='All data')
plt.text(0, 2.93, r"$SD = %.3f$ V"%(U_std),  fontsize = 8)
plt.text(0, 2.95, r"$Avg = %.3f$ V"%(U_mean),  fontsize = 8)
plt.text(1.5, 2.93, r"$Vmax = %.3f$ V"%(U_max),  fontsize = 8)
plt.text(1.5, 2.95, r"$Vmin = %.3f$ V"%(U_min),  fontsize = 8)
plt.xlabel('Elongation (mm)')
plt.ylabel('Voltage (V)')
plt.plot(P_line, U_line, 'k-', color='k', label="Model")
plt.legend(loc='best')

plt.subplot(2, 3, 5)
plt.scatter(P, F, s=12, c='c', label='All data')
plt.text(0, -3.6, r"$SD = %.3f$ N"%(F_std),  fontsize = 8)
plt.text(0, -3.9, r"$Avg = %.3f$ N"%(F_mean),  fontsize = 8)
plt.text(1.7, -3.9, r"$Fmax = %.3f$ N"%(F_max),  fontsize = 8)
plt.text(1.7, -3.6, r"$Fmin = %.3f$ N"%(F_min),  fontsize = 8)
plt.xlabel('Elongation (mm)')
plt.ylabel('Force (N)')
plt.plot(P_line, F_line, 'k-', color='k', label="Model")
plt.legend(loc='best')

plt.subplot(2, 3, 3)
plt.plot(P_line, R, 'k-', color='k')
plt.title('Resistance as a function of the elongation')
plt.text(0, 1430, r"$Rmax = %.3f$ Ω"%(R_max),  fontsize = 8)
plt.text(0, 1450, r"$Rmin = %.3f$ Ω"%(R_min),  fontsize = 8)
plt.xlabel('Elongation (mm)')
plt.ylabel('Resistance (Ohm)')
plt.legend(loc='best')
plt.show()
