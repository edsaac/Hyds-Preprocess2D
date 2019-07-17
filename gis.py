import sys, os, shutil, re, subprocess
from pathlib import Path
from fily import touchFile

#Import Qgis 
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


############***#

###   Checks if a layer is valid when loaded to QGIS
def checkLayer(layerName):                  
    print("Layer is valid?:  " + str(layerName.isValid()))
    if not layerName.isValid():
        print("Layer failed to load!")
        #sys.exit("Byee \n")
    else:
        print("Layer loaded sucessfully")


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
    path2VertexX = "../.Temp/3.OutlineVertexX.shp"

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
    path2Unioned = "../.Temp/4.Unioned.shp"
    
    print("__Something wrong but it works__:")##
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
    path2Calc = "../.Temp/5.RMIN.shp"
   
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

###   Sample data from raster on points
def sampleRaster(inputNodes,rasterFile,outputNodes):
    
    #Gets absolute path. It is necessary to load CSV into QGIS
    fullInputpath = str(os.path.abspath(inputNodes))

    #Load and check input points SHP layer to environment
    csvInputNodes = "file://" + \
        fullInputpath + \
        "?crs=epsg:3116&delimiter=%s&xField=%s&yField=%s"\
        % (",", "Xm", "Ym")
    meshNodes = QgsVectorLayer(csvInputNodes, "points", "delimitedtext")
    checkLayer(meshNodes)

    #Calculates the Bottom Elevation
    params = {'INPUT':meshNodes,
        'RASTERCOPY': rasterFile,
        'COLUMN_PREFIX': "B",
        'OUTPUT':outputNodes
            }
    processing.run("qgis:rastersampling", params )

###   Sample data from a polygon SHP on points 
def rasterPoly(mapFile,outputFile,burnField="FRICTION"):
    touchFile(outputFile)
    
    command = "gdal_rasterize -a " + \
        str(burnField) + \
        " -tr 10.0 10.0" + \
        " -a_nodata -999.0" + \
        " -ot Float32 -of GTiff " + \
        str(os.path.abspath(mapFile)) + \
        " " + \
        str(os.path.abspath(outputFile))
   
    os.system(command)