# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 13:52:00 2016

@author: Will Pisani

This script will analyze bulk modulus data files (BK) and plot 
pressure versus volumetric strain. It will also create data files 
for use in R.
Prior to running this script, you should have extracted the thermodynamic data from your log file using LAMMPS_Log_2_Data_File.py.
Plug that *_sim_data.txt filename and directory location into this script in the appropriate place and then run it.

Script Usage:
Honestly, Python works best in an IDE like Spyder because it's easier to debug,
but you can also run this from the terminal like so: python Bulk_Analysis.py.
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
from PyPDF2 import PdfFileMerger, PdfFileReader

# ------- Change to appropriate directory------------------------
os.chdir("path/to/directory")

#----------Data file name specified here------------------------
sim_dat_file_name = "your_file_name_here_sim_data.txt"

#---------------------------------------------------------------

# Define a function for exiting the script gracefully
def exit_gracefully():
    raise Exception("This exception was made for gracefully exiting scripts.")
    
#----------Check for appropriate data file----------------------
#My scripts follow a certain naming convention and this script will only work with that convention.
#For example, PEEK0911RxBKS5.log.lammps
#PEEK is the polymer, 0911 is the date Sept11, Rx is ReaxFF, BK is bulk modulus, S5 is sample 5
if sim_dat_file_name.find('BK') > 0 or sim_dat_file_name.find('bk') > 0:
    print("\n{} is a bulk modulus data file.\n".format(sim_dat_file_name))
    print("Moving on....\n")
else:
    print("\n{} is NOT a bulk modulus data file.\n".format(sim_dat_file_name))
    print("Please use a bulk modulus data file.")
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
BK_data = np.loadtxt(sim_dat_file_name)

print("\nData has been loaded.\n")

#------------------Separate data into vectors----------------------------------
time_index = thermo_header.index('Time')
press_index = thermo_header.index('Press')
volume_index = thermo_header.index('Volume')
density_index = thermo_header.index('Density')

press_array = BK_data[:,press_index]
time_array = BK_data[:,time_index]
volume_array = BK_data[:,volume_index]
density_array = BK_data[:,density_index]

volume_initial = volume_array[0] # Volume at beginning of BK simulation


#---------------------Begin BK Analysis---------------------------------------
print("Running BK analysis...")
# Calculate difference in volume between initial volume and current volume
vol_strain = (volume_array - volume_initial)/volume_initial

#-----------------------Plot BK data------------------------------------------

#Extract base filename
begfigname = sim_dat_file_name.split('_')[0]

#Get sample number from filename
sampnum = ' Sample ' + begfigname[-1]

#Make title for figures
titlename = 'Amorphous PEEK Bulk Modulus ReaxFF' + sampnum

# Create figures
print("\nPlotting pressure versus volumetric strain...")
bk_fig = plt.figure(1)
bk_ax = bk_fig.add_subplot(1,1,1)

# Plot data
bk_ax.scatter(vol_strain,press_array)#,facecolors='none',edgecolors='b')

# Set labels
bk_ax.set_xlabel('Volumetric strain')
bk_ax.set_ylabel('Pressure (atm)')
bk_ax.set_title(titlename)
plt.gca().invert_xaxis()

#Save plots
bk_filename = begfigname + '_PvdV' + '.pdf'
bk_fig.savefig(bk_filename)

#Save data for use in R
bk_R_data = np.zeros((len(press_array),2))
bk_R_data[:,0] = press_array
bk_R_data[:,1] = vol_strain
csvtitle = begfigname + '_BK_RData' + '.csv'
np.savetxt(csvtitle,bk_R_data,delimiter=",")
print("\nData file ready for R analysis has been saved as {}\n".format(csvtitle))
print("Plots saved to {}\n".format(bk_filename)) 
