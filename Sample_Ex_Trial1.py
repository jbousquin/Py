# Name: Sample_Ex_Trial1.py
# Description: Creates a table that shows the values of cells from 
#              a set of rasters, for defined locations. 
#              The locations are defined by raster cells. 
#      
# Requirements: Spatial Analyst Extension

# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *

# Set environment settings
env.workspace = "C:/sapyexamples/data"

# Set local variables
inRasters = ["elevation",
             "costraster"]
locations = "observers.shp"
outTable = "c:/sapyexamples/output/samptable02"
sampMethod = "NEAREST"

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Execute Sample
Sample(inRasters, locations, outTable, sampMethod)