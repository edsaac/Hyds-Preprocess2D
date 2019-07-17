import sys, os, shutil, re
from pathlib import Path

###   Builds a line for the GEO file setting the new start value of
###     GEO indices of certain feature
def addLastIndex(parameter, quantity = 0, recursive = False):
    if recursive == False:
        indicator = str(parameter) + " = " + str(quantity) + ";\n" 
    else:
        indicator = str(parameter) + " = " + str(parameter) + " + " + str(quantity) + ";\n" 
    return indicator


###   Builds the "Point()" GEO features from a list of X-coordinates, 
###     Y-coordinates, Z-coordinates, indices and element sizes  
def buildGEOPoints(X,Y,Z=[],I=[],R=[]):
    ligne=['']
    for item in range(len(X)):
        i1 = int(I[item])
        x1 = float(X[item])
        y1 = float(Y[item])
        z1 = float(Z[item])
        r1 = float(R[item])
        ligne.append("Point(P+" + str(i1) + ") = {" \
                 + str(x1) +\
             "," + str(y1) +\
             "," + str(z1) +\
             "," + str(r1) + "};"
                 )
    return ligne

###   Builds the "Line()" GEO features from a list of Start-Points,
###     End-Points and indices
def buildGEOLines(I,L1,L2):
    ligne=['']
    for item in range(len(I)):
        i1 = int(I[item])
        l1 = int(L1[item])
        l2 = int(L2[item])
        ligne.append("Line(L+" + str(i1) + ") = {P+" \
                    + str(l1) +\
             ", P+" + str(l2) + "};"
                 )
    return ligne

###   From a list of data, extracts a list of features without repetitions
###     e.g., [0,1,1,2,2,3] >> [0,1,2,3]
###     It works as set() but keeps the order of the elements on the original list
def setColumn(column):
    result = []
    k = 0
    for i in range(len(column)):
        if column[i] not in result :
            result.append(column[i])
            k+=1
    return result

###   Builds a list of three columns separated by a space in T3S format
def buildT3S_3Col(Col1,Col2,Col3):
    T3S = []
    for i in range(len(Col1)):
        line = str(Col1[i]) + " " + str(Col2[i]) + " " + str(Col3[i])
        T3S.append(line)
    return(T3S)

###   Builds a list of two columns separated by a comma in CSV format
def buildCSV_2Col(Col1,Col2):
    T3S = ["Xm,Ym"]
    for i in range(len(Col1)):
        line = str(Col1[i]) + "," + str(Col2[i])
        T3S.append(line)
    return(T3S)


###   Generates the Header for the T3S file
def buildT3S_Header(nNodes,nElements,nAtrib,Atrib):
    AtribLines = "#"
    for i in range(len(nAtrib)):
        AtribLines+="\n:AttributeName " + str(nAtrib[i]) + " " + str(Atrib[i])

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
        \n#" + \
        AtribLines + \
        "\n#\
        \n:NodeCount " + str(nNodes) +"\
        \n:ElementCount " + str(nElements) + "\
        \n:ElementType  T3\
        \n#\
        \n:EndHeader\n"
    return(header)