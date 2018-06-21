# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 15:19:09 2018

@author: jbousqui
"""

#Raster_rpu_tifs

import fiona
import rasterio
import os
from os.path import join


def writeRaster(outFile, out_image, out_meta):
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    with rasterio.open(outFile, "w", **out_meta) as dest:
        dest.write(out_image)


def arc_writeRaster(in_raster, out_raster, outPoly):
    in_template_dataset = outPoly
    arcpy.Clip_management(in_raster, "", out_raster, in_template_dataset)


# Boundary file (vector/raster processing units)
boundaries = r"C:\ArcGIS\Local_GIS\National_RBI\gdal\BoundaryUnit.shp"
# tif raster file
raster = r"C:\ArcGIS\Local_GIS\National_RBI\EA_flood\EnviroAtlas_CONUS_estimated_floodplain\EnviroAtlas_CONUS_estimated_floodplain.tif"

#output location
path = join(os.path.dirname(boundaries), "rpu_flood_rasters")

# Fields of interest
fields = ["UnitType", "DrainageID", "UnitID"]
att = "properties"

with fiona.open(boundaries, "r") as shp:
    geoms = [feat["geometry"] for feat in shp if feat[att][fields[0]]=="RPU"]
    drainID = [feat[att][fields[1]] for feat in shp if feat[att][fields[0]]=="RPU"]
    unitID = [feat[att][fields[1]] for feat in shp if feat[att][fields[0]]=="RPU"]
    
#remove HI and CI
i=0
for drain in drainID:
    if drain in ["HI", "CI"]:
        del drainID[i]
        del geoms[i]
        del unitID[i]
    else:
        i+=1

#arcpy alternative
import arcpy
rast_obj = arcpy.Raster(raster)
for i, geo in enumerate(geoms):
    outFile = join(path, "{}_{}_flood.tif".format(unitID[i], drainID[i]))
    arc_writeRaster(rast_obj, outFile, geo)




#FOSS alternative    
with rasterio.open(raster) as src:
    for i, geo in enumerate(geoms):
        out_image, out_transform = rasterio.tools.mask(src, geo, crop=True)
        out_meta = src.meta.copy()
        outFile = join(path, "{}_{}_flood.tif".format(unitID[i], drainID[i]))
        writeRaster(outFile, out_image, out_transform, out_meta)
