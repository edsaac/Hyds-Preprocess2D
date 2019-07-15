#!/usr/bin/env python3
#
#////////////////////////////////////////////////////////////////////////
#                                                                       #
#                                 MSH2T3S.py                            # 
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
# Purpose:    Script takes in a MSH (v.2) file generated on gmsh and 
#             produces a t3s mesh file (MSH) recognized by BlueKenue(C). 
#
# Needs:      Python3, csv, sys, os, shutil
#
# Usage:      python3 MSH2T3S.py <input.msh> <output.t3s> <option> 
#                 <raster_1.tif> [<raster_2.tif>]
#
# where:
# --> input.msh : a string that defines the path to MSH file from where 
#                 the gmsh mesh is to be read.
#
# --> output.t3s: a string that defines the path to the T3S file where 
#                 the BlueKenue mesh will be written.                       
#
# --> option    : a string that defines which spatial values have to be 
#                 retrieved from a raster TIFF file 
#
#     --> bottom: Only a DEM file is used to define the BOTTOM on the file
#
#     --> energy: Only a raster file containing BOTTOM FRICTION values 
#                 is used for the T3S
#
#     --> botenr: Both BOTTOM and BOTTOM FRICTION are sampled from two 
#                 raster files
#
#     --> notifs: Sampling node data is not performed and a dummy value is 
#                 given on the T3S
#  
# --> raster.tif: a string that defines the path to TIF file from where the
#                 attributes are to be read. 
#                 
# Bibliography & Useful links:
# -- https://github.com/pprodano/pputils
# -- http://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format-version-2-_0028Legacy_0029
#
#////////////////////////////////////////////////////////////////////////

import csv, sys, os, re

#import own functions 
import fily, gis, gets, build
#////////////////////////////////////////////////////////////////////////

#Import Qgis libraries 
from qgis.core import *
from qgis.processing import *
from qgis.utils import *
from qgis.analysis import *
from PyQt5.QtCore import QVariant

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

#Start QGIS Project
project = QgsProject.instance()

#Clean temporal files
fily.touchFolder("../.Temp")

####################################################################

#Retrieve path of files from the arguments passed to the script
pathToMSHFile = str(sys.argv[1])            #MSH  input file 
pathToT3SFile = str(sys.argv[2])            #T3S output file

#Create a new empty T3S File
fily.resetFile(pathToT3SFile,"T3S")

#Read MSH file and organize it as a list
Raw_MSH = fily.parseFile(pathToMSHFile)

#Extract Nodes from the MSH File
startNodes = gets.getLineIndex(Raw_MSH,"$Nodes")      
endNodes   = gets.getLineIndex(Raw_MSH,"$EndNodes")   
Nodes_MSH  = Raw_MSH[startNodes+2:endNodes]

#Extract Coordinates of the extracted list of nodes
manyNodes  = int(Raw_MSH[startNodes+1])
xCoord_MSH = gets.getColumnContents(Nodes_MSH,2)
yCoord_MSH = gets.getColumnContents(Nodes_MSH,3)

#Save a temporal CSV file with the X,Y coordinates

#Sample the raster onto the mesh nodes saved on the temporal CSV
#if execMode in [""]:
    #BLABLABLA
#elif:
    #BLABLABLA

#Build T3S Node List
Nodes_T3S  = build.buildT3S_3Col(xCoord_MSH,yCoord_MSH,xCoord_MSH)

#Extract Elements from the MSH File
startElements = gets.getLineIndex(Raw_MSH,"$Elements")
endElements   = gets.getLineIndex(Raw_MSH,"$EndElements")
Elements_MSH  = Raw_MSH[startElements+2:endElements]

#Extract only 2d Triangles from the MSH elements
Triangles_MSH = gets.filterMSHElement(Elements_MSH,2)

#Extract only the structure of elements from the list
manyElements   = int(len(Triangles_MSH))
p1Elements_MSH = gets.getColumnContents(Triangles_MSH,6)
p2Elements_MSH = gets.getColumnContents(Triangles_MSH,7)
p3Elements_MSH = gets.getColumnContents(Triangles_MSH,8)

#Build T3S Element List
Elements_T3S  = build.buildT3S_3Col(p1Elements_MSH,p2Elements_MSH,p3Elements_MSH)

#Build T3S Header
Header_T3S  = build.buildT3S_Header(manyNodes,manyElements)

#Write T3S Files
fily.appendFile(Header_T3S,pathToT3SFile,True)       #Header
fily.appendFile(Nodes_T3S,pathToT3SFile)             #Nodes
fily.appendFile(Elements_T3S,pathToT3SFile)          #Triangles

print("MSH2T3S ~OK~: " + str(sys.argv[1]) + " > " + str(sys.argv[2]))