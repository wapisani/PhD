# Ph.D. Dissertation Appendix B: LAMMPS, Python, R, MAC/GMC, etc. Scripts and Data Files

## What is this?
---
This repository contains a portion of the many, many scripts I have written and data files I have generated over the length of my PhD at [Michigan Tech](https://mtu.edu). 

## How is this repo organized?
---
The LAMMPS scripts and data files are organized by chapter and then by methodology stage. The MAC/GMC files will be under chapter 4. The Python and R scripts are largely independent of chapter and so are in their own folders at the root of the repository. 

## Why is Chapter 5 incomplete?
---
Update March 28, 2022: Chapter 5 has been published ([link](https://www.sciencedirect.com/science/article/abs/pii/S1359836821000652?via%3Dihub)). I am uploading the relevant material as I have the time and energy to do so. It may take some time before all material is uploaded. 

Original text: The entirety of chapter 5 has the potential to be [export-controlled](https://www.wikiwand.com/en/International_Traffic_in_Arms_Regulations) someday and so this is a necessary precaution. If I receive notice that chapter 5 can be released to the public, then that directory will be updated with the relevant scripts and data files once the associated journal article has been published. 



## Do I need to learn language Y to use script X?
---
No, but it is **highly, highly, highly recommended to learn Python.** In all likelihood, you will need to modify my Python and R scripts to fit your particular situation. I will not modify them for you.

## How do I use script X?
---
The general workflow for using the Python and R scripts is as follows. Use LAMMPS_Log_2_Data_File.py to extract the thermodynamic data from your log file. Then, depending on your usage, plug in the filename and directory of the text file generated by LAMMPS_Log_2_Data_file.py into one of the other Python scripts. Then from there, plug in the generated csv file into the associated R script.

For example, let's say you wanted the Young's modulus of polymerized PEEK. You run the simulation in LAMMPS and the simulation completes successfully and writes the log file to PEEK0730RxYMS1.log.lammps. Take that log file and plug in the file name and directory into LAMMPS_Log_2_Data_file.py and run it. You may need to change line 360 with the correct thermo dump frequency. If it runs without errors you should have another file called PEEK0730RxYMS1_sim_data.txt in the same directory. From here, open up YM_Analysis.py and plug in PEEK0730RxYMS1_sim_data.txt and its directory location into the script and run the program. If the simulation was run on a recent version of LAMMPS, it should complete. You should now have a plot or two as PDFs and a csv file named PEEK0730RxYMS1_sim_data_YMyData.csv. Now open up the YMPlot.r script in R Studio. Change the directory and filename and try to run the file by clicking "Source" in the top-right corner of the editor sub-window.

## What software versions do I need to run x?
---
Update March 28, 2022: I recommend installing the latest version of Anaconda Python 3 and not Python 2. Python 2 is obsolete and is no longer receiving security updates. Please do not use Python 2 unless you absolutely have to. Most of my scripts will probably run as is in Python 3.9+, but if not, they're not very long scripts and so would be easy to update to Python 3 syntax. The function [2to3](https://docs.python.org/3/library/2to3.html) would probably fix anything that doesn't run.

All Python scripts were written for Python 2.7. The PyPDF2 package will need to be installed as well as numpy and matplotlib/pylab. ~~I recommend the Anaconda Python 2.7 distribution as it includes everything needed to run my scripts.~~ The scripts will likely need to be updated for the latest 3.x version. All Python scripts were meant to be run inside an IDE like Spyder or PyCharm. R scripts will likely work with no modifications with the latest versions of R and R studio. The LAMMPS scripts were written for a variety of versions that are now a few years old, but they may still work with the latest version of [LAMMPS](https://lammps.org/). 

The MAC/GMC example input decks will work for version 4.z-2. 

## How do I obtain MAC/GMC?
---
You will need to contact the authors of [MAC/GMC](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20030014606.pdf). I cannot distribute the code.

## What does this error mean?
---
Welcome to the world of debugging code! 9/10 times Googling the error message leads to good answers on StackOverflow. 1/10 times it's something really easy to fix and we just missed it or we're trying to use the script in a way that it's not meant for.

If you're using my Python and R scripts without modification and your filename convention is vastly different from mine, you will need to modify the Python scripts to fit your convention or change your convention to my convention.

## May I contact you for help?
---
Yes, you may contact me, but I will not modify any code for you. Part of the Ph.D. process is learning how to research a problem and come up with solutions to address that problem. 

## Your code doesn't work or could use improvement.
---
With the MIT license (below), the code included in this repository is provided **AS IS**, *without any warranty that it will work for you*. Please feel free to fork this repository for your own usage, but I am the owner of the copyright for this software and the MIT license language must remain for all of my code.

## License
---
MIT License

Copyright (c) 2022 Dr. William A. Pisani

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

