#This script will compute the bulk modulus from a plot of pressure vs volumetric strain.
#
#License information:
#
#MIT License
#
#Copyright (c) 2019 Will Pisani
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

if (Sys.info()['sysname']=="Linux"){
  setwd("/path/to/directory/on/linux")
} else {
# Paths in Windows in R require \\ instead of \
 setwd("C:\\path\\to\\directory\\on\\Windows") 

}

#Read in csv file
bkfile <-"your_file_name_here_BK_RData.csv"
bkdat <- read.csv(bkfile)
bkfilename <- strsplit(bkfile,"\\.")[[1]]

#create vectors for pressure and volumetric strain
bkpress <- bkdat[,1] *1.01325*10^5/1000000 # Converting atm to MPa
bkvolstrain <- bkdat[,2]
bkendpoint <- length(bkpress)
bkpress <- bkpress[1:bkendpoint]
bkvolstrain <- bkvolstrain[1:bkendpoint]

#fit a regular linear model to data, this is for the segmented command
lin.mod <- lm(bkpress ~ bkvolstrain)

#use segmented package to calculated breakpoint (bk)
segmented.mod <- segmented::segmented(lin.mod, seg.Z = ~bkvolstrain, psi=-0.05)
#Define moving average function
#mav <- function(x,n=1000){filter(x,rep(1/n,n),sides=2)}


#bkdens_ma <- mav(bkdens,1500)

# Get point at bk_value
# Get slope of first line
bk_modulus <- summary(segmented.mod)$coefficients[2,1]/1000 # Going from MPa to GPa
bk_modulus <- abs(round(bk_modulus,2)) # Round to 2 decimal places
bk_value <- segmented.mod$psi[2]
bk_value_stderror <- segmented.mod$psi[3]
bk_y_value <- segmented.mod$coefficients[2]*bk_value+segmented.mod$coefficients[1]

# Save regular plot to pdf
pdf(paste(bkfilename[1],"pdf",sep="."))
plot(bkvolstrain,bkpress,col="blue",xlim=c(0,min(bkvolstrain)),ylim=c(-2000,3500),main = paste("Bulk Modulus=",bk_modulus,"GPa"),xlab = 'Volumetric strain',ylab = 'Pressure (MPa)')
#plot(bktemp,bkdens)
par(new = TRUE)
plot(segmented.mod,col="red",xlim=c(0,min(bkvolstrain)),ylim=c(-2000,3500),xlab = '',ylab = '',rug=FALSE)
par(new = TRUE)
plot(bk_value,bk_y_value,pch=24,col="white",bg="white",xlim=c(0,min(bkvolstrain)),ylim=c(-2000,3500),xlab = '',ylab = '')
dev.off()