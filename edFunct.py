

###   Extract data from raster to nodes {in construction}
def sampleRaster(inputNodes,rasterFile,outputNodes):
    
    #Creates an empty SHP file for scratching the X coordinate
    sampledNodes = "../.Temp/1_Sampled.shp"
    touchFile(sampledNodes)

    #Load and check input points SHP layer to environment
    meshNodes = QgsVectorLayer(inputNodes, "points")
    checkLayer(meshNodes)

    #Load and check raster TIF layer to environment
    rasterToProbe = QgsVectorLayer(rasterFile, "raster")
    checkLayer(rasterToProbe)

    #Calculates the X-coordinates as a new field on a SHP
    params = {'INPUT':meshNodes,
        'RASTERCOPY': rasterToProbe,
        'COLUMN_PREFIX': "B",
        'OUTPUT':path2VertexX
            }
    processing.run("qgis:rastersampling", params )

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

#////////////////////////////////////////////////////////////////////////