import sys, os, shutil, csv, re
from pathlib import Path

###   Reads a CSV file and returns a whole row, a whole column or a
###     single item
def getCommaFile(fileName, row = -1, col= -1):
    #Reads the CSV file from the given path
    try: 
        PointFile = open(fileName)
        rawPointFile = list(csv.reader(PointFile))                       
        PointFile.close()
    except FileNotFoundError:
        print("CSV file could not be found")

    #Checks non-empty file
    if len(rawPointFile) < 1 :
        print(str(fileName) + " is empty :S \n")
        sys.exit("Bye!")
    
    #Returns a single row of the CSV file
    if row != -1 and col == -1:
        
        try:
            return rawPointFile[row]
        except IndexError:
            print("Row could not be found")

    #Return a single column of the CSV file
    elif row == -1 and col != -1:
        try:
            colFile=[]
            for row in range(len(rawPointFile)):
                colFile.append(rawPointFile[row][col])
            return colFile
        except IndexError:
            print("Column could not be found")

    #Return a single value of the CSV file
    elif row != -1 and col != -1:
        try:
            return rawPointFile[row][col]
        except IndexError:
            print("Item could not be found")
    else:
        print("dafuq")

###   From the CSV headers identifies the position of certain attribute
def getColumn(xID,fileName):
    try:
        header = getCommaFile(fileName, row = 0)
        return(header.index(xID))
    except ValueError:
        print(str(xID) + " column could not be found")

###   Finds the line number where a string is found (needle), similarly 
###     to the .sh program "grep"
def getLineIndex(haystack,needle):
    try:
        return(haystack.index(needle))
    except ValueError:
        print("Pattern could not be found")


###   Returns the i-th element of each element from a list of strings
###     e.g. ["A B C","1 2 3"] >> [B,2]
def getColumnContents(haystack,colIndex,separator = " "):
    colIndex -= 1 #index start at 0
    column = []
    for line in haystack : 
        X = line.split()
        column.append(X[colIndex])
    return column



###   From a .msh mesh, extracts a list of the elements corresponding to
###     just a dimension. By default it extracts TRIANGLES
def filterMSHElement(listElements,dimension = 2):
    X = getColumnContents(listElements,2)
    filteredElements = []
    for i in range(len(X)):
        if int(X[i]) == dimension :
            filteredElements.append(listElements[i])
    return filteredElements