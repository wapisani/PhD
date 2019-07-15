#This script will take the Tg data (temp and density) and plot it.
#It will find the CTE below the Tg and above the Tg.
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
tgfile <-"your_file_name_here_CTE_RData.csv"
tgdat <- read.csv(tgfile)
tgfilename <- strsplit(tgfile,"\\.")[[1]]

#create vectors for temp, linear expansion, volume expansion
tgtemp <- tgdat[,1]
tglin <- tgdat[,2]
tgvol <- tgdat[,3]
tgdens <- tgdat[,4]
tgtemp <- rev(tgtemp)
tglin <- rev(tglin)
tgvol <- rev(tgvol)
tgdens <- rev(tgdens)
#fit a regular linear model to data, this is for the segmented command
lin.mod <- lm(tgdens ~ tgtemp)

#use segmented package to calculated breakpoint (Tg)
segmented.mod <- segmented::segmented(lin.mod, seg.Z = ~tgtemp, psi=416)
#Define moving average function
#mav <- function(x,n=1000){filter(x,rep(1/n,n),sides=2)}


#tgdens_ma <- mav(tgdens,1500)

# Get point at tg_value
tg_value <- segmented.mod$psi[2]
tg_value_stderror <- segmented.mod$psi[3]
tg_y_value <- segmented.mod$coefficients[2]*tg_value+segmented.mod$coefficients[1]

# Save regular plot to pdf
pdf(paste(tgfilename[1],"pdf",sep="."))
plot(tgtemp,tgdens,col="blue",xlim=c(300,500),ylim=c(1.24,1.34),xlab = 'Temperature (Kelvin)',ylab = 'Density (g/cc)')
#plot(tgtemp,tgdens)
par(new = TRUE)
plot(segmented.mod,col="red",xlim=c(300,500),ylim=c(1.24,1.34),xlab = '',ylab = '',rug=FALSE)
par(new = TRUE)
plot(tg_value,tg_y_value,pch=24,col="white",bg="white",xlim=c(300,500),ylim=c(1.24,1.34),xlab = '',ylab = '')
dev.off()

#tg_value <- 459.5

# Begin CTE analysis
# These ranges will need to be changed for each individual sample/run.
# tg_above and tg_below are the ranges the CTE equation will be fitted to
tg_above <- c(tg_value,500)
tg_below <- c(300,tg_value)



# Find indices of tgtemp where the above ranges occur
tg_above_lower_index <- which(tgtemp > tg_above[1])[1]
tg_above_upper_index <- tail(which(tgtemp > tg_above[2]),1)
tg_below_lower_index <- which(tgtemp > tg_below[1])[1]
tg_below_upper_index <- which(tgtemp > tg_below[2])[1]

# Get ranges for fitting
cte_linear_above <- tglin[tg_above_lower_index:tg_above_upper_index]
cte_linear_below <- tglin[tg_below_lower_index:tg_below_upper_index]
cte_volume_above <- tgvol[tg_above_lower_index:tg_above_upper_index]
cte_volume_below <- tgvol[tg_below_lower_index:tg_below_upper_index]
temp_below <- tgtemp[tg_below_lower_index:tg_below_upper_index]
temp_above <- tgtemp[tg_above_lower_index:tg_above_upper_index]

# Fit a linear model to the volumetric CTE data below Tg
vcte_below_mod <- lm(formula = cte_volume_below ~ temp_below -1)
vcte_above_mod <- lm(formula = cte_volume_above ~ temp_above -1)
lcte_below_mod <- lm(formula = cte_linear_below ~ temp_below -1)
lcte_above_mod <- lm(formula = cte_linear_above ~ temp_above -1)

# Save volumetric CTE plot to pdf
pdf(paste(tgfilename[1],"vCTE.pdf",sep="_"))
plot(tgtemp,tgvol,col="blue",xlim=c(300,500),ylim=c(min(tgvol),max(tgvol)),xlab="Temperature (K)",ylab="Volumetric expansion (dV/V times 1000)")
text(375,31,sprintf("CVTE = %3.2E/K",vcte_below_mod$coefficients[2]*10^-3),pos=2,col="red")
text(375,29,sprintf("CVTE = %3.2E/K",vcte_above_mod$coefficients[2]*10^-3),pos=2,col="brown")
par(new = TRUE)
abline(v=tg_value)
text(tg_value-20,-10,sprintf("Tg=%3.0f K",tg_value))
par(new = TRUE)
# The clip command can be used to limit some line using lines or abline
clip(tg_below[1],tg_below[2],-100,100)
abline(lm(cte_volume_below ~ temp_below),col="red")
par(new = TRUE)
clip(tg_above[1],tg_above[2],-100,100)
abline(lm(cte_volume_above ~ temp_above),col="brown")
dev.off()

# Save linear CTE plot to pdf
pdf(paste(tgfilename[1],"lCTE.pdf",sep="_"))
plot(tgtemp,tglin,col="blue",xlim=c(300,500),ylim=c(min(tglin),max(tglin)),xlab="Temperature (K)",ylab="Linear expansion (dV/V times 1000)")
text(375,11,sprintf("CLTE = %3.2E/K",lcte_below_mod$coefficients[2]*10^-3),pos=2,col="red")
text(375,9,sprintf("CLTE = %3.2E/K",lcte_above_mod$coefficients[2]*10^-3),pos=2,col="brown")
par(new = TRUE)
abline(v=tg_value)
text(tg_value-20,-3,sprintf("Tg=%3.0f K",tg_value))
par(new = TRUE)
# The clip command can be used to limit some line using lines or abline
clip(tg_below[1],tg_below[2],-100,100)
abline(lm(cte_linear_below ~ temp_below),col='red')
par(new = TRUE)
clip(tg_above[1],tg_above[2],-100,100)
abline(lm(cte_linear_above ~ temp_above),col='brown')

dev.off()

# Save moving average plot to pdf
# ma_name <- paste(tgfilename[1],"ma",sep="_")
# pdf(paste(ma_name,"pdf",sep="."))
# plot(tgtemp,tgdens_ma,col="blue",xlim=c(300,500),ylim=c(1.24,1.34),xlab = 'Temperature (Kelvin)',ylab = 'Density (g/cc)')
# #plot(tgtemp,tgdens)
# par(new = TRUE)
# plot(segmented.mod,col="red",xlim=c(300,500),ylim=c(1.24,1.34),xlab = '',ylab = '',rug=FALSE)
# par(new = TRUE)
# plot(tg_value,tg_y_value,pch=24,col="white",bg="white",xlim=c(300,500),ylim=c(1.24,1.34),xlab = '',ylab = '')
# dev.off()

# Get slope coefficients into variables
clte_above <- lcte_above_mod$coefficients[2]
clte_below <- lcte_below_mod$coefficients[2]
cvte_above <- vcte_above_mod$coefficients[2]
cvte_below <- vcte_below_mod$coefficients[2]

# Write Tg value to file
tg_data <- data.frame(tg_value,tg_value_stderror,clte_above,clte_below,cvte_above,cvte_below)
write.table(tg_data, file=paste(tgfilename[1],"txt",sep="."))

