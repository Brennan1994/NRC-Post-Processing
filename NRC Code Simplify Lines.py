from hec.script import *
from hec.heclib.dss import *
from hec.io import *
from hec.heclib.util import HecTime
from operator import itemgetter
import java
import csv
from math import *

#This Script takes a dss file with just the full frequency curve from a HEC-WAT run and simplifies it down to a specified number of points. 
#The output is a csv file with the filtered down data.


def CoordinateListFromSeperateLists(listOfX, listOfY):
    # takes the individual lists of x and y coordinates from DSS and makes them into a list of lists [a list of coordinates that are stored in 2 item lists]
    # Returns the list of coordinates
    coordinateList = []
    for count in range(0,len(listOfX)):
        pairingList = []
        pairingList.append(listOfX[count])
        pairingList.append(listOfY[count])
        coordinateList.append(pairingList)
    return coordinateList          

def Area(point0,point1,point2):
    # taken from Will's area function in LifeSimGIS by the same name. Takes 3 points and returns the area of the triangle formed by them. 
    x=0
    y=1
    return abs( ((point0[x]*point1[y]) + (point1[x]*point2[y]) + (point2[x]*point0[y]) - (point1[x]*point0[y]) - (point2[x]*point1[y]) - (point0[x]*point2[y])) * 0.5 )

def VisvaligamWhyattSimplify(numToKeep, coordinateList):
    # Stolen from Will's function in LifeSimGIS by the same name. Thins a line down to the specified amount of points based on the VW algorithm.
    #http://bost.ocks.org/mike/simplify/
    removeLimit = (len(coordinateList) - numToKeep) # This determines the number of times we're going to go through this process to end with our desired number of points
    for i in range(0,(removeLimit)): 
        minIndex = 1 # This sets the first minIndex(the points that get removed) as the second point in the line. Don't want to chop off the end. 
        minArea = Area(coordinateList[0], coordinateList[1], coordinateList[2]) # this is the area of our first triangle. It's the baseline we'll start our first comparison to.
        for j in range(2, len(coordinateList) - 2): # starting at 2, because we're gonna start calculating areas, and we already calculated area 1. 
            #ending at minus 2 because we don't want the last point, and the len function uses counting numbers, so we have to reduce by an extra -1 to account for 0 index
            tmpArea = Area(coordinateList[j-1], coordinateList[j], coordinateList[j+1]) #calculates the area of the triangle and stores it
            if (tmpArea < minArea): # Checks to see if this is smaller than the smallest area we've calculated. If it is, we store it's index and make it the new area to compare to
                minIndex = j 
                minArea = tmpArea
        del coordinateList[minIndex]
    return coordinateList

def GetInvCDF(probability):
    # Stolen from Will's statistics Library
    #Taylor Series Coefficients
    c0 = 2.515517
    c1 = 0.802853
    c2 = 0.010328
    d1 = 1.432788
    d2 = 0.189269
    d3 = 0.001308
    
    #Checking the input, and ensuring validity 
    q = probability
    if q==0.5:
        zScore = 0
        return zScore
    if q<=0:
        q = 0.000000000000001
    if q>=1:
        q = 0.999999999999999

    #Conversion happens here
    t = sqrt(log(1/pow(q,2)))
    x = t - (c0+c1*t+c2*pow(t,2)) / (1+d1*t+d2*pow(t,2)+d3*pow(t,3))
    zScore = x
    return zScore

def VisvaligamWhyattSimplifyOptimized(numToKeep, coordinateList):
    print("filtering...")
    
    removeLimit = (len(coordinateList) - numToKeep) # This determines the number of times we're going to go through this process to end with our desired number of points
    areaList = []
    areaList.append(999999.99999)#place holder so area index will match coordinate index 
    for j in range(1, len(coordinateList) - 1): 
        tmpArea = Area(coordinateList[j-1], coordinateList[j], coordinateList[j+1])
        areaList.append(tmpArea) # corresponding area is always going to be coordinate list index -1 
    for each in range(0,removeLimit):    
        minIndex = areaList.index(min(areaList))
        #deletes the coordinate with the smallest area, removes it's area from the area list, and removes the areas around it the areas of points before and after which are now invalid
        del coordinateList[minIndex]
        del areaList[minIndex]
        del areaList[minIndex-1]
        del areaList[minIndex]
        
        #Recalculate the areas around the removed point
        newArea0 = Area(coordinateList[minIndex-2], coordinateList[minIndex-1], coordinateList[minIndex])
        newArea1 = Area(coordinateList[minIndex-1], coordinateList[minIndex], coordinateList[minIndex+1])
        newArea2 = Area(coordinateList[minIndex], coordinateList[minIndex+1], coordinateList[minIndex+2])
        
        #Insert new areas into the area list
        areaList.insert(minIndex-1,newArea2)
        areaList.insert(minIndex-1,newArea1)
        areaList.insert(minIndex-1,newArea0)
        
        #ProgressReporting
        if each % 100 == 0:
            print each
         
    return coordinateList


def CoordinateListToSeperateLists(coordinateList, xOryIndicator):
    #This takes a list of lists, and extracts either the x or y coordinates into their own seprate list. if xOryIndicator is specified as 0, the user gets X values, otherwise y.
    outputList = []
    for eachCoordinate in coordinateList:
        if xOryIndicator == 0:
            outputList.append(eachCoordinate[0])
        else:
            outputList.append(eachCoordinate[1])
    return outputList

#This function breaks down a list of list into a single list of a specified row (the first entry in each list) . requires the list of lists, and a row counter as inputs.
def listOfListsToRows(ListofLists,rowCounter):
    row = [item[rowCounter] for item in ListofLists]
    return row

##############    DEFINING SOURCE DATA , OUTPUT LOCATION, HEADERS ################ 
#Source file: Must contain only the data you're trying to spit out. 
fileName = r"D:\NRC-WAT\Brennan_Chart_Production\1_DSS_Files_for_Figures\Existing_Conditions\TimeWindow\32.65FlowFreqOnly.dss"
#Output file: You can name this anything and place it anywhere
outFile = open(r'D:\NRC-WAT\Brennan_Chart_Production\1_DSS_Files_for_Figures\Existing_Conditions\TimeWindow\32.65FlowFreqOnly.csv', 'wb')
#open the dss file
dssFile = HecDss.open(fileName)
# Create List of pathnames in dss file 
pathnames = dssFile.getPathnameList()

writer = csv.writer(outFile)
for eachPathname in pathnames:
#############   TEEING UP  LIST CREATION ###################################
#Pulling the data from DSS
    myPDC = dssFile.get(eachPathname)
##############   CREATING Y (Value) LIST ###################################
    valuesList = myPDC.yOrdinates[0]
##############   CREATING X (Probability) LIST    ###############################
    probList = myPDC.xOrdinates
##############   Creating zScore LIST        ###############################
    zScoreList = []   
    for eachProb in probList:
        zScore = GetInvCDF(eachProb)
        zScoreList.append(zScore)
#############    MERGING THE LISTS INTO 1    ###############################
    coordinateList = CoordinateListFromSeperateLists(zScoreList,valuesList)
#############    FILTERING OUT POINTS ON THE LINE #########################
# SPECIFY ENDING NUMBER OF POINTS IN THE FIRST ARGUMENT 
    shortenedList = VisvaligamWhyattSimplify(500, coordinateList)
############      WRITE IT OUT      ########################################
    for eachCoordinate in shortenedList:
        writer.writerow(eachCoordinate)
outFile.close()
print('Done!')
