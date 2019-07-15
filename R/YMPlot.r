#This script will find the yield point, Young's modulus, and 
#Poisson's ratio.
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
ymfile <- "your_file_name_here_sim_data_YMxData.csv"
ymfilename <- strsplit(ymfile,"\\.")[[1]]
ymdat <- read.csv(ymfile)

#create vectors for stress and strain
ymstress <- ymdat[,1]
ymaxstrain <- ymdat[,2]
ymtrstrain <- ymdat[,3]
ymtime <- ymdat[,4]

#Create new vectors containing data before chain slippage, change accordingly.

ymendpoint <- length(ymaxstrain)

ymstressnew <- ymstress[1:ymendpoint]
ymaxstrainnew <- ymaxstrain[1:ymendpoint]
ymtrstrainnew <- ymtrstrain[1:ymendpoint]

#If the beginning of Poisson's ratio plot is super weird, just do ymaxstrainnew[500:ymendpoint]
psaxstrainnew <- ymaxstrainnew
pstrstrainnew <- ymtrstrainnew
# psaxstrainnew <- ymaxstrainnew[600:1700]
# pstrstrainnew <- ymtrstrainnew[600:1700]

#fit a regular linear model to data, this is for the segmented command
lin.mod <- lm(ymstressnew ~ ymaxstrainnew)
lin2.mod <- lm(pstrstrainnew ~ psaxstrainnew)

#use segmented package to calculated breakpoint(s), for multiple use c(value,value) after psi=
#Young's modulus, value for psi is guess
segmented.mod <- segmented::segmented(lin.mod, seg.Z = ~ymaxstrainnew, psi=0.02)

#Get breakpoint x-axis value for use in the Poisson's ratio breakpoint analysis
ps_psi_guess <- segmented.mod$psi[2]

#use segmented package to calculate breakpoint for Poisson's ratio data
#Uses x-axis breakpoint value from Young's modulus analysis
segmentedps.mod <- segmented::segmented(lin2.mod, seg.Z = ~psaxstrainnew, psi=0.04)

#Extract coefficients
#Set more breaks to 1 if multiple breakpoints are needed
morebreaks <- 0

#Young's modulus average and standard error
ym_value <- summary(segmented.mod)$coefficients[2,1]
ym_stderror <- summary(segmented.mod)$coefficients[2,2]
if (morebreaks == 1) {
  ym_strainvalue1 <- segmented.mod$psi[3]
  ym_strainvalue2 <- segmented.mod$psi[4]
} else {
  ym_strainvalue <- segmented.mod$psi[2]
}

#This is used in the Young's modulus plot  
modulus_value <- round(ym_value/1000,digits=1)  # To get it into GPa

#Intercept of line
ym_intercept <- summary(segmented.mod)$coefficients[1,1]
ym_intstderror <- summary(segmented.mod)$coefficients[1,2]


#Extract Poisson's ratio coefficients

#Poisson's ratio and standard error
ps_value <- summary(segmentedps.mod)$coefficients[2,1]
ps_stderror <- summary(segmentedps.mod)$coefficients[2,2]

#Poisson intercept
ps_intercept <- summary(segmentedps.mod)$coefficients[1,1]
ps_intstderror <- summary(segmentedps.mod)$coefficients[1,2]

#Write matrix
if (morebreaks == 1) {
  df_ymps <- data.frame(ym_value,ym_stderror,ym_strainvalue1,ym_strainvalue2,ym_intercept,ym_intstderror,ps_value,ps_stderror,ps_intercept,ps_intstderror)
  
} else {
  df_ymps <- data.frame(ym_value,ym_stderror,ym_strainvalue,ym_intercept,ym_intstderror,ps_value,ps_stderror,ps_intercept,ps_intstderror)
}
#Write coefficients to file
write.table(df_ymps,file=paste(ymfilename[1],"txt",sep="."),sep="\t")

# Get point at YM_value
ym_value <- segmented.mod$psi[2]
ym_value_stderror <- segmented.mod$psi[3]
ym_y_value <- segmented.mod$coefficients[2]*ym_value+segmented.mod$coefficients[1]

#Get point at Poisson value
ps_ax_value <- segmentedps.mod$psi[2] # x-axis value of breakpoint
ps_tr_value <- segmentedps.mod$coefficients[2]*ps_ax_value+ps_intercept

# Create moving average for journal article
ma <- function(x,n=5){filter(x,rep(1/n,n),sides=2)}
ymstressma <- ma(ymstress)
ymaxstrainma <- ma(ymaxstrain)

# Need to plot full stress strain curve
# pdf(paste(ymfilename[1],"_PEEKpaper_fullcurve",".pdf",sep=""))
# par(cex.lab=1.5,cex.axis=1.5)
# plot(ymaxstrainma,ymstressma,col="black",cex.lab=3,xlim=c(0,0.2),ylim=c(-50,max(ymstressnew)),xlab = 'True Strain',ylab = 'True Stress (MPa)')
# dev.off()

#Plot breakpoint analysis for Young's modulus
pdf(paste(ymfilename[1],"_zoomedin",".pdf",sep=""))
par(cex.lab=1.5,cex.axis=1.5)
# The below is for normal analysis. The second plot is for journal articles.
plot(ymaxstrainnew,ymstressnew,col="black",xlim=c(0,max(ymaxstrainnew)),ylim=c(min(ymstressnew),max(ymstressnew)),main = paste("Young's Modulus=",modulus_value,"GPa"),xlab = 'True Strain',ylab = 'True Stress (MPa)')
# plot(ymaxstrainnew,ymstressnew,col="black",xlim=c(0,max(ymaxstrainnew)),ylim=c(-50,max(ymstressnew)),xlab = 'True Strain',ylab = 'True Stress (MPa)')
#par(new = TRUE)
plot(segmented.mod,col="red",lwd=3,xlim=c(0,max(ymaxstrainnew)),ylim=c(min(ymstressnew),max(ymstressnew)),xlab = '',ylab = '',rug=FALSE,add=TRUE)
#par(new = TRUE)
points(ym_value,ym_y_value,pch=21,cex=4,col="lightskyblue",bg="lightskyblue",xlim=c(0,max(ymaxstrainnew)),ylim=c(min(ymstressnew),max(ymstressnew)),xlab = '',ylab = '')
dev.off()

#Plot breakpoint analysis for Poisson's ratio
ympoissonname <- paste(ymfilename[1],"_Poisson",sep="")
pdf(paste(ympoissonname,"pdf",sep="."))
plot(psaxstrainnew,pstrstrainnew,col="blue",xlim=c(0,max(psaxstrainnew)),ylim=c(-0.1,0.1),main = paste("Poisson's ratio =",abs(round(ps_value,digits=4))),xlab = 'True Axial Strain',ylab = 'True Transverse Strain')
par(new = TRUE)
plot(segmentedps.mod,col="red",xlim=c(0,max(psaxstrainnew)),ylim=c(-0.1,0.1),xlab = '',ylab = '',rug=FALSE)
par(new = TRUE)
plot(ps_ax_value,ps_tr_value,pch=24,col="black",bg="black",xlim=c(0,max(psaxstrainnew)),ylim=c(-0.1,0.1),xlab = '',ylab = '')
dev.off()




