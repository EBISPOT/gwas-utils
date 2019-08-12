#!/usr/bin/env Rscript

# This small R util keeps track of the length of data releases and estimates when we are reaching 
# the two week and month long data releases.

##
## Function to update the table with the new data:
##
updateDF = function(df, filename, newRow){
    
    # Ask user about the details of the new data release:
    newValues = strsplit(newRow, "_")[[1]]
    cat(sprintf("[Info] New release date (YYYY/MM/DD): %s\n", newValues[1]))
    cat(sprintf("[Info] New release length (minutes): %s\n", newValues[2]))
    cat(sprintf("[Info] New association count: %s\n", newValues[3]))

    # Adding new values to dataframe:
    print(class(df$Date))
    df = rbind(df, c(newValues[1], as.integer(newValues[2]), as.integer(newValues[3])))

    # Save dataframe if file name is specified:
    newDate = gsub('/','_',newValues[1])
    newFile = gsub(".csv", paste('_',newDate,'.csv', sep =''), filename)
    write.csv(df, file = newFile,row.names=FALSE)

    # return update dataframe:
    return(df)
}

##
## Reading and processing data:
##
args = commandArgs(trailingOnly=TRUE)
filename = args[1] # Input data is read from the first command line argument
newRow = args[2] # The new row of the file: YYYY/MM/DD_#######_######
df = read.table(filename, sep = ",", header = TRUE, stringsAsFactor=FALSE) # Read file to dataframe

# Adding new data to dataframe and save to file:
df = updateDF(df, filename, newRow)

# Format columns:
df$Minutes = as.integer(df$Minutes)
df$assocCount = as.integer(df$assocCount)
df['formattedDates'] = format(as.Date(df$Date, "%Y/%m/%d"), format="%b %d")

# Calculating days:
df['Days'] = df$Minutes / (24 *60)

##
## Plot:
##

xLim = c(min(df$assocCount)*0.9, max(df$assocCount)*1.1)
yLim = c(2, max(df$Days)*1.1)

# Initialize plot:
png("test.png", width = 900, height = 600)
par(mar=c(6.1, 5.1, 4.1, 2.1))
plot(df$assocCount, df$Days, ylab = "Data release days", xlab = "Association count", 
     cex.lab = 1.7, cex = 1.6, pch = 16, col = c(rep('cornflowerblue', nrow(df)-1),'goldenrod'), 
     cex.axis = 1.6, ylim = yLim, xlim = xLim)

# Fit linear:
linear = lm(Days ~ assocCount, data = df)
coeffs = coefficients(linear)
abline(linear, col ='firebrick')

# Adding text:
text(df$assocCount*1.01, df$Days + 0.3, labels = df$formattedDates, cex = 1.2)

twoWeeks = round((14 - coeffs[1][[1]])/coeffs[2][[1]]/1000,0)
twoWeeksDist = twoWeeks - round(df$assocCount[1]/1000)
oneMonth = round((31 - coeffs[1][[1]])/coeffs[2][[1]]/1000,0)
oneMonthDist = oneMonth - round(df$assocCount[1]/1000)

# Adding prediction:
text(xLim[1] * 1.02, yLim[2] - 1, labels = sprintf("Two weeks: %sK associations away",twoWeeksDist), adj = 0, cex = 1.8)
text(xLim[1] * 1.02, yLim[2] - 2, labels = sprintf("One month: %sK associations away",oneMonthDist), adj = 0, cex = 1.8)
dev.off()


