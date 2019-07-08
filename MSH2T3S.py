#
#////////////////////////////////////////////////////////////////////////
#                                                                       #
#                                 MSG2T3S.py                            # 
#                                                                       #
#////////////////////////////////////////////////////////////////////////
#
# Author:     Edwin
# 
# Date:       July 8, 2019
#
# Modified:   July 8, 2019
#
# Works on:   python3
#
# Purpose:    Script takes in a MSH file generated on gmsh and produces 
#             a t3s mesh file (MSH) recognized by BlueKenue(C)
#
# Needs:      Python3, csv, sys, os, shutil
#
# Usage:      python3 MSH2T3S.py <input.msh> <output.t3s>
#
# where:
# --> input.msh: a string that defines the path to MSH file from where the
#                gmsh mesh is to be read.
#
# --> output.t3s: a string that defines the path to the T3S file where the 
#                 BlueKenue mesh will be written.                       
#
# Bibliography & Useful links:
# -- https://github.com/pprodano/pputils
#
#////////////////////////////////////////////////////////////////////////

import csv, sys, os, re

##INPUT File
pathToMSHFile = str(sys.argv[1])

##OUTPUT File
pathToT3SFile = str(sys.argv[2])

def readFile(pathToFile):
    try: 
        X = (open(pathToFile,"r"))
        return(X)
    except FileNotFoundError:
        print("CSV file could not be found")
def getLineIndex(haystack,needle):
    try:
        return(haystack.index(needle))
    except ValueError:
        print("Pattern could not be found")
def parseFile(varFile):
    X = str(varFile.read())
    return(X.split("\n"))
def getColumnContents(haystack,colIndex,separator = " "):
    colIndex -= 1 #index start at 0
    column = []
    for line in haystack : 
        X = line.split()
        column.append(X[colIndex])
    return column
def buildT3S_3Col(Col1,Col2,Col3):
    T3S = []
    for i in range(len(Col1)):
        line = str(Col1[i]) + " " + str(Col2[i]) + " " + str(Col3[i])
        T3S.append(line)
    return(T3S)
def appendFile(what, whereToFile = pathToT3SFile,isString = False):
    if not isString :
        with open(whereToFile,"a") as outFile:
            for i in range(len(what)):
                outFile.write(str(what[i]) + "\n")
            outFile.close()
    else:
        with open(whereToFile,"a") as outFile:
            outFile.write(str(what))
            outFile.close()

def resetT3SFile(nameFile):
    with open(nameFile,"w") as outFile:
        outFile.write('')
        outFile.close()
def filterMSHElement(listElements,dimension = 2):
    X = getColumnContents(listElements,2)
    filteredElements = []
    for i in range(len(X)):
        if int(X[i]) == dimension :
            filteredElements.append(listElements[i])
    return filteredElements
def buildT3S_Header(nNodes,nElements):
    header = "#########################################################################\
        \n:FileType t3s  ASCII  EnSim 1.0\
        \n# Edwin Hydraulics Centre/Saavedra Research Council (~c~) 1111-2222\
        \n# DataType                 2D T3 Scalar Mesh\
        \n#\
        \n:Application              BlackKenue\
        \n:Version                  3.3.4\
        \n:WrittenBy                edwin\
        \n:CreationDate             Fri, Jul 04, 2019 12:00 PM\
        \n#\
        \n#------------------------------------------------------------------------\
        \n:SourceFile   Z:file.excel\
        \n#\
        \n#\
        \n:AttributeName 1 BOTTOM FRICTION\
        \n#\
        \n:NodeCount " + str(nNodes) +"\
        \n:ElementCount " + str(nElements) + "\
        \n:ElementType  T3\
        \n#\
        \n:EndHeader\n"
    return(header)

#Touch T3S File
resetT3SFile(pathToT3SFile)

#Get MSH File into python
MSHFile = readFile(pathToMSHFile)
Raw_MSH = parseFile(MSHFile)

#Extract Nodes
startNodes = getLineIndex(Raw_MSH,"$Nodes")
endNodes   = getLineIndex(Raw_MSH,"$EndNodes")
Nodes_MSH  = Raw_MSH[startNodes+2:endNodes]

#Extract Coordinates of Nodes
manyNodes  = int(Raw_MSH[startNodes+1])
xCoord_MSH = getColumnContents(Nodes_MSH,2)
yCoord_MSH = getColumnContents(Nodes_MSH,3)

#Build T3S Node List
Nodes_T3S  = buildT3S_3Col(xCoord_MSH,yCoord_MSH,xCoord_MSH)

#Extract Nodes
startElements = getLineIndex(Raw_MSH,"$Elements")
endElements   = getLineIndex(Raw_MSH,"$EndElements")
Elements_MSH  = Raw_MSH[startElements+2:endElements]

#Extract 2d Triangles MSH elements
Triangles_MSH = filterMSHElement(Elements_MSH,2)

#Extract Structure of Elements
manyElements   = int(len(Triangles_MSH))
p1Elements_MSH = getColumnContents(Triangles_MSH,6)
p2Elements_MSH = getColumnContents(Triangles_MSH,7)
p3Elements_MSH = getColumnContents(Triangles_MSH,8)

#Build T3S Element List
Elements_T3S  = buildT3S_3Col(p1Elements_MSH,p2Elements_MSH,p3Elements_MSH)

#Build T3S Header
Header_T3S  = buildT3S_Header(manyNodes,manyElements)

#Write Files
appendFile(Header_T3S,pathToT3SFile,True)
appendFile(Nodes_T3S,pathToT3SFile)
appendFile(Elements_T3S,pathToT3SFile)

print("")