# -*- coding: utf-8 -*-
"""
Created on Tue May 31 15:38:57 2016

@author: Will Pisani

This script will load shearing simulation data files and plot the 
results. It will also write the appropriate data to a file for analysis in R.
Prior to running this script, you should have extracted the thermodynamic data from your log file using LAMMPS_Log_2_Data_File.py.
Plug that *_sim_data.txt filename and directory location into this script in the appropriate place and then run it.

Potential improvements:
Turn this script into a function with options (no plots, only plots, no output,etc.)

Script Usage:
Honestly, Python works best in an IDE like Spyder because it's easier to debug,
but you can also run this from the terminal like so: python Shear_Analysis.py.
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
from copy import deepcopy
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
sim_dat_file_name = "your_file_name_here_sim_data.txt"

varplots = 1 # 0 means no plots, 1 means plots
#---------------------------------------------------------------

# Define a function for exiting the script gracefully
def exit_gracefully():
    raise Exception("This exception was made for gracefully exiting scripts.")
    
#----------Check for appropriate data file----------------------
#My scripts follow a certain naming convention and this script will only work with that convention.
#For example, PEEK0911RxShS5.log.lammps
#PEEK is the polymer, 0911 is the date Sept11, Rx is ReaxFF, Sh is shear modulus, S5 is sample 5
if sim_dat_file_name.find('Sh') > 0:
    print("\n{} is a shearing data file.\n".format(sim_dat_file_name))
    print("Moving on....\n")
else:
    print("\n{} is NOT a shearing data file.\n".format(sim_dat_file_name))
    print("Please use a Sh file.")
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
Sh_data = np.loadtxt(sim_dat_file_name)

print("\nData has been loaded. Moving on to analysis")
# Get index of 'dir'
Sh_dir_index = thermo_header.index('v_dir')
Sh_dir_num = int(Sh_data[0,Sh_dir_index])

# dir 1 means xy
# dir 2 means xz
# dir 3 means yz

# Get sample number for plotting purposes, this assumes a certain structure 
# in the file name.
sample_num = sim_dat_file_name[sim_dat_file_name.find("rS")+1:sim_dat_file_name.find("_")]

# Get base name of data file
begfigname = sim_dat_file_name.split('.')[0].split('_')[0]

# Get today's date
TodayDate = time.strftime("%m-%d-%Y")

# Determine titlename of figures

if sim_dat_file_name.find('Cr') > 0:
    titlename = "PEEK Crystal ReaxFF Shearing " + sample_num
else:
    titlename = "PEEK Amorphous ReaxFF Shearing " + sample_num
    

# Branch the script based on strain direction
if varplots == 0:
    print("\nNo Plots will be printed.")
    # Get the xy, xz, and yz box dimensions
    Yz_index = thermo_header.index("Yz")
    Yz = Sh_data[:,Yz_index]
    Xz_index = thermo_header.index("Xz")
    Xz = Sh_data[:,Xz_index]
    Xy_index = thermo_header.index("Xy")
    Xy = Sh_data[:,Xy_index]
    print("The dimension of xy is %3.3f" % Xy[-1])
    print("The dimension of xz is %3.3f" % Xz[-1])
    print("The dimension of yz is %3.3f" % Yz[-1])
else:
    
    # If the system was strained in the xy-direction...
    if Sh_dir_num == 1: 
        
        time_index = thermo_header.index('Time')
        sxy_ave_index = thermo_header.index('f_sxy_ave')
        cellgamma_index = thermo_header.index('CellGamma')
        cellbeta_index = thermo_header.index('CellBeta')
        cellalpha_index = thermo_header.index('CellAlpha')
        # Get relevant data
        cellgamma = Sh_data[:,cellgamma_index]
        gamma_xy = 90 - cellgamma
        gamma_xy_radians = np.pi/180 * gamma_xy
        true_gamma_xy_rad = np.log(1+gamma_xy_radians)
        true_gamma_xy = np.log(1+gamma_xy)
        cellbeta = Sh_data[:,cellbeta_index]
        gamma_xz = 90 - cellbeta
        cellalpha = Sh_data[:,cellalpha_index]
        gamma_yz = 90 - cellbeta
        timedat = Sh_data[:,time_index]
        sxy_ave = Sh_data[:,sxy_ave_index]
        
        
        # Plotting
        print("\nPlotting data and saving to PDF...\n")
        clf()
        scatter(true_gamma_xy_rad,sxy_ave,facecolors='none',edgecolors='b')
#        plot(true_gamma_xy_rad,sxy_ave)        
        sxy_ave_max = np.max(sxy_ave)
        title(titlename)
        xlabel('True Strain along the xy-axis')
        ylabel('True Stress along the xy-axis (MPa)')
        xlim([0,np.max(true_gamma_xy_rad)+0.05*np.max(true_gamma_xy_rad)])
        ylim([-100,np.max(sxy_ave)+0.05*np.max(sxy_ave)])
        stressxyfigname = begfigname + '_Stress_Strainxy_' + TodayDate + '.pdf'
        savefig(stressxyfigname)
        clf()
        
        #Find index where strain become greater than 0.09
        for n,strain in enumerate(true_gamma_xy_rad):
            if strain > 0.09:
                cutoff_value = n
                break
            else:
                cutoff_value = len(true_gamma_xy_rad)
                
        #Get arrays of new data, chop off data greater than 0.09 true strain
        new_strain = deepcopy(true_gamma_xy_rad[0:cutoff_value])
        new_stress_xy = deepcopy(sxy_ave[0:cutoff_value])
        clf()
        scatter(new_strain,new_stress_xy,facecolors='none',edgecolors='b')
        title(titlename+' Shortened')
        xlabel('True strain along the xy-axis')
        ylabel('True Stress along the xy-axis (MPa)')
        xlim([0,np.max(new_strain)+0.05*np.max(new_strain)])
        ylim([np.min(new_stress_xy),np.max(new_stress_xy)-100])
        stressxyshortfigname = begfigname + '_Stress_Strainxy_Short_' + TodayDate + '.pdf'
        savefig(stressxyshortfigname)
        clf()
        
        #Save data for use in R
        sh_R_data = np.zeros((len(new_strain),2))
        sh_R_data[:,0] = new_stress_xy
        sh_R_data[:,1] = new_strain
        csvtitle = sim_dat_file_name.split('.')[0] + '_ShxyData' + '.csv'
        np.savetxt(csvtitle,sh_R_data,delimiter=",")
        print("Data file ready for R analysis has been saved as {}\n".format(csvtitle))
        print("Plots saved to {} and {}\n".format(stressxyfigname,stressxyshortfigname)) 

        fig_close()
#        
#        figurenames = [stressxfigname,poissonfigname,timefigname]
#    
#        #Credit for this solution goes to Rejected at StackOverflow. URL: https://stackoverflow.com/questions/17104926/pypdf-merging-multiple-pdf-files-into-one-pdf
#        
#        mergedfigname = begfigname + '_StressxPoisson_' + TodayDate + '.pdf'
#        merger = PdfFileMerger()
#        for figname in figurenames:
#            merger.append(PdfFileReader(file(figname,'rb')))
#            
#        
#        merger.write(mergedfigname)
#        #For this part, need to not have directory open in Explorer, this apparently doesn't matter now.
#        for figname in figurenames:
#            os.remove(figname)
        
    # If the system was strained in the xz-direction...   
    elif Sh_dir_num == 2: 
        
        time_index = thermo_header.index('Time')
        sxz_ave_index = thermo_header.index('f_sxz_ave')
        cellgamma_index = thermo_header.index('CellGamma')
        cellbeta_index = thermo_header.index('CellBeta')
        cellalpha_index = thermo_header.index('CellAlpha')
        # Get relevant data
        cellbeta = Sh_data[:,cellbeta_index]
        gamma_xz = 90 - cellbeta
        gamma_xz_radians = np.pi/180 * gamma_xz
        true_gamma_xz_rad = np.log(1+gamma_xz_radians)
        true_gamma_xz = np.log(1+gamma_xz)
        cellbeta = Sh_data[:,cellbeta_index]
        gamma_xz = 90 - cellbeta
        cellalpha = Sh_data[:,cellalpha_index]
        gamma_yz = 90 - cellbeta
        timedat = Sh_data[:,time_index]
        sxz_ave = Sh_data[:,sxz_ave_index]
        
        
        # Plotting
        print("\nPlotting data and saving to PDF...\n")
        clf()
        scatter(true_gamma_xz_rad,sxz_ave,facecolors='none',edgecolors='b')
#        plot(true_gamma_xz_rad,sxz_ave)        
        sxz_ave_max = np.max(sxz_ave)
        title(titlename)
        xlabel('True Strain along the xz-axis')
        ylabel('True Stress along the xz-axis (MPa)')
        xlim([0,np.max(true_gamma_xz_rad)+0.05*np.max(true_gamma_xz_rad)])
        ylim([-550,350])
        stressxzfigname = begfigname + '_Stress_Strainxz_' + TodayDate + '.pdf'
        savefig(stressxzfigname)
        clf()
        
        #Find index where strain become greater than 0.09
        for n,strain in enumerate(true_gamma_xz_rad):
            if strain > 0.09:
                cutoff_value = n
                break
            else:
                cutoff_value = len(true_gamma_xz_rad)
                
        #Get arrays of new data, chop off data greater than 0.09 true strain
        new_strain = deepcopy(true_gamma_xz_rad[0:cutoff_value])
        new_stress_xz = deepcopy(sxz_ave[0:cutoff_value])
        clf()
        scatter(new_strain,new_stress_xz,facecolors='none',edgecolors='b')
        title(titlename+' Shortened')
        xlabel('True strain along the xz-axis')
        ylabel('True Stress along the xz-axis (MPa)')
        xlim([0,np.max(new_strain)+0.05*np.max(new_strain)])
        ylim([np.min(new_stress_xz),np.max(new_stress_xz)-100])
        stressxzshortfigname = begfigname + '_Stress_Strainxz_Short_' + TodayDate + '.pdf'
        savefig(stressxzshortfigname)
        clf()
        
        #Save data for use in R
        sh_R_data = np.zeros((len(new_strain),2))
        sh_R_data[:,0] = new_stress_xz
        sh_R_data[:,1] = new_strain
        csvtitle = sim_dat_file_name.split('.')[0] + '_ShxzData' + '.csv'
        np.savetxt(csvtitle,sh_R_data,delimiter=",")
        print("Data file ready for R analysis has been saved as {}\n".format(csvtitle))
        print("Plots saved to {} and {}\n".format(stressxzfigname,stressxzshortfigname)) 

        fig_close()
    # If the system was strained in the yz-direction...    
    elif Sh_dir_num == 3:
        
        time_index = thermo_header.index('Time')
        syz_ave_index = thermo_header.index('f_syz_ave')
        cellgamma_index = thermo_header.index('CellGamma')
        cellbeta_index = thermo_header.index('CellBeta')
        cellalpha_index = thermo_header.index('CellAlpha')
        # Get relevant data
        cellalpha = Sh_data[:,cellalpha_index]
        gamma_yz = 90 - cellalpha
        gamma_yz_radians = np.pi/180 * gamma_yz
        true_gamma_yz_rad = np.log(1+gamma_yz_radians)
        true_gamma_yz = np.log(1+gamma_yz)
        cellbeta = Sh_data[:,cellbeta_index]
        gamma_xz = 90 - cellbeta
        cellalpha = Sh_data[:,cellalpha_index]
        gamma_yz = 90 - cellbeta
        timedat = Sh_data[:,time_index]
        syz_ave = Sh_data[:,syz_ave_index]
        
        
        # Plotting
        print("\nPlotting data and saving to PDF...\n")
        clf()
        scatter(true_gamma_yz_rad,syz_ave,facecolors='none',edgecolors='b')
#        plot(true_gamma_yz_rad,syz_ave)        
        syz_ave_max = np.max(syz_ave)
        title(titlename)
        xlabel('True Strain along the yz-axis')
        ylabel('True Stress along the yz-axis (MPa)')
        xlim([0,np.max(true_gamma_yz_rad)+0.05*np.max(true_gamma_yz_rad)])
        ylim([-150,150])
        stressyzfigname = begfigname + '_Stress_Strainyz_' + TodayDate + '.pdf'
        savefig(stressyzfigname)
        clf()
        
        #Find index where strain become greater than 0.09
        for n,strain in enumerate(true_gamma_yz_rad):
            if strain > 0.09:
                cutoff_value = n
                break
            else:
                cutoff_value = len(true_gamma_yz_rad)
                
        #Get arrays of new data, chop off data greater than 0.09 true strain
        new_strain = deepcopy(true_gamma_yz_rad[0:cutoff_value])
        new_stress_yz = deepcopy(syz_ave[0:cutoff_value])
        clf()
        scatter(new_strain,new_stress_yz,facecolors='none',edgecolors='b')
        title(titlename+' Shortened')
        xlabel('True strain along the yz-axis')
        ylabel('True Stress along the yz-axis (MPa)')
        xlim([0,np.max(new_strain)+0.05*np.max(new_strain)])
        ylim([np.min(new_stress_yz),np.max(new_stress_yz)-100])
        stressyzshortfigname = begfigname + '_Stress_Strainyz_Short_' + TodayDate + '.pdf'
        savefig(stressyzshortfigname)
        clf()
        
        #Save data for use in R
        sh_R_data = np.zeros((len(new_strain),2))
        sh_R_data[:,0] = new_stress_yz
        sh_R_data[:,1] = new_strain
        csvtitle = sim_dat_file_name.split('.')[0] + '_ShyzData' + '.csv'
        np.savetxt(csvtitle,sh_R_data,delimiter=",")
        print("Data file ready for R analysis has been saved as {}\n".format(csvtitle))
        print("Plots saved to {} and {}\n".format(stressyzfigname,stressyzshortfigname)) 

        fig_close()
    else:
        print("dir is either not specified in the thermo data or....")
