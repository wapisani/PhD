# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 00:13:32 2016

@author: Will Pisani

This script will analyze Tg data files and extract CTE data for analysis in the R script. The extracted data is in a csv file and can be used computing CTE and Tg.
Prior to running this script, you should have extracted the thermodynamic data from your log file using LAMMPS_Log_2_Data_File.py.
Plug that *_sim_data.txt filename and directory location into this script in the appropriate place and then run it.

Script Usage:
Honestly, Python works best in an IDE like Spyder because it's easier to debug,
but you can also run this from the terminal like so: python Tg_CTE_Analysis.py.
This script requires numpy to be installed in the terminal.

License information:

MIT License

Copyright (c) 2019 Will Pisani

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


# Import necessary libraries
import time
import os
import getpass
import re
import numpy as np
from matplotlib import pyplot as plt
from pylab import clf,plot,xlabel,ylabel,title,savefig,scatter,xlim,ylim,legend
from pylab import close as fig_close
from PyPDF2 import PdfFileMerger, PdfFileReader

# ------- Change to appropriate directory------------------------
os.chdir("path/to/directory")

#----------Data file name specified here------------------------
sim_dat_file_name = "Your_file_name_here_sim_data.txt"

#---------------------------------------------------------------

# Define a function for exiting the script gracefully
def exit_gracefully():
    raise Exception("This exception was made for gracefully exiting scripts.")
    
#----------Check for appropriate data file----------------------
if sim_dat_file_name.find('Tg') > 0:
    print("\n{} is a Tg data file.\n".format(sim_dat_file_name))
    print("Moving on....\n")
else:
    print("\n{} is NOT a Tg data file.\n".format(sim_dat_file_name))
    print("Please use a Tg file.")
    print("Exiting....\n")
    exit_gracefully()
    
print("Loading data...\n")

#Get shape and size info from file
#Code inspired by John La Rooy: https://stackoverflow.com/questions/1767513/read-first-n-lines-of-a-file-in-python
with file(sim_dat_file_name, 'r') as data_file:
    header = [next(data_file) for x in range(2)]

# Get thermo header
thermo_header = header[1].split()[1:]

# Load data
Tg_data = np.loadtxt(sim_dat_file_name)

print("\nData has been loaded.\n")

#------------------Separate data into vectors----------------------------------
temp_index = thermo_header.index('Temp')
time_index = thermo_header.index('Time')
length_index = thermo_header.index('Lx')
density_index = thermo_header.index('Density')

temp_array = Tg_data[:,temp_index]
time_array = Tg_data[:,time_index]
length_array = Tg_data[:,length_index]
density_array = Tg_data[:,density_index]

length_initial = length_array[0] # Length of each cube side at beginning of Tg sim
volume_initial = length_initial ** 3 # Volume of cube at beginning of Tg sim

#---------------------Begin CTE Analysis---------------------------------------
print("Running CTE analysis...")
# Calculate difference in volume between initial volume and current volume
# The negative 1 was added to account for cooling Tg sims
delta_volume = (length_array**3 - volume_initial)

# Calculate delta V/V_0 times 1000
dV_V = (delta_volume / volume_initial) * 1000

# Calculate difference in length between initial length and current length
delta_length = -1*(length_array - length_initial)

# Calculate delta_l/l_0 times 1000
dl_l = (delta_length / length_initial) * 1000

# Still need to actually calculate CTE

#-----------------------Plot CTE data------------------------------------------

# Create figures
print("\nPlotting volumetric and linear thermal expansion...")
cvte_fig = plt.figure(1)
clte_fig = plt.figure(2)
cvte_ax = cvte_fig.add_subplot(1,1,1)
clte_ax = clte_fig.add_subplot(1,1,1)

# Plot data
cvte_ax.scatter(temp_array,dV_V)#,facecolors='none',edgecolors='b')
clte_ax.scatter(temp_array,dl_l)#,facecolors='none',edgecolors='b')

# Set labels
clte_ax.set_xlabel('Temperature (K)')
clte_ax.set_ylabel('Linear Expansion (dL/L times 1000)')
clte_ax.set_title('Coefficient of Linear Thermal Expansion')
cvte_ax.set_xlabel('Temperature (K)')
cvte_ax.set_ylabel('Volume Expansion (dV/V times 1000)')
cvte_ax.set_title('Coefficient of Volumetric Thermal Expansion')

#Save plots
cvte_filename = sim_dat_file_name.split('_')[0] + '_cvte' + '.pdf'
clte_filename = sim_dat_file_name.split('_')[0] + '_clte' + '.pdf'
cvte_fig.savefig(cvte_filename)
clte_fig.savefig(clte_filename)

#Save data for use in R
cte_R_data = np.zeros((len(temp_array),4))
cte_R_data[:,0] = temp_array
cte_R_data[:,1] = dl_l
cte_R_data[:,2] = dV_V
cte_R_data[:,3] = density_array
csvtitle = sim_dat_file_name.split('_')[0] + '_CTE_RData' + '.csv'
np.savetxt(csvtitle,cte_R_data,delimiter=",")
print("\nData file ready for R analysis has been saved as {}\n".format(csvtitle))
print("Plots saved to {} and {}\n".format(cvte_filename,clte_filename)) 
