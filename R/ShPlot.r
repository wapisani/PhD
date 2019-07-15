#This script will find the shear modulus. You will need to change the initial guess and may need to adjust the window of data.
#
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

#------------------------CSV file name here---------------------
shfile <- "your_file_name_here_sim_data_ShxyData.csv"


#-------------------Read in csv file-----------------------------
shfilename <- strsplit(shfile,"\\.")[[1]]
shdat <- read.csv(shfile)

#create vectors for stress and strain
shstress <- shdat[,1]
shstrain <- shdat[,2]

#Create new vectors containing data before chain slippage, change accordingly.
shendpoint <- length(shstrain)
shstress <- shstress[1:shendpoint]
shstrain <- shstrain[1:shendpoint]


#fit a regular linear model to stress-strain data, this is for the segmented command
lin.mod <- lm(shstress ~ shstrain)

#use segmented package to calculated breakpoint(s), for multiple use c(value,value) after psi=
#Young's modulus, value for psi is guess
segmented.mod <- segmented::segmented(lin.mod, seg.Z = ~shstrain, psi=0.02)

#Extract coefficients
#Set more breaks to 1 if multiple breakpoints are needed
morebreaks <- 0

#Shear modulus average and standard error
sh_value <- summary(segmented.mod)$coefficients[2,1]
sh_stderror <- summary(segmented.mod)$coefficients[2,2]
if (morebreaks == 1) {
  sh_strainvalue1 <- segmented.mod$psi[3]
  sh_strainvalue2 <- segmented.mod$psi[4]
} else {
  sh_strainvalue <- segmented.mod$psi[2]
}

#This is used in the shear modulus plot  
modulus_value <- round(sh_value/1000,digits=1)  # To get it into GPa

#Intercept of line
sh_intercept <- summary(segmented.mod)$coefficients[1,1]
sh_intstderror <- summary(segmented.mod)$coefficients[1,2]


#Write matrix
if (morebreaks == 1) {
  df_shps <- data.frame(sh_value,sh_stderror,sh_strainvalue1,sh_strainvalue2,sh_intercept,sh_intstderror)
  
} else {
  df_sh <- data.frame(sh_value,sh_stderror,sh_strainvalue,sh_intercept,sh_intstderror)
}
#Write coefficients to file
write.table(df_sh,file=paste(shfilename[1],"txt",sep="."),sep="\t")

# Get point at sh_value
sh_value <- segmented.mod$psi[2]
sh_value_stderror <- segmented.mod$psi[3]
sh_y_value <- segmented.mod$coefficients[2]*sh_value+segmented.mod$coefficients[1]

#Plot breakpoint analysis for shear modulus
pdf(paste(shfilename[1],"pdf",sep="."))
plot(shstrain,shstress,col="blue",xlim=c(0,max(shstrain)),ylim=c(min(shstress),max(shstress)),main = paste("Shear Modulus=",modulus_value,"GPa"),xlab = 'True Strain',ylab = 'True Stress (MPa)')
par(new = TRUE)
plot(segmented.mod,col="red",xlim=c(0,max(shstrain)),ylim=c(min(shstress),max(shstress)),xlab = '',ylab = '',rug=FALSE)
par(new = TRUE)
plot(sh_value,sh_y_value,pch=24,col="black",bg="black",xlim=c(0,max(shstrain)),ylim=c(min(shstress),max(shstress)),xlab = '',ylab = '')
dev.off()





