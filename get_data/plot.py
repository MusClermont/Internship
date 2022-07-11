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
with open ('all_data.txt', 'r') as datafile :						# All data
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
	
		
def function(P, a, b, c):									# Define the objective function
    return a * np.exp(-b * P) + c


""" Curve Fitting """
popt, _ = curve_fit(function, P, U)								# popt contains the coefficients a, b and c in list
#print(popt)											# a = 0.38845225; b = 0.18639939; c = 2.8406692 
a, b, c = popt											# Summarize the parameter values
P_line = arange(min(P), max(P), 1)								# Define a sequence of inputs between the smallest and largest known inputs
U_line = function(P_line, a, b, c)								# Calculate the output for the range


""" Plotting """
plt.subplot(2, 1, 1)
plt.scatter(P1, U1, s=12, c='b', label='1st measure')
plt.scatter(P2, U2, s=12, c='g', label='2nd measure')
plt.scatter(P3, U3, s=12, c='r', label='3rd measure')
plt.title('Voltage as a function of the elongation')
plt.ylabel('Voltage (V)')
plt.legend(loc='best')

plt.subplot(2, 1, 2)
plt.scatter(P, U, s=12, c='c', label='All data')
plt.xlabel('elongation (mm)')
plt.ylabel('Voltage (V)')
plt.plot(P_line, U_line, 'k-', color='k', label="Model")
plt.legend(loc='best')
plt.show()


