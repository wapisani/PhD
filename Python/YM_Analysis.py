# -*- coding: utf-8 -*-
"""
Created on Tue May 31 15:38:57 2016

@author: Will Pisani

This script will load Young's modulus simulation data files and plot the results. It will also write the appropriate data to a file for analysis in R.
Prior to running this script, you should have extracted the thermodynamic data from your log file using LAMMPS_Log_2_Data_File.py.
Plug that *_sim_data.txt filename and directory location into this script in the appropriate place and then run it.

Potential improvements:
Turn this script into a function with options (no plots, only plots, no output,etc.)

Script Usage:
Honestly, Python works best in an IDE like Spyder because it's easier to debug,
but you can also run this from the terminal like so: python YM_Analysis.py.
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
from pylab import clf,plot,xlabel,ylabel,title,savefig,scatter,xlim,ylim,legend
from pylab import close as fig_close
from PyPDF2 import PdfFileMerger, PdfFileReader

# ------- Change to appropriate directory------------------------
os.chdir("path/to/directory")

#----------Data file name specified here------------------------

sim_dat_file_name = "your_log_file_name_here_sim_data.txt"

#---------------------------------------------------------------

# Define a function for exiting the script gracefully
def exit_gracefully():
    raise Exception("This exception was made for gracefully exiting scripts.")
    
#----------Check for appropriate data file----------------------
#My scripts follow a certain naming convention and this script will only work with that convention.
#For example, PEEK0911RxYMS5.log.lammps
#PEEK is the polymer, 0911 is the date Sept11, Rx is ReaxFF, YM is Young's modulus, S5 is sample 5
if sim_dat_file_name.find('YM') > 0 or sim_dat_file_name.find('ym') > 0:
    print("\n{} is a Young's Modulus data file.\n".format(sim_dat_file_name))
    print("Moving on....\n")
elif sim_dat_file_name.find('Ul1') > 0 or sim_dat_file_name.find('Ul2') > 0 or sim_dat_file_name.find('Ul3') > 0:
    print("\n{} is an axial unloading data file.\n".format(sim_dat_file_name))
    print("Moving on....\n")
else:
    print("\n{} is NOT a Young's Modulus data file.\n".format(sim_dat_file_name))
    print("Please use a YM file.")
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
YM_data = np.loadtxt(sim_dat_file_name)

print("\nData has been loaded. Moving on to analysis")
# Get index of 'dir'
YM_dir_index = thermo_header.index('v_dir')
YM_dir_num = int(YM_data[0,YM_dir_index])


# Get sample number for plotting purposes, this assumes a certain structure 
# in the file name.
sample_num = sim_dat_file_name[sim_dat_file_name.find("S")+1:sim_dat_file_name.find("_")]

# Get base name of data file
begfigname = sim_dat_file_name.split('.')[0].split('_')[0]

# Get today's date
TodayDate = time.strftime("%m-%d-%Y")

# Determine titlename of figures

if sim_dat_file_name.find('Cr') > 0:
    titlename = "PEEK Crystal ReaxFF YM Sample " + sample_num
else:
    titlename = "PEEK Amorphous ReaxFF YM Sample " + sample_num
    

# Branch the script based on strain direction

# If the system was strained in the x-direction...
if YM_dir_num == 1: 
    
    time_index = thermo_header.index('Time')
    sxx_ave_index = thermo_header.index('f_sxx_ave')
    eengx_index = thermo_header.index('v_eengx')
    eengy_index = thermo_header.index('v_eengy')
    eengz_index = thermo_header.index('v_eengz')
    # Get relevant data
    eengx = YM_data[:,eengx_index]
    etruex = np.log(1+eengx)
    eengy = YM_data[:,eengy_index]
    etruey = np.log(1+eengy)
    eengz = YM_data[:,eengz_index]
    etruez = np.log(1+eengz)
    timedat = YM_data[:,time_index]
    sxx_ave = YM_data[:,sxx_ave_index]
    
    
    # Plotting
    print("\nPlotting data and saving to PDF...\n")
    clf()
    scatter(etruex,sxx_ave,facecolors='none',edgecolors='b')
    #Get maximum y value, max() doesn't work on sxx_ave because it's
    #a list of strings. The below converts the strings into numpy floats.
    sxx_ave_max = max([np.float(value) for value in sxx_ave])
    title(titlename)
    xlabel('True Strain along the x-axis')
    ylabel('True Stress along the x-axis (MPa)')
    xlim([0,max(etruex)+0.1*max(etruex)])
    ylim([-100,sxx_ave_max])
    stressxfigname = begfigname + '_Stress_Strainx_' + TodayDate + '.pdf'
    savefig(stressxfigname)
    clf()
    
    plot(etruex,etruey)
    title(titlename)
    xlabel('True Axial Strain (along the x-axis)')
    ylabel('True Transverse Strain (along the y-axis)')
    xlim([0,max(etruex)+0.1*max(etruex)])
    poissonfigname = begfigname + '_Poissonyx_' + TodayDate + '.pdf'
    savefig(poissonfigname)
    clf()
    
    scatter(etruex,etruez,facecolors='none',edgecolors='b')
    title(titlename)
    xlabel('True axial strain (along the x-axis)')
    ylabel('True transverse strain (along the z-axis)')
    xlim([0,max(etruex)+0.1*max(etruex)])
    poisson13figname = begfigname + '_Poissonzx_' + TodayDate + '.pdf'
    savefig(poisson13figname)
    clf()
    
    clf()
    plot(timedat,sxx_ave)
    title(titlename)
    xlabel('Time (fs)')
    ylabel('True stress along the x-axis (MPa)')
    timefigname = begfigname + '_Stressx_time_' + TodayDate + '.pdf'
    savefig(timefigname)
    clf()
    
    figurenames = [stressxfigname,poissonfigname,poisson13figname,timefigname]

    #Credit for this solution goes to Rejected at StackOverflow. URL: https://stackoverflow.com/questions/17104926/pypdf-merging-multiple-pdf-files-into-one-pdf
    
    mergedfigname = begfigname + '_StressxPoisson_' + TodayDate + '.pdf'
    merger = PdfFileMerger()
    for figname in figurenames:
        merger.append(PdfFileReader(file(figname,'rb')))
        
    
    merger.write(mergedfigname)
    #For this part, need to not have directory open in Explorer, this apparently doesn't matter now.
    for figname in figurenames:
        os.remove(figname)
    print("Plots saved to {}\n".format(mergedfigname))   
    # Save data for use in R
    ymdata = np.zeros((len(etruex),4))
    ymdata[:,0] = sxx_ave
    ymdata[:,1] = etruex
    ymdata[:,2] = etruey
    ymdata[:,3] = timedat
    csvtitle = sim_dat_file_name.split('.')[0] + '_YMxData' + '.csv'
    np.savetxt(csvtitle,ymdata,delimiter=",")
    print("Data file ready for R analysis has been saved as {}\n".format(csvtitle))
    # Now save another csv file that has etruez as the transverse strain
    # so that you can get nu_13
    ymdata[:,2] = etruez
    csvtitle = sim_dat_file_name.split('.')[0] + '_YMxData_nu13.csv'
    np.savetxt(csvtitle,ymdata,delimiter=",")
    print("Data file ready for R analysis has been saved as {}\n".format(csvtitle))
    fig_close()
# If the system was strained in the y-direction...   
elif YM_dir_num == 2: 
    
    time_index = thermo_header.index('Time')
    syy_ave_index = thermo_header.index('f_syy_ave')
    eengx_index = thermo_header.index('v_eengx')
    eengy_index = thermo_header.index('v_eengy')
    # Get relevant data
    eengx = YM_data[:,eengx_index]
    etruex = np.log(1+eengx)
    eengy = YM_data[:,eengy_index]
    etruey = np.log(1+eengy)
    timedat = YM_data[:,time_index]
    syy_ave = YM_data[:,syy_ave_index]
    
    # Plotting
    print("\nPlotting data and saving to PDF...\n")
    clf()
    scatter(etruey,syy_ave,facecolors='none',edgecolors='b')
    #Get maximum y value, max() doesn't work on sxx_ave because it's
    #a list of strings. The below converts the strings into numpy floats.
    syy_ave_max = max([np.float(value) for value in syy_ave])
    title(titlename)
    xlabel('True strain along the y-axis')
    ylabel('True stress along the y-axis (MPa)')
    xlim([0,max(etruey)+0.1*max(etruey)])
    ylim([-50,syy_ave_max])
    stressyfigname = begfigname + 'Stress_Strainy_' + TodayDate + '.pdf'
    savefig(stressyfigname)
    clf()
    
    plot(etruey,etruex)
    title(titlename)
    xlabel('True Axial Strain (along the y-axis)')
    ylabel('True Transverse Strain (along the x-axis)')
    xlim([0,max(etruey)+0.1*max(etruey)])
    poissonfigname = begfigname + 'Poissonxy_' + TodayDate + '.pdf'
    savefig(poissonfigname)
    clf()
    
    clf()
    scatter(timedat,syy_ave,facecolors='none',edgecolors='b')
    title(titlename)
    xlabel('Time (fs)')
    ylabel('True stress along the y-axis (MPa)')
    timefigname = begfigname + 'Stressy_time_' + TodayDate + '.pdf'
    savefig(timefigname)
    clf()
    
    figurenames = [stressyfigname,poissonfigname,timefigname]

    #Credit for this solution goes to Rejected at StackOverflow. URL: https://stackoverflow.com/questions/17104926/pypdf-merging-multiple-pdf-files-into-one-pdf
    
    mergedfigname = begfigname + '_StressyPoisson_' + TodayDate + '.pdf'
    merger = PdfFileMerger()
    for figname in figurenames:
        merger.append(PdfFileReader(file(figname,'rb')))
        
    
    merger.write(mergedfigname)
    #For this part, need to not have directory open in Explorer, this apparently doesn't matter now.
    for figname in figurenames:
        os.remove(figname)
    print("Plots saved to {}\n".format(mergedfigname))
    #Save data for use in R
    ymdata = np.zeros((len(etruex),4))
    ymdata[:,0] = syy_ave
    ymdata[:,1] = etruey
    ymdata[:,2] = etruex
    ymdata[:,3] = timedat
    csvtitle = sim_dat_file_name.split('.')[0] + '_YMyData' + '.csv'
    np.savetxt(csvtitle,ymdata,delimiter=",")
    print("Data file ready for R analysis has been saved as {}\n".format(csvtitle))
    fig_close()
# If the system was strained in the z-direction...    
elif YM_dir_num == 3:
    
    time_index = thermo_header.index('Time')
    szz_ave_index = thermo_header.index('f_szz_ave')
    eengz_index = thermo_header.index('v_eengz')
    eengy_index = thermo_header.index('v_eengy')
    # Get relevant data
    eengz = YM_data[:,eengz_index]
    etruez = np.log(1+eengz)
    eengy = YM_data[:,eengy_index]
    etruey = np.log(1+eengy)
    timedat = YM_data[:,time_index]
    szz_ave = YM_data[:,szz_ave_index]
    
    # Plotting
    print("\nPlotting data and saving to PDF...\n")
    clf()
    scatter(etruez,szz_ave,facecolors='none',edgecolors='b')
    #Get maximum y value, max() doesn't work on sxx_ave because it's
    #a list of strings. The below converts the strings into numpy floats.
    szz_ave_max = max([np.float(value) for value in szz_ave])
    title(titlename)
    xlabel('True strain along the z-axis')
    ylabel('True stress along the z-axis (MPa)')
    xlim([0,max(etruez)+0.1*max(etruez)])
    ylim([-100,szz_ave_max])
    stresszfigname = begfigname + 'Stress_Strainz_' + TodayDate + '.pdf'
    savefig(stresszfigname)
    clf()
    
    scatter(etruez,etruey,facecolors='none',edgecolors='b')
    title(titlename)
    xlabel('True Axial Strain (along the z-axis)')
    ylabel('True Transverse Strain (along the y-axis)')
    xlim([0,max(etruez)+0.1*max(etruez)])
    poissonfigname = begfigname + 'Poissonyz_' + TodayDate + '.pdf'
    savefig(poissonfigname)
    clf()
    
    clf()
    plot(timedat,szz_ave)
    title(titlename)
    xlabel('Time (fs)')
    ylabel('True stress along the z-axis (MPa)')
    timefigname = begfigname + 'Stressy_time_' + TodayDate + '.pdf'
    savefig(timefigname)
    clf()
    
    figurenames = [stresszfigname,poissonfigname,timefigname]

    #Credit for this solution goes to Rejected at StackOverflow. URL: https://stackoverflow.com/questions/17104926/pypdf-merging-multiple-pdf-files-into-one-pdf
    
    mergedfigname = begfigname + '_StressZPoisson_' + TodayDate + '.pdf'
    merger = PdfFileMerger()
    for figname in figurenames:
        merger.append(PdfFileReader(file(figname,'rb')))
        
    
    merger.write(mergedfigname)
    #For this part, need to not have directory open in Explorer, this apparently doesn't matter now.
    for figname in figurenames:
        os.remove(figname)
    print("Plots saved to {}\n".format(mergedfigname))
    #Save data for use in R
    ymdata = np.zeros((len(etruex),4))
    ymdata[:,0] = szz_ave
    ymdata[:,1] = etruez
    ymdata[:,2] = etruey
    ymdata[:,3] = timedat
    csvtitle = sim_dat_file_name.split('.')[0] + '_YMzData' + '.csv'
    np.savetxt(csvtitle,ymdata,delimiter=",")
    print("Data file ready for R analysis has been saved as {}\n".format(csvtitle))
    fig_close()
else:
    print("dir is either not specified in the thermo data or....")
