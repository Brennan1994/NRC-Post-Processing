from hec.script import *
from hec.heclib.dss import *
from hec.io import *
from hec.heclib.util import HecTime
import java
import csv



#This funtion breaks down a list of list into a single list of a specified row (like the first entry in each list) . requires the list of lists, and a row counter as inputs.
def listOfListsToRows(ListofLists,rowCounter):
    row = [item[rowCounter] for item in ListofLists]
    return row

##############    DEFINING SOURCE DATA , OUTPUT LOCATION, HEADERS ################
#Source file: Must contain only the data you're trying to spit out. 
fileName = r"D:\NRC-WAT\Brennan_Chart_Production\1_DSS_Files_for_Figures\New folder\32_flow.dss"
#Output file: You can name this anything and place it anywhere
outFile = open(r'D:\NRC-WAT\Brennan_Chart_Production\1_DSS_Files_for_Figures\New folder\32_flow.csv', 'wb')
#open the dss file
dssFile = HecDss.open(fileName)
# Create List of pathnames in dss file 
pathnames = dssFile.getPathnameList()
#creating headers
formatedList = []
for eachPathname in pathnames:
    formatedList.append(eachPathname)
    formatedList.append('')
header1 = formatedList
#writing headers
writer = csv.writer(outFile)
writer.writerow(header1)

masterList = []
for eachPathname in pathnames:
#############   TEEING UP  LIST CREATION ###################################
#Pulling the data from DSS
    myPDC = dssFile.get(eachPathname)
##############   CREATING Y (Value) LIST ###################################
    valuesList = myPDC.yOrdinates[0]
##############   CREATING X (Probability) LIST    ##########################
    probList = myPDC.xOrdinates
##############   APPENDING THE MASTER LISTS    #############################
    masterList.append(probList)
    masterList.append(valuesList)
##############     TESTING LISTS FOR VALIDITY      #########################
    for eachProb in probList:
        if eachProb > 1:
            print eachPathname
    if len(probList) != len(valuesList):
            print eachPathname
#################         WRITING        ##################################
rowCounter = 0
for x in range(0,len(masterList[0])):
    row = listOfListsToRows(masterList, rowCounter)
    rowCounter = rowCounter+1
    writer.writerow(row)
outFile.close()


