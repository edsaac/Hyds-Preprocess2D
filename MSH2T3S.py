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
# Modified:   July 18, 2019
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
#     --> --bott: Only a DEM file is used to define the BOTTOM on the file
#
#     --> --fric: Only a raster file containing BOTTOM FRICTION values 
#                 is used for the T3S
#
#     --> --both: Both BOTTOM and BOTTOM FRICTION are sampled from two 
#                 raster files
#
#     --> --none: Sampling node data is not performed and a dummy value is 
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
import fily, gis, gets, build               #import own functions 
#////////////////////////////////////////////////////////////////////////

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
csvFilePath = "../.Temp/CSV.csv"
fily.resetFile(csvFilePath,"T3S")
XYcsvFile   = build.buildCSV_2Col(xCoord_MSH,yCoord_MSH)
fily.appendFile(XYcsvFile,csvFilePath,False)

### Retrieves SHP Conversor Mode
#### -bott | BOTTOM                     : Elevation Model
#### -fric | BOTTOM FRICTION            : Raster Friction
#### -both | BOTTOM & BOTTOM FRICTION   : Both Rasters
#### -none | NONE                       : No Attribute
execMode = str(sys.argv[3]).lower()

if execMode in ["--bott"]:
    pathToTIFFile = str(sys.argv[4])            #TIF  input file

    #Sample the raster onto the mesh nodes saved on the temporal CSV
    sampledRasterFile = "../.Temp/SampledBottom.csv"
    gis.sampleRaster(csvFilePath,pathToTIFFile,sampledRasterFile)

    #Get BOTTOM data column from a DEM
    zBottom = gets.getCommaFile(sampledRasterFile,col=2)
    zBottom = zBottom[1:]
    
    nAttribute = ["1"]
    whichAttri = ["BOTTOM"]

if execMode in ["--fric"]:
    pathToFRIFile = str(sys.argv[4])            #TIF  input file

    #Rasterize the friction polygon SHP to avoid repeated values
    rasterizedFrictionFile = "../.Temp/SampledFriction.tif"
    gis.rasterPoly(pathToFRIFile,rasterizedFrictionFile,"FRICTION")
    
    #Sample the raster onto the mesh nodes saved on the temporal CSV
    sampledFrictionFile = "../.Temp/SampledFriction.csv"
    gis.sampleRaster(csvFilePath,rasterizedFrictionFile,sampledFrictionFile)
    
    #Get BOTTOM FRICTION data column from a SHP Polygon
    fBottom = gets.getCommaFile(sampledFrictionFile,col=2)
    zBottom = fBottom[1:]
    
    #Keywords for the T3S header
    nAttribute = ["1"]
    whichAttri = ["BOTTOM FRICTION"]

elif execMode in ["--both"]:
    pathToDEMFile = str(sys.argv[4])            #TIF  input file
    pathToFRIFile = str(sys.argv[5])            #SHP  input file

    #Sample the raster onto the mesh nodes saved on the temporal CSV
    sampledRasterFile = "../.Temp/SampledBottom.csv"
    gis.sampleRaster(csvFilePath,pathToDEMFile,sampledRasterFile)

    #Get BOTTOM data column from a sampled file
    zBottom = gets.getCommaFile(sampledRasterFile,col=2)
    zBottom = zBottom[1:]

    #Rasterize the friction polygon SHP to avoid repeated values
    rasterizedFrictionFile = "../.Temp/SampledFriction.tif"
    gis.rasterPoly(pathToFRIFile,rasterizedFrictionFile,"FRICTION")
    
    #Sample the raster onto the mesh nodes saved on the temporal CSV
    sampledFrictionFile = "../.Temp/SampledFriction.csv"
    gis.sampleRaster(csvFilePath,rasterizedFrictionFile,sampledFrictionFile)
    
    #Get BOTTOM FRICTION data column from a SHP Polygon
    fBottom = gets.getCommaFile(sampledFrictionFile,col=2)
    fBottom = fBottom[1:]

    #Merge BOTTOM and BOTTOM FRICTION
    zfValue = []
    try:
        for i in range(len(fBottom)):
            zfValue.append(str(zBottom[i]) + " " + str(fBottom[i]))
        zBottom = zfValue
    except IndexError:
        "Frction Map has overlying features. Mesh nodes with multiple BOTTOM FRICTION values :("

    #Keywords for the T3S header
    nAttribute = ["1","2"]
    whichAttri = ["BOTTOM","BOTTOM FRICTION"]

elif execMode in ["--none",""]:  
    #Insert a dummy BOTTOM value
    zBottom = ["0"]*len(xCoord_MSH)

    #Build T3S Node List
    Nodes_T3S  = build.buildT3S_3Col(xCoord_MSH,yCoord_MSH,zBottom)

    #Keywords for the T3S header
    nAttribute = "1"
    whichAttri = "NONE"


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

#Build T3S Node List
Nodes_T3S  = build.buildT3S_3Col(xCoord_MSH,yCoord_MSH,zBottom)

#Build T3S Element List
Elements_T3S  = build.buildT3S_3Col(p1Elements_MSH,p2Elements_MSH,p3Elements_MSH)

#Build T3S Header
Header_T3S  = build.buildT3S_Header(manyNodes,manyElements,nAttribute,whichAttri)

#Write T3S Files
fily.appendFile(Header_T3S,pathToT3SFile,True)       #Header1
fily.appendFile(Nodes_T3S,pathToT3SFile)             #Nodes
fily.appendFile(Elements_T3S,pathToT3SFile)          #Triangles

print("MSH2T3S ~OK~: " + str(sys.argv[1]) + " > " + str(sys.argv[2]))
