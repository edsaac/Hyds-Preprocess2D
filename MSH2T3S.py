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
# Modified:   July 10, 2019
#
# Works on:   python3
#
# Purpose:    Script takes in a MSH (v.2) file generated on gmsh and produces 
#             a t3s mesh file (MSH) recognized by BlueKenue(C). 
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
# -- http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format-version-2-_0028Legacy_0029
#
#////////////////////////////////////////////////////////////////////////

import csv, sys, os, re

#Retrieve path of files from the arguments passed to the script
pathToMSHFile = str(sys.argv[1])            #MSH  input file 
pathToT3SFile = str(sys.argv[2])            #T3S output file

#////////////////////////////////////////////////////////////////////////
#                         def Functions                                 #
#////////////////////////////////////////////////////////////////////////

###   Reads a MSH file without parsing by columns
def readFile(pathToFile):
    try: 
        X = (open(pathToFile,"r"))
        return(X)
    except FileNotFoundError:
        print("MSH file could not be found")

###   Finds the line number where a string is found (needle), similarly 
###     to the .sh program "grep"
def getLineIndex(haystack,needle):
    try:
        return(haystack.index(needle))
    except ValueError:
        print("Pattern could not be found")

###   Takes a text file and splits it as a list of strings. Each line
###     on the file is an element of the list
def parseFile(varFile):
    try: 
        X = str(varFile.read())
        return(X.split("\n"))
    except FileNotFoundError:
        print("MSH for parsing file could not be found")

###   Returns the i-th element of each element from a list of strings
###     e.g. ["A B C","1 2 3"] >> [B,2]
def getColumnContents(haystack,colIndex,separator = " "):
    colIndex -= 1 #index start at 0
    column = []
    for line in haystack : 
        X = line.split()
        column.append(X[colIndex])
    return column

###   Builds a list of three columns separated by a space in T3S format
def buildT3S_3Col(Col1,Col2,Col3):
    T3S = []
    for i in range(len(Col1)):
        line = str(Col1[i]) + " " + str(Col2[i]) + " " + str(Col3[i])
        T3S.append(line)
    return(T3S)

###   Appends a list to a file
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

###   Resets and creates a new file
def resetT3SFile(nameFile):
    try: 
        with open(nameFile,"w") as outFile:
            outFile.write('')
            outFile.close()
    except FileNotFoundError:
        print("T3S file could not be found when reseting")

###   From a .msh mesh, extracts a list of the elements corresponding to
###     just a dimension. By default it extracts TRIANGLES
def filterMSHElement(listElements,dimension = 2):
    X = getColumnContents(listElements,2)
    filteredElements = []
    for i in range(len(X)):
        if int(X[i]) == dimension :
            filteredElements.append(listElements[i])
    return filteredElements

###   Generates the Header for the T3S file
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

#////////////////////////////////////////////////////////////////////////

#Create a new empty T3S File
resetT3SFile(pathToT3SFile)

#Read MSH file and organize it as a list
MSHFile = readFile(pathToMSHFile)
Raw_MSH = parseFile(MSHFile)

#Extract Nodes from the MSH File
startNodes = getLineIndex(Raw_MSH,"$Nodes")      
endNodes   = getLineIndex(Raw_MSH,"$EndNodes")   
Nodes_MSH  = Raw_MSH[startNodes+2:endNodes]

#Extract Coordinates of the extracted list of nodes
manyNodes  = int(Raw_MSH[startNodes+1])
xCoord_MSH = getColumnContents(Nodes_MSH,2)
yCoord_MSH = getColumnContents(Nodes_MSH,3)

#Build T3S Node List
Nodes_T3S  = buildT3S_3Col(xCoord_MSH,yCoord_MSH,xCoord_MSH)

#Extract Elements from the MSH File
startElements = getLineIndex(Raw_MSH,"$Elements")
endElements   = getLineIndex(Raw_MSH,"$EndElements")
Elements_MSH  = Raw_MSH[startElements+2:endElements]

#Extract only 2d Triangles from the MSH elements
Triangles_MSH = filterMSHElement(Elements_MSH,2)

#Extract only the structure of elements from the list
manyElements   = int(len(Triangles_MSH))
p1Elements_MSH = getColumnContents(Triangles_MSH,6)
p2Elements_MSH = getColumnContents(Triangles_MSH,7)
p3Elements_MSH = getColumnContents(Triangles_MSH,8)

#Build T3S Element List
Elements_T3S  = buildT3S_3Col(p1Elements_MSH,p2Elements_MSH,p3Elements_MSH)

#Build T3S Header
Header_T3S  = buildT3S_Header(manyNodes,manyElements)

#Write T3S Files
appendFile(Header_T3S,pathToT3SFile,True)       #Header
appendFile(Nodes_T3S,pathToT3SFile)             #Nodes
appendFile(Elements_T3S,pathToT3SFile)          #Triangles

print("MSH2T3S ~OK~: " + str(sys.argv[1]) + " > " + str(sys.argv[2]))