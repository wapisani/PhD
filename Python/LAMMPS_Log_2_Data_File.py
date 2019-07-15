# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 11:52:09 2015

@author: wapisani
This script will parse LAMMPS log files and extract the data to a text file. This script is the first step for analyzing elastic modulus, shear modulus, CTE, Tg, bulk modulus etc with my set of Python and R scripts.
Currently only works with final logs (*.log.lammps).
If you have access to Pizza.py from the LAMMPS website, I recommend developing your own thermo plotter and data extractor using Pizza.py. Pizza.py makes it really easy, much easier than this script does.

Script Usage:
Honestly, Python works best in an IDE like Spyder because it's easier to debug,
but you can also run this from the terminal like so: python LAMMPS_Log_2_Data_File.py.
This script requires numpy to be installed in the terminal.

Potential improvements:
Turn this script into a function capable of being called from other scripts.
Extend this script to extract multiple run sections' thermo data. Only works with one.

License information:

MIT License

Copyright (c) 2019 Will Pisani

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# Import necessary libraries
#import time
import os
import getpass
import re
import numpy as np
#from pylab import clf,plot,xlabel,ylabel,title,savefig,scatter,xlim,ylim,legend
#from PyPDF2 import PdfFileMerger, PdfFileReader

# Change to directory where log is located
os.chdir("path/to/directory")
logname = "your_log_name_here.log.lammps"



#Set all switches to off in the beginning and turn them on only if they
#are found in the filename
#My scripts follow a certain naming convention and this script will only work with that convention.
#For example, PEEK0911RxEqS5.log.lammps
#PEEK is the polymer, 0911 is the date Sept11, Rx is ReaxFF, Eq is equilibration, S5 is sample 5
varreaxff = 0   # switch for ReaxFF
varopls = 0     # switch for OPLS
varriff = 0     # switch for Reactive IFF
vartg = 0       # switch for Tg
varym = 0       # switch for YM
vardfy = 0      # switch for densification
vareq = 0       # switch for Equilibration
varcr = 0       # switch for crystal
varsh = 0       # switch for shearing
varlog = 0      # switch for log files
varul = 0       # switch for unloading sims
varbk = 0       # switch for bulk modulus

#Determine which type of analysis to run
#If the letters OP are present in logname, then the force field is OPLS.
if logname.find('OP') > 0: #If the letters are not present, find returns -1.
    force_field = 'OPLS' 
    varopls = 1
    
    
    #If the letters Cr are present in logname, then set varcr =1.
    if logname.find('Cr') > 0: #Running a crystalline PEEK sim
        varcr = 1
        
        
    elif logname.find('Dfy') > 0: #Running a densification sim
        vardfy = 1
        
       
    
    #If the letters Rx are present in logname, then the force field is ReaxFF.
elif logname.find('Rx') > 0: 
    force_field = 'ReaxFF'
    
    varreaxff = 1
    
    #If the letters Tg are present in logname, then set vartg = 1.
    if logname.find('Tg') > 0:
        vartg = 1
        
        if logname.find('Cr') > 0: #Running crystalline PEEK in ReaxFF
            varcr = 1
            
    #If the letters YM are present in logname, then set varym = 1.
    elif logname.find('YM') > 0 or logname.find('ym') > 0:
        varym = 1
        
        if logname.find('Cr') > 0: #Running crystalline PEEK in ReaxFF
            varcr = 1
            
    elif logname.find('Ul1') > 0 or logname.find('Ul2') > 0 or logname.find('Ul3') > 0:
        varul = 1   
        
    #If the letters Eq are present in logname, then set vareq = 1.
    elif logname.find('Eq') > 0:
        vareq = 1
        
        if logname.find('Cr') > 0: #Running crystalline PEEK in ReaxFF
            varcr = 1    
            
    elif logname.find('Sh') > 0: # Running shearing simulation
        varsh = 1
        
        if logname.find('Cr') > 0: #Running crystalline PEEK in ReaxFF
            varcr = 1
    
    elif logname.find("BK") > 0 or logname.find("bk") > 0: # Running bulk modulus in ReaxFF
        varbk = 1
    
    
        
    else:
        print("What are you running in ReaxFF that isn't YM, Tg, or E1?")
elif logname.find('riff') > 0:
    varriff = 1
    

#Moving average analysis flag    
varma = 0

# Determine if log file is a .log or a .in.o###### file
if logname.split('.')[1] == 'log':
    varlog = 1

#Change titlename based on analysis type
#OPLS sims
if varopls == 1:
    #Crystalline PEEK
    if varcr == 1:
        #Extract base filename
        begfigname = logname.split('.')[0]
        
        #Get sample number from filename
        sampnum = ' Sample ' + begfigname[len(begfigname)-1]
        
        #Make title for figures
        titlename = 'PEEK Crystal ' + force_field + sampnum
        
    #Amorphous PEEK, densifying
    elif vardfy == 1:
        #Extract base filename
        begfigname = logname.split('.')[0]
        
        #Get sample number from filename
        sampnum = ' Sample ' + begfigname[len(begfigname)-1]
        
        #Make title for figures
        titlename = 'PEEK Amorphous ' + force_field + 'Densification' + sampnum
        
    #More if statements for polymerization, PEEK/GNP combined, etc.

#ReaxFF sims
elif varreaxff == 1:
    if vartg == 1: #Tg sims
    
        #Extract base filename
        begfigname = logname.split('.')[0]
        
        #Get sample number from filename
        sampnum = ' Sample ' + begfigname[len(begfigname)-1]
        
        #Make title for figures
        titlename = 'PEEK Tg ' + force_field + sampnum
        
    elif varym == 1: #YM sims
        #Extract base filename
        begfigname = logname.split('.')[0]
        
        #Get sample number from filename
        if logname.split('.')[1] == 'log':
            #My YM sim logs have the direction they are being strained in as
            #the last character (_2, y-dir) so the sample number is before _2.
            sampnum = ' Sample ' + begfigname[len(begfigname)-3]
        else:
            #If it's just the running log [something].in.sh[something] then
            #the sample number is the last character
            sampnum = ' Sample ' + begfigname[len(begfigname)-1]
        
        #Make title for figures
        titlename = 'PEEK YM ' + force_field + sampnum
        
    elif vareq == 1: #ReaxFF equilibrations sims
        #Extract base filename
        begfigname = logname.split('.')[0]
    
        #Get sample number from filename
        sampnum = ' Sample ' + begfigname[len(begfigname)-1]
        
        #Make title for figures
        titlename = 'PEEK Eq ' + force_field + sampnum
    
    elif varul == 1: # ReaxFF unloading sims
        #Extract base filename
        begfigname = logname.split('.')[0]
    
        #Get sample number from filename
        sampnum = ' Sample ' + begfigname[len(begfigname)-1]
        
        #Make title for figures
        titlename = 'PEEK Unloading ' + force_field + sampnum
        
    elif varbk == 1: # ReaxFF bulk modulus sims
        #Extract base filename
        begfigname = logname.split('.')[0]
    
        #Get sample number from filename
        sampnum = ' Sample ' + begfigname[len(begfigname)-1]
        
        #Make title for figures
        titlename = 'PEEK Bulk Modulus ' + force_field + sampnum
    
    #More if statements based on what's needed





#-----------------------------Open data file for reading-----------------------

# If the log file being analyzed is a .log file
if varlog == 1:
    
    #Open log file for reading
    with open(logname) as frunlog:
        
        i = 0 #Initialize counting variable
        
        #This flag is used so that the script doesn't break before progressing to
        #the actual numerical data. Sometimes there are some warnings before 
        #the data starts.
        fine_to_break = 0 #Set flag to 0 at start
        
        #This flag is set when the first 'run' command is found.
        #The second 'run' command has the number of time steps after it.
        run_step_flag = 0
        
        thermocatrownum = 50000000000
        #setting this variable to an extremely large number prevents errors down the line
        
        #This loop will get a list of the thermodynamics categories and the 
        #number of categories to preallocate memory.
        for line in frunlog:
            if varym == 1 or varsh == 1 or varul == 1 or varriff == 1: #If analyzing a Young's mod or shear mod simulation
                if i == 0:
                    #Get the frequency of log dumps in time steps
                    dump_spacing = int(re.sub("\s\s+"," ",line).split(' ')[4])

                if run_step_flag == 0:
                    if re.sub("\s\s+"," ",line).split(' ')[0] == 'run':
                        run_step_flag = 1 #Set flag to 1 when first occurence of 'run' is found
                        
                elif run_step_flag == 1: #If flag is set to 1
                    if re.sub("\s\s+"," ",line).split(' ')[0] == 'run':
                        #Get the total number of time steps
                        total_timesteps = int(re.sub("\s\s+"," ",line).split(' ')[1])
                        run_step_flag = 2 #Set flag to 2 once timesteps has been found
                        
                    
                if line.split(' ')[0] == 'Time':
                    #Get list of thermodynamics categories
                    thermocat = line.rsplit()
                    thermocat_string = line
                    
                    #Get line number of thermodynamics categories line
                    thermocatrownum = i
                    #Get number of categories
                    thermonum = len(thermocat)
                    
                    #End loop
                    break
                    
            elif vartg == 1 and varcr == 0: #If amorphous Tg
                if i == 0:
                    #Get the frequency of log dumps in time steps
                    # This number will need to be changed to match your simulations. It corresponds to the thermo output frequency.
                    dump_spacing = 500
                 
                # Get the total number of time steps 
                if re.sub("\s\s+"," ",line).split(' ')[0] == 'run':
                    
                    total_timesteps = int(re.sub("\s\s+"," ",line).split(' ')[1])
                    
                if line.split(' ')[0] == 'Step':
                    #Get list of thermodynamics categories
                    thermocat = line.rsplit()
                    thermocat_string = line
                    
                    #Get line number of thermodynamics categories line
                    thermocatrownum = i
                    #Get number of categories
                    thermonum = len(thermocat)
                    
                    #End loop
                    break
            elif vartg == 1 and varcr == 1: #If crystalline Tg
                if i == 1: #On the second line
                    #Get the frequency of log dumps in time steps
                    # This number will need to be changed to match your simulations. It corresponds to the thermo output frequency.
                    dump_spacing = 500
                    
                # Get the total number of time steps 
                if re.sub("\s\s+"," ",line).split(' ')[0] == 'run':
                    
                    total_timesteps = int(re.sub("\s\s+"," ",line).split(' ')[1])
            
                if line.split(' ')[0] == 'Step':
                    #Get list of thermodynamics categories
                    thermocat = line.rsplit()
                    thermocat_string = line
                    
                    #Get line number of thermodynamics categories line
                    thermocatrownum = i
                    #Get number of categories
                    thermonum = len(thermocat)
                    
                    #End loop
                    break
            elif varbk == 1: #If bulk modulus sims
                if i == 1: #On the second line
                    #Get the frequency of log dumps in time steps
                    # This number will need to be changed to match your simulations. It corresponds to the thermo output frequency.
                    dump_spacing = 500
            
                # Get the total number of time steps 
                if re.sub("\s\s+"," ",line).split(' ')[0] == 'run':
                    
                    total_timesteps = int(re.sub("\s\s+"," ",line).split(' ')[1])
            
                if line.split(' ')[0] == 'Time':
                    #Get list of thermodynamics categories
                    thermocat = line.rsplit()
                    thermocat_string = line
                    
                    #Get line number of thermodynamics categories line
                    thermocatrownum = i
                    #Get number of categories
                    thermonum = len(thermocat)
                    
                    #End loop
                    break
            
            
            else:
                print("You're attempting to get a data file for an unknown simulation type.")
                break #End loop
            #Increment counting variable
            i+=1 
        
        #------------Preallocate memory------------------
        # Calculate number of rows needed
        thermo_rows = total_timesteps/500 + 1 #total_timesteps/dump_spacing + 1
        
        # Allocate memory
        thermodata = np.zeros((thermo_rows,thermonum))
        
        #------------Get data---------------------------
        # Start looping through data in file
         
        
        k = 0 # Initialize new counting variable
        #This for loop starts at the line in the file after the line the previous
        #loop broke on.
        for line in frunlog:
            
            #Check if numerical data is done
            if line.split(' ')[0] == 'Loop' or line.split(' ')[0] == 'WARNING:':
                break #Break out of the loop
                    
                
                
            # Replace multiple spaces with one space, strip leading spaces, 
            # and split the line at every space.
            data = re.sub("\s\s+"," ",line).lstrip(' ').rsplit()
            
            # Convert data into floats
            data = [float(single_data) for single_data in data]
            
            # Assign data to thermodata matrix
            thermodata[k,:] = data
            
            # Increment counting variable
            k += 1
            
            
                
        
    #------------Write data to file----------------
    output_name = logname.split('.')[0] + '_sim_data.txt'
    with file(output_name, 'w') as data_file:
        #Write information about shape of matrix to file
        data_file.write('# Array shape: {0}\n'.format(thermodata.shape))
        
        #Write thermo categories to file
        data_file.write('# {}'.format(thermocat_string))
        
        #Write simulation data to file
        np.savetxt(data_file,thermodata)

# If the file being analyzed is a running log file
else:
    #Open log file for reading
    with open(logname) as frunlog:
        
        i = 0 #Initialize counting variable
        
        #This flag is used so that the script doesn't break before progressing to
        #the actual numerical data. Sometimes there are some warnings before 
        #the data starts.
        fine_to_break = 0 #Set flag to 0 at start
        
        
        thermocatrownum = 50000000000
        #setting this variable to an extremely large number prevents errors down the line
        
        # Start iterating through log file
        for line in frunlog:
            if varsh == 1 or varym == 1: # If simulation is shearing or tensile straining
                if line.split(' ')[0] == 'Time':
                    #Get list of thermodynamics categories
                    thermocat = line.rsplit()
                    thermocat_string = line
                    
                    #Get line number of thermodynamics categories line
                    thermocatrownum = i
                    #Get number of categories
                    thermonum = len(thermocat)
                    
                    # Initialize numpy matrix
                    thermodata = np.zeros((1,thermonum))
                    
                if i > thermocatrownum: # Start data collection
                    # Replace multiple spaces with one space, strip leading spaces, 
                    # and split the line at every space.
                    data = re.sub("\s\s+"," ",line).lstrip(' ').rsplit()
            
                    # Convert data into floats
                    data = [float(single_data) for single_data in data]
                    
                    #Convert data into numpy array
                    data = np.asarray(data)
                    
                    # Create new numpy array
                    newdata = np.zeros((1,thermonum))
                    
                    # Set contents of newdata equal to data
                    newdata[0,:] = data
                    
                    if i == thermocatrownum + 1:
                        thermodata[0,:] = newdata
                    else:
                        thermodata = np.append(thermodata,newdata,axis=0)
                        
                i += 1 # Increment counting variable
                    
    #------------Write data to file----------------
    output_name = logname.split('.')[0] + '_partial_data.txt'
    with file(output_name, 'w') as data_file:
        #Write information about shape of matrix to file
        data_file.write('# Array shape: {0}\n'.format(thermodata.shape))
        
        #Write thermo categories to file
        data_file.write('# {}'.format(thermocat_string))
        
        #Write simulation data to file
        np.savetxt(data_file,thermodata)       
                    
                    
                    