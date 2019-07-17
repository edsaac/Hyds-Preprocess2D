#!/usr/bin/env python3
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
# Modified:   July 12, 2019
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
#     --> -p: a polygon SHP is taken to define the boundaries of the 
#            computational domain. It may contain rings (holes) in its 
#            configuration. Only one attribute is necessary to define the
#            element size which has to be called "R_m". 
#
#     --> -i: a polygon SHP is taken to define the boundaries of the 
#            computational domain. It may contain rings (holes) in its 
#            configuration. Only one attribute is necessary to define the
#            element size which has to be called "R_m". An additional polygon
#            SHP is added to define different "R_m" values on the vertices
#            of the boundary polygon on the <optional.shp> field. 
#
#     --> -l: a line SHP is taken to define hard lines on the 
#            computational domain. It may contain as many lines as desired, 
#            however, they have to be inside the computational domain. 
#            Closed polygons generate errors when meshing. One attribute 
#            is necesary defining the element size which has to be called 
#            "R_m"
#
#     --> -v: a points SHP is taken to define hard points on the 
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

#import own functions 
import fily, gis, gets, build

##  Start QGIS  ##
QgsApplication.setPrefixPath('/usr', True)
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
qgs = QgsApplication([], True)
qgs.initQgis()

#Add plugins and processing algorithms
sys.path.append('/usr/share/qgis/python/plugins/')  #Path to QGIS installation
import processing
from processing.core.Processing import Processing

#Add native functions
Processing.initialize()
qgs.processingRegistry().addProvider(QgsNativeAlgorithms())

####################################################################

#Start QGIS Project
project = QgsProject.instance()

#Clean temporal files
fily.touchFolder("../.Temp")

### Retrieves SHP Conversor Mode
#### -p | polygon         : SHP polygon
#### -i | heteropolygon   : SHP polygon + SHP polygon
#### -l | lines           : SHP lines
#### -v | vertices        : SHP points
execMode = str(sys.argv[1]).lower()

if   execMode in ["-p","--polygon"]:
    path2Polygon = str(sys.argv[2])                        #Outline Polygon SHP << INPUT
    path2Line = "../.Temp/1.OutlineLine.shp"               #Outline Line SHP path
    path2Vertex = "../.Temp/2.OutlineVertex.shp"           #Outline Vertices SHP path
    path2VertexXY = str(sys.argv[3])                       #Output CSV + XY Coordinates >> OUTPUT

    fily.touchFile(path2Line)
    fily.touchFile(path2Vertex)
    fily.touchFile(path2VertexXY)

    gis.polyToLine(path2Polygon,path2Line)              #SHP Polygon   >> SHP Lines
    gis.lineToVertex(path2Line,path2Vertex)             #SHP Lines     >> SHP Vertices
    gis.vertexToXYCSV(path2Vertex,path2VertexXY)        #SHP Vertices  >> CVS XY Vertices
    print("SHP2GEO polygon ~OK~:  " + str(sys.argv[2]) + " > " + str(sys.argv[3]))

elif execMode in ["-i","--heteropolygon"]:
    path2Polygon = str(sys.argv[2])                        #Outline Polygon SHP << INPUT
    path2SizeMap = str(sys.argv[3])                        #Outline Polygon SHP << INPUT
    path2Line = "../.Temp/1.OutlineLine.shp"               #Outline Line SHP path
    path2Vertex = "../.Temp/2.OutlineVertex.shp"           #Outline Vertices SHP path
    path2UnionV = "../.Temp/3.VertexMapped.shp"            #Outline Vertices SHP path
    path2VertexXY = str(sys.argv[4])                       #Output CSV + XY Coordinates >> OUTPUT

    print("\n\n1.1. Polygon to Lines")
    gis.polyToLine(path2Polygon,path2Line)                     #SHP Polygon   >> SHP Lines
    print("\n\n1.2. Lines to Vertices")
    gis.lineToVertex(path2Line,path2Vertex)                    #SHP Lines     >> SHP Vertices
    print("\n\n1.3. Map element sizes on Vertices")
    gis.mapElementSizes(path2Vertex,path2SizeMap,path2UnionV)  #SHP Vertices  >> SHP Mapped Vertices
    print("\n\n1.4. Save XY-Vertices")
    gis.vertexToXYCSV(path2UnionV,path2VertexXY)               #SHP Mapped V  >> CVS XY Vertices
    print("\n\n1.5. SHP2GEO iPolygon ~OK~:  " + str(sys.argv[2]) + \
        " + " + str(sys.argv[3]) + "> " + str(sys.argv[4]))

elif execMode in ["-l","--line"]:
    path2Line = str(sys.argv[2])                           #Outline Line SHP path
    path2Vertex = "../.Temp/2.OutlineVertex.shp"           #Outline Vertices SHP path
    path2VertexXY = str(sys.argv[3])                       #Output CSV + XY Coordinates >> OUTPUT

    print("\n\n1.1. Lines to Vertices")
    gis.lineToVertex(path2Line,path2Vertex)             #SHP Lines     >> SHP Vertices
    print("\n\n1.2. Save XY-Vertices")
    gis.vertexToXYCSV(path2Vertex,path2VertexXY)        #SHP Vertices  >> CVS XY Vertices
    print("\n\n1.3. SHP2GEO Lines ~OK~:  " + str(sys.argv[2]) + " > " + str(sys.argv[3]))

elif execMode in ["-v","--vertices"]:
    path2Vertex = str(sys.argv[2])                         #Outline Vertices SHP path
    path2VertexXY = str(sys.argv[3])                       #Output CSV + XY Coordinates >> OUTPUT

    print("\n\n1.1. Save XY-Vertices")
    gis.vertexToXYCSV(path2Vertex,path2VertexXY)        #SHP Vertices  >> CVS XY Vertices
    print("\n\n1.2. SHP2GEO Vertices ~OK~:  " + str(sys.argv[2]) + " > " + str(sys.argv[3])) 

else:
    print("Unrecognized parameter:  " + str(sys.argv[1]))

#Delete temporal folder
shutil.rmtree("../.Temp", ignore_errors=True)

