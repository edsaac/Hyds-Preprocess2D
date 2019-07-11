#
#////////////////////////////////////////////////////////////////////////
#                                                                       #
#                                 SHP2GEO.py                            # 
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
# Purpose:    Script takes in a group of ESRI vector files (SHP) of a 
#             geometry and produces a geometry file (CSV) used by the 
#             buildGEO.py  program to generate a geometry file (GEO) used 
#             by gmsh.
#
# Needs:      Python3, sys, os, shutil, qgis.bin
#
# Usage:      python3 buildGEO.py <mode> <input.shp> <optional.shp> <output.csv>
#
# where:
# --> mode: a string that defines how the script will behave according 
#           to the type of vector file used as input. SHP files may 
#           correspond to polygons, lines or points.
#
#     --> p: a polygon SHP is taken to define the boundaries of the 
#            computational domain. It may contain rings (holes) in its 
#            configuration. Only one attribute is necessary to define the
#            element size which has to be called "R_m". 
#
#     --> i: a polygon SHP is taken to define the boundaries of the 
#            computational domain. It may contain rings (holes) in its 
#            configuration. Only one attribute is necessary to define the
#            element size which has to be called "R_m". An additional polygon
#            SHP is added to define different "R_m" values on the vertices
#            of the boundary polygon on the <optional.shp> field. 
#
#     --> l: a line SHP is taken to define hard lines on the 
#            computational domain. It may contain as many lines as desired, 
#            however, they have to be inside the computational domain. 
#            Closed polygons generate errors when meshing. One attribute 
#            is necesary defining the element size which has to be called 
#            "R_m"
#
#     --> v: a points SHP is taken to define hard points on the 
#            computational domain. It may contain as many points as desired, 
#            however, they have to be inside the computational domain. 
#            Repeated points generate errors when meshing. One attribute 
#            is necesary defining the element size which has to be called 
#            "R_m"
#
# --> input.shp: a string that defines the path to the ESRI vector file from 
#                which the geometry will be taken.
#
# --> output.csv: a string that defines the path to the CSV file where the 
#                 geometrical entities will be written                       
#
# Bibliography & Useful links:
# -- https://gis.stackexchange.com/questions/279874/using-qgis3-processing-algorithms-from-standalone-pyqgis-scripts-outside-of-gui
# -- https://github.com/pprodano/pputils
# -- https://gis.stackexchange.com/questions/287576/where-to-find-documentation-on-algorithm-parameters-when-writing-scripts-in-qgis
#
#////////////////////////////////////////////////////////////////////////

import sys, os, shutil
from pathlib import Path

#Import Qgis 
from qgis.core import *
from qgis.processing import *
from qgis.utils import *
from qgis.analysis import *
from PyQt5.QtCore import QVariant

#////////////////////////////////////////////////////////////////////////
#                         def Functions                                 #
#////////////////////////////////////////////////////////////////////////

###   Removes and creates a folder
def resetFolder(folderName):                
    try: 
        os.rmdir(folderName)                          
    except FileNotFoundError:
        print("Create temporal folder")
    except OSError:
        shutil.rmtree(folderName, ignore_errors=True) 
    os.makedirs(folderName)

###   Checks if a layer is valid when loaded to QGIS
def checkLayer(layerName):                  
    print("Layer is valid?:  " + str(layerName.isValid()))
    if not layerName.isValid():
        print("Layer failed to load!")
        #sys.exit("Byee \n")
    else:
        print("Layer loaded sucessfully")

###   Creates an empty file. If the file exists, it will be erased
def touchFile(fileName):
    if not os.path.exists(fileName):
        Path(fileName).touch()
    else:
        os.remove(fileName)
        Path(fileName).touch()

###   Takes a polygon SHP and returns a line SHP
def polyToLine(inputFile,outputFile):
    
    #Load and check polygon layer to environment
    Outline_PolyLayer = QgsVectorLayer(inputFile, "OutlinePolygon")
    checkLayer(Outline_PolyLayer)

    #Convert Polygon to Lines
    params = {
        'INPUT':Outline_PolyLayer, 
        'OUTPUT':outputFile
        }
    processing.run("native:polygonstolines", params )

###   Takes a line SHP and returns its vertices as a points SHP    
def lineToVertex(inputFile,outputFile):
    
    #Load and check line layer to environment
    Outline_LineLayer = QgsVectorLayer(inputFile, "OutlineLine")
    checkLayer(Outline_LineLayer)
    
    ##Convert Lines to Vertices
    params = {
        'INPUT':Outline_LineLayer, 
        'OUTPUT':outputFile
        }
    processing.run("native:extractvertices", params )

###   Takes a points SHP and returns a points layer with its coordinates
###     as attributes of each feature. [Output should be CSV]
def vertexToXYCSV(inputFile,outputFile):
    
    #Creates an empty SHP file for scratching the X coordinate
    path2VertexX = "../SHP_Files/.Temp/3.OutlineVertexX.shp"
    touchFile(path2VertexX)

    #Load input points SHP layer to environment
    Outline_VertexLayer = QgsVectorLayer(inputFile, "OutlineVertex")
    checkLayer(Outline_VertexLayer)

    #Calculates the X-coordinates as a new field on a SHP
    params = {'INPUT':Outline_VertexLayer,
        'FIELD_NAME': "X_m",
        'FIELD_TYPE': 0,
        'FIELD_LENGHT':10,
        'FIELD_PRECISION':3,
        'NEW_FIELD':True,
        'FORMULA':"$x",
        'OUTPUT':path2VertexX
            }
    processing.run("qgis:fieldcalculator", params )

    #Load new points SHP layer (the one with X calculated) to environment
    Outline_VertexLayerX = QgsVectorLayer(path2VertexX, "OutlineVertexX")
    checkLayer(Outline_VertexLayerX)

    #Calculates the Y-coordinates as a field on a newfile 
    #   (given by the output format)
    params = {'INPUT':Outline_VertexLayerX,
        'FIELD_NAME': "Y_m",
        'FIELD_TYPE': 0,
        'FIELD_LENGHT':10,
        'FIELD_PRECISION':3,
        'NEW_FIELD':True,
        'FORMULA':"$y",
        'OUTPUT':outputFile                               #Should be .csv
            }
    processing.run("qgis:fieldcalculator", params )

###   Takes a points layer and writes a new points layer with a field Rx_m
###     obtained when comparing the R_m specified in the inputFile and the 
###     R_m given in mapFile. This is used when different element sizes are
###     specified over the computational domain boundary, e.g., inlets.
def mapElementSizes(inputFile,mapFile,outputFile):
    
    #Load and checks points layer to environment
    Outline_VertexLayer = QgsVectorLayer(inputFile, "OutlineVertex")
    checkLayer(Outline_VertexLayer)
    
    #Load and checks the element sizes map layer to environment
    Map_Sizes = QgsVectorLayer(mapFile, "MapElementSize")
    checkLayer(Map_Sizes)

    #Create scratch layer for the Union result
    path2Unioned = "../SHP_Files/.Temp/4.Unioned.shp"
    touchFile(path2Unioned)

    #The R_m attribute for element sizes taken from Map is passed to the 
    #   vertices affected by the mapFile
    params = {
        'INPUT':Outline_VertexLayer,
        'OVERLAY':Map_Sizes,
        'OVERLAY_FIELDS_PREFIX':"O_",
        'OUTPUT':path2Unioned
        }
    processing.run("native:union", params )

    #Load and checks the scratch points layer to environment
    Unioned_V = QgsVectorLayer(path2Unioned, "UnionedV")
    checkLayer(Unioned_V)

    #Create another scratch layer for the result of the decision between 
    #   the original element size R_m or the one mapped from mapFile
    path2Calc = "../SHP_Files/.Temp/5.RMIN.shp"
    touchFile(path2Calc)

    #The decision is the minimal value of R_m 
    params = {'INPUT':Unioned_V,
        'FIELD_NAME': "Rx_m",
        'FIELD_TYPE': 0,
        'FIELD_LENGHT':10,
        'FIELD_PRECISION':3,
        'NEW_FIELD':True,
        'FORMULA':"min(R_m,O_R_m)",
        'OUTPUT':path2Calc
            }
    processing.run("qgis:fieldcalculator", params )

    #Load and checks to environment the points layer with the new field 
    #   "Rx_m" that contains the definitive element size attribute
    RCalc_V = QgsVectorLayer(path2Calc, "RCalculated")
    checkLayer(RCalc_V)

    #Sorts the values by the "vertex_index" expression to keep the 
    #   topology of the original polygon
    params = {'INPUT':RCalc_V,
        'EXPRESSION' : "to_int( \"vertex_ind\" )",
        'ASCENDING'  : True,
        'NULLS_FIRST': False,
        'OUTPUT':outputFile
            }
    processing.run("native:orderbyexpression", params )

#////////////////////////////////////////////////////////////////////////

##  Start QGIS  ##
QgsApplication.setPrefixPath('/usr', True)
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
qgs = QgsApplication([], True)
qgs.initQgis()

#Add plugins and processing algorithms
sys.path.append('/usr/share/qgis/python/plugins/')
import processing
from processing.core.Processing import Processing

#Add native functions
Processing.initialize()
qgs.processingRegistry().addProvider(QgsNativeAlgorithms())

####################################################################

#Start QGIS Project
project = QgsProject.instance()

#Clean temporal files
resetFolder("../SHP_Files/.Temp")

### Retrieves SHP Conversor Mode
#### p | polygon         : SHP polygon
#### i | heteropolygon   : SHP polygon + SHP polygon
#### l | lines           : SHP lines
#### v | vertices        : SHP points
execMode = str(sys.argv[1]).lower()

if   execMode in ["p","polygon"]:
    path2Polygon = str(sys.argv[2])                        #Outline Polygon SHP << INPUT
    path2Line = "../SHP_Files/.Temp/1.OutlineLine.shp"     #Outline Line SHP path
    path2Vertex = "../SHP_Files/.Temp/2.OutlineVertex.shp" #Outline Vertices SHP path
    path2VertexXY = str(sys.argv[3])                       #Output CSV + XY Coordinates >> OUTPUT

    touchFile(path2Line)
    touchFile(path2Vertex)
    touchFile(path2VertexXY)

    polyToLine(path2Polygon,path2Line)              #SHP Polygon   >> SHP Lines
    lineToVertex(path2Line,path2Vertex)             #SHP Lines     >> SHP Vertices
    vertexToXYCSV(path2Vertex,path2VertexXY)        #SHP Vertices  >> CVS XY Vertices
    print("SHP2GEO polygon ~OK~:  " + str(sys.argv[2]) + " > " + str(sys.argv[3]))

elif execMode in ["i","heteropolygon"]:
    path2Polygon = str(sys.argv[2])                        #Outline Polygon SHP << INPUT
    path2SizeMap = str(sys.argv[3])                        #Outline Polygon SHP << INPUT
    path2Line = "../SHP_Files/.Temp/1.OutlineLine.shp"     #Outline Line SHP path
    path2Vertex = "../SHP_Files/.Temp/2.OutlineVertex.shp" #Outline Vertices SHP path
    path2UnionV = "../SHP_Files/.Temp/3.VertexMapped.shp"  #Outline Vertices SHP path
    path2VertexXY = str(sys.argv[4])                       #Output CSV + XY Coordinates >> OUTPUT

    touchFile(path2Line)
    touchFile(path2Vertex)
    touchFile(path2UnionV)
    touchFile(path2VertexXY)

    polyToLine(path2Polygon,path2Line)                     #SHP Polygon   >> SHP Lines
    lineToVertex(path2Line,path2Vertex)                    #SHP Lines     >> SHP Vertices
    mapElementSizes(path2Vertex,path2SizeMap,path2UnionV)  #SHP Vertices  >> SHP Mapped Vertices
    vertexToXYCSV(path2UnionV,path2VertexXY)               #SHP Mapped V  >> CVS XY Vertices
    print("SHP2GEO iPolygon ~OK~:  " + str(sys.argv[2]) + \
        " + " + str(sys.argv[3]) + "> " + str(sys.argv[4]))

elif execMode in ["l","line"]:
    path2Line = str(sys.argv[2])                           #Outline Line SHP path
    path2Vertex = "../SHP_Files/.Temp/2.OutlineVertex.shp" #Outline Vertices SHP path
    path2VertexXY = str(sys.argv[3])                       #Output CSV + XY Coordinates >> OUTPUT

    touchFile(path2Vertex)
    touchFile(path2VertexXY)

    lineToVertex(path2Line,path2Vertex)             #SHP Lines     >> SHP Vertices
    vertexToXYCSV(path2Vertex,path2VertexXY)        #SHP Vertices  >> CVS XY Vertices
    print("SHP2GEO Lines ~OK~:  " + str(sys.argv[2]) + " > " + str(sys.argv[3]))

elif execMode in ["v","vertices"]:
    path2Vertex = str(sys.argv[2])                         #Outline Vertices SHP path
    path2VertexXY = str(sys.argv[3])                       #Output CSV + XY Coordinates >> OUTPUT

    touchFile(path2VertexXY)

    vertexToXYCSV(path2Vertex,path2VertexXY)        #SHP Vertices  >> CVS XY Vertices
    print("SHP2GEO Vertices ~OK~:  " + str(sys.argv[2]) + " > " + str(sys.argv[3])) 

else:
    print("Unrecognized parameter:  " + str(sys.argv[1]))

#Delete temporal folder
shutil.rmtree("../SHP_Files/.Temp", ignore_errors=True)

