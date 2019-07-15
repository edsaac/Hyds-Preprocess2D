#Boundary SHP >> Boundary XY CSV #
#SHP2GEO.py i ../SHP_Files/Boundary.shp ../SHP_Files/ElementSizesMap.shp ../CSV_Files/Boundari.csv

#Points in Surface SHP >> Points in Surface XY CSV #
#SHP2GEO.py v ../SHP_Files/PointsinDomain.shp ../CSV_Files/PointsD.csv

#Points in Surface SHP >> Points in Surface XY CSV #
#SHP2GEO.py l ../SHP_Files/Lines.shp ../CSV_Files/Lines.csv

# Boundary XY CSV >> Boundary GEO #
#buildGEO.py -b ../CSV_Files/Boundari.csv ../GEO_Files/Boundari.geo

# Points in Surface XY CSV >> Points in Surface GEO #
#buildGEO.py -p ../CSV_Files/PointsD.csv ../GEO_Files/Boundari.geo

# Points in Surface XY CSV >> Lines in Surface GEO #
#buildGEO.py -l ../CSV_Files/Lines.csv ../GEO_Files/Boundari.geo

#Mesh generation with GMSH
#~/Apps/gmsh-3.0.6/bin/gmsh -2 ../GEO_Files/Boundari.geo 

#GMSH Mesh to T3S
MSH2T3S.py ../GEO_Files/Boundari.msh ../T3S_Files/Boundari.t3s
