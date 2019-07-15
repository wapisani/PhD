#This script will take the Tg data (temp and density) and plot it.
#It will find the Tg temp by fitting two lines to the data.
#You will need to update the breakpoint guess for your system. I recommend setting the initial guess as the Tg value for your system.
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
tgfile <-"your_file_name_here_TgData.csv"
tgdat <- read.csv(tgfile)
tgfilename <- strsplit(tgfile,"\\.")[[1]]

#create vectors for temp and dens
tgtemp <- tgdat[,1]
tgdens <- tgdat[,2]

#fit a regular linear model to data, this is for the segmented command
lin.mod <- lm(tgdens ~ tgtemp)

#use segmented package to calculated breakpoint (Tg)
segmented.mod <- segmented::segmented(lin.mod, seg.Z = ~tgtemp, psi=416)
#Define moving average function
mav <- function(x,n=1000){filter(x,rep(1/n,n),sides=2)}


tgdens_ma <- mav(tgdens,8500)

# Get point at tg_value
tg_value <- segmented.mod$psi[2]
tg_value_stderror <- segmented.mod$psi[3]
tg_y_value <- segmented.mod$coefficients[2]*tg_value+segmented.mod$coefficients[1]

# Save regular plot to pdf
pdf(paste(tgfilename[1],"pdf",sep="."))
plot(tgtemp,tgdens,col="blue",xlim=c(300,520),ylim=c(1.24,1.34),xlab = 'Temperature (Kelvin)',ylab = 'Density (g/cc)')
#plot(tgtemp,tgdens)
par(new = TRUE)
plot(segmented.mod,col="red",xlim=c(300,520),ylim=c(1.24,1.34),xlab = '',ylab = '',rug=FALSE)
par(new = TRUE)
plot(tg_value,tg_y_value,pch=24,col="white",bg="white",xlim=c(300,520),ylim=c(1.24,1.34),xlab = '',ylab = '')
dev.off()

# Save moving average plot to pdf
ma_name <- paste(tgfilename[1],"ma",sep="_")
pdf(paste(ma_name,"pdf",sep="."))
plot(tgtemp,tgdens_ma,col="lightskyblue",xlim=c(300,520),ylim=c(1.26,1.32),xlab = 'Temperature (K)',ylab = 'Density (g/cc)',cex.lab=1.5, cex.axis=1.5, cex.main=1.5, cex.sub=1.5)
#plot(tgtemp,tgdens)
#Comment out the next part if not using PEEK1013...S4_cool
par(new = TRUE)
clip(300,tg_value+30,-100,100)
abline(coef=segmented.mod$coefficients,col="black")
par(new = TRUE)
clip(tg_value-30,520,-100,100)
abline(coef=c(1.381,-0.0002156),col="black")
#And uncomment the next line
#plot(segmented.mod,col="red",xlim=c(300,500),ylim=c(1.24,1.34),xlab = '',ylab = '',rug=FALSE)
par(new = TRUE)
#Triangle is pch=24
plot(tg_value,tg_y_value,pch=21,col="black",bg="black",xlim=c(300,520),ylim=c(1.26,1.32),xlab = '',ylab = '',cex.lab=1.5, cex.axis=1.5, cex.main=1.5, cex.sub=1.5)
dev.off()

# Write Tg value to file
tg_data <- data.frame(tg_value,tg_value_stderror)
write.table(tg_data, file=paste(tgfilename[1],"txt",sep="."))

