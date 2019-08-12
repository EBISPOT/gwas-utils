#!/usr/bin/env Rscript

library("zoo")

# Required column names:
requiredColumns = c("Year", "TA", "GWAS")
currentDate = format(Sys.time(), "%Y-%m-%d")

# Extracting command line arguments. 
# Important: input check is not done at this point, it's done in the caller script.
args = commandArgs(trailingOnly=TRUE)
inputFile = args[1]

##
## Reading and testing input file:
##

df = read.table(inputFile, sep = ",", header = TRUE, as.is = TRUE)

# Checking if all the required columns are present in the dataframe:
for( req in requiredColumns ){
    if( ! req %in% colnames(df)){
        cat(sprintf("[Error] The required column (%s) is missing. Exiting.\n", req))
        quit()
    }
}

cat("[Info] Data loaded. Data looks good.\n")


## 
## Derive some values:
##
df['cumulative_TA'] =  cumsum(df$TA)
df['cumulative_GWAS'] = cumsum(df$GWAS)
df['GWAS_only'] = df['cumulative_GWAS'] - df['cumulative_TA']
df['ratio'] = df['cumulative_TA'] /df['GWAS_only']

##
## Plotting data:
##
darkredColor = adjustcolor('#A23123', 0.6)
darkGreenColor = adjustcolor('#87AC5F', 0.6)
pdf(sprintf("TA_vs_GWAS_stackedBar_%s.pdf",currentDate), width = 10, height = 6) # Comment this row out if no pdf is needed.

par(mar = c(5.1, 6.1, 4.1, 2.1))
b = barplot(t(as.matrix(df[,c('GWAS_only','cumulative_TA')])), cex.axis = 1.4,
  xlab="", col=c(darkredColor,darkGreenColor), las = 2, ylim = c(0,4500))
mtext("Number of papers", side =2, line = 4.3, cex = 1.5)
axis(1, at = b, labels = df$Year, cex.axis = 1.5, lwd = 0, lwd.ticks = 1)

legend('topleft', legend = c("TA papers only", "GWAS papers"), cex = 1.6,
       col = c(darkGreenColor,darkredColor), pch = 15, pt.cex = 4,bty = "n")


# Adding text:
text(b + 0.1,df$cumulative_GWAS + 200, labels = sprintf("%.1f%%", df$ratio*100), cex = 1.1)
dev.off()