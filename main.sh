# Boundary SHP >> Boundary XY CSV #
python3 SHP2GEO.py p ../SHP_Files/Boundary.shp ../CSV_Files/Boundary.csv

#Points in Surface SHP >> Points in Surface XY CSV #
python3 SHP2GEO.py v ../SHP_Files/PointsinDomain.shp ../CSV_Files/PointsD.csv

#Points in Surface SHP >> Points in Surface XY CSV #
python3 SHP2GEO.py l ../SHP_Files/Lines.shp ../CSV_Files/Lines.csv

# Boundary XY CSV >> Boundary GEO #
python3 buildGEO.py b ../CSV_Files/Boundary.csv ../GEO_Files/Boundary.geo

# Points in Surface XY CSV >> Points in Surface GEO #
python3 buildGEO.py p ../CSV_Files/PointsD.csv ../GEO_Files/Boundary.geo

# Points in Surface XY CSV >> Lines in Surface GEO #
python3 buildGEO.py l ../CSV_Files/Lines.csv ../GEO_Files/Boundary.geo
