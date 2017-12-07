# -*- coding: utf-8 -*-
"""H2O pyt

Author: Justin Bousquin
bousquin.justin@epa.gov
"""

import os
import json
import utils

def soils():
    #get soils
    
def landuse():
    #export raster image
def NHD():
    #adapt what was used for RBI
def roads(FIPS, directory):
    # Download
    filename = "tl_2013_{}_roads.zip".format(FIPS)
    request = "ftp://ftp2.census.gov/geo/tiger/TIGER2013/ROADS/"
    utils.HTTPS_download(request, directory, filename)
    # Make sure download is valid
    utils.Check_archive(directory, filename)
    # Unzip
    z = directory + os.sep + filename
    utils.WinZip_unzip(z)

def main():
    soils()    

#try:
#    main()
#except:

# Polygon from user
poly = r"C:\ArcGIS\Local_GIS\Export_Output.shp"
outDIR = os.path.dirname(poly)

# Project in WebMercator (3857) if not projected


county, FIPS = polyFIPS(poly)

roads(FIPS, outDIR)



# Get county for extent

