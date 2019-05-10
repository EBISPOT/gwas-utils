#/usr/bin/env Rscript

library("stringr")

# Required column names:
requiredColumns = c("year", "studies", "studiesSS", "publication", "publicationSS")
currentDate = format(Sys.time(), "%Y-%m-%d")

# Extracting command line arguments. 
# Important: input check is not done at this point, it's done in the caller script.
args = commandArgs(trailingOnly=TRUE)
startYear = args[1]
inputFile = args[2]

##
## Reading and testing input file:
##

summaryStatsDf = read.table(inputFile, header = TRUE, as.is = TRUE, sep = ",")

# Checking if all the required columns are present in the dataframe:
for( req in requiredColumns ){
    if( ! req %in% colnames(summaryStatsDf)){
        cat(sprintf("[Error] The required column (%s) is missing. Exiting.\n", req))
        quit()
    }
}

cat("[Info] Data loaded. Data looks good.\n")

##
## Extract date from input file name:
##

fileDate = str_extract(inputFile, "\\d{4}-\\d{2}-\\d{2}")
fileDate = format(Sys.time(), "%h %Y")

# If the date cannot be extracted from the input filename, we assume the file was generated on the same day:
if ( ! is.na(fileDate) ){
    fileDate = format(as.POSIXct(fileDate,format="%Y-%m-%d"), "%h %Y")
}

studyMain = paste("Publication with summary statistics\nas of ", fileDate)
publicationMain = paste("Publication with summary statistics\nas of ", fileDate)
cumulativeMain = paste("All data as of\n", fileDate)

##
## Plotting functions:
##

# Get cumulative data:
getCumulativeData = function(summaryStatsDf){
    cumultiveMatrix = matrix(c(sum(summaryStatsDf$studies) - sum(summaryStatsDf$studiesSS), 
         sum(summaryStatsDf$studiesSS),
         sum(summaryStatsDf$publication) - sum(summaryStatsDf$publicationSS), 
         sum(summaryStatsDf$publicationSS)), ncol = 2)
    colnames(cumultiveMatrix) = c('Studies', 'Publications')
    return(cumultiveMatrix)
}

# Function to generate plot:
drawBars = function(inputMatrix, mainLabel){
    
    # Define colors:
    ssColor = adjustcolor("goldenrod", alpha.f = 0.7)
    nossColor = adjustcolor("cornflowerblue", alpha.f = 0.7)
    
    # Calculate percentages:
    percentages = round(inputMatrix[2,] / colSums(inputMatrix) * 100,0)

    # Get the max:
    maxHeight = max(colSums(inputMatrix)) * 1.2

    # Plotting bars:
    xPos = barplot(inputMatrix, 
            col=c(nossColor,ssColor),
            ylim = c(0,maxHeight), cex.axis = 2.1,
            las = 2, xaxt='n', ann=FALSE,
           main = mainLabel, cex.main=2
    )
    
    # Adding axis:
    axis(1, at = xPos, 
        labels = colnames(inputMatrix), 
         lty = 0, cex.axis = 2.1)

    # Adding percentages to the columns:
    text(x = xPos, y = colSums(inputMatrix) + (maxHeight * 0.05), 
         labels = paste(percentages, "%", sep = ""), cex = 2.3)
}

##
## Doing some calculations:
##

# Subtract studies:
summaryStatsDf['studyPlot'] = summaryStatsDf$studies - summaryStatsDf$studiesSS

# Subtract publication:
summaryStatsDf['pubPlot'] =  summaryStatsDf$publication - summaryStatsDf$publicationSS

##
## Running individual plots:
##

## Filter studies:
studyMatrix = t(as.matrix(summaryStatsDf[summaryStatsDf$year >= startYear, c('studyPlot', 'studiesSS')]))
colnames(studyMatrix) = summaryStatsDf[summaryStatsDf$year >= startYear,'year']

# Saving data:
png(sprintf("studies_%s.png", currentDate), width = 600, height = 600)
drawBars(studyMatrix, studyMain)
dev.off()

## Filter publication:
publicationMatrix = t(as.matrix(summaryStatsDf[summaryStatsDf$year >= startYear, c('pubPlot', 'publicationSS')]))
colnames(publicationMatrix) = summaryStatsDf[summaryStatsDf$year >= startYear,'year']

# Saving plot into file:
png(sprintf("publications_%s.png", currentDate), width = 600, height = 600)
drawBars(publicationMatrix, publicationMain)
dev.off()

## Prepare cumulative data:
cumultiveMatrix = getCumulativeData(summaryStatsDf)

# Saving plot into file:
png(sprintf("cumulative_%s.png", currentDate), width = 400, height = 600)
drawBars(cumultiveMatrix, cumulativeMain)
dev.off()

##
## Generate multiplot
## 

# Initialize plot:
png(sprintf("all_plots_%s.png", currentDate), width = 1300, height = 500)
layout(matrix(c(1,1,2,2,3), nrow = 1, ncol = 5, byrow = TRUE))

par(mar=c(4.1,6.1,4.1,2.1))
drawBars(studyMatrix, studyMain)
drawBars(publicationMatrix, publicationMain)
drawBars(cumultiveMatrix, cumulativeMain)

dev.off()

