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
fileName = r"D:\NRC-WAT\Brennan_Chart_Production\1_DSS_Files_for_Figures\New folder\PreExistingConditions_DSS\74.46_NRC.dss"
#open the dss file
dssFile = HecDss.open(fileName)
# Create List of pathnames in dss file 
pathnames = dssFile.getPathnameList()
count = 0
for eachPathname in pathnames:
#############   TEEING UP  LIST CREATION ###################################
#Pulling the data from DSS
    myPDC = dssFile.get(eachPathname)
##############   CREATING Y (Value) LIST ###################################
    valuesList = myPDC.yOrdinates[0]
##############   CREATING X (Probability) LIST    ##########################
    probList = myPDC.xOrdinates
##############   APPENDING THE MASTER LISTS    #############################
##############     TESTING LISTS FOR VALIDITY      #########################
# This value is the elevation that is only attained in events which contain a dam breach
    if max(valuesList) > 495: 
    	count = count + 1
print count
