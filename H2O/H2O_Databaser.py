# -*- coding: utf-8 -*-
"""H2O pyt

Author: Justin Bousquin
bousquin.justin@epa.gov
"""

import os
import json
import utils
import arcpy
#only used for addfield

def soils(FIPS, directory):
    #current methods defines FIPS using current census, alternatively
    #the polygon geometry can be used to define the SSA based on overlap.
    #If re-writing this way, BE AWARE of Spatial Reference
    #"soil data develppment tools" uses AOI to get Areasymbols
    
    # Build WSS query/download
    # Define AOI by state/county
    for FIP in FIPS:
        state = utils.getStateName(FIP)
        county = utils.splitFIPS(FIP)[1]
        county_SSA = "{}{}".format(state, county)
        
        # SSA can be used to define area of interest on WSS
        #http://websoilsurvey.nrcs.usda.gov/app/WebSoilSurvey.aspx?aoissa=NC175
        map_aoi = "aoissa={}".format(SSA)

        # Get list of SSA for FIP
        SSA_list = utils.getCounty_surveys(FIP)
        for SSA in SSA_list:
            # Get latest saverest
            date_year_mo_da = utils.getSurvey_date(SSA)            
    
            # Download SSURGO by SSA
            # Example: WSS_url + wss_SSA_FL113_[2017-10-06].zip
            WSS_url = "https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/"
            filename = "wss_SSA_{}_[{}].zip".format(SSA, date_year_mo_da)
            # Get zip
            utils.HTTPS_download(WSS_url, directory, filename)
            # Check zip
            if utils.Check_archive(directory, filename):
                z = directory + os.sep + filename
                # Extract desired shp to soils_file
                out_file = directory + os.sep + "AOI_soils.shp"
                SSA_shp = "{0}{1}spatial{1}soilmu_a_{0}.shp".format(SSA, os.sep)
                utils.extract_shp_to(z, SSA_shp, out_file)
                
            # Instead get geometries and create polygons?
            #then query map unit keys mukey

        # Edit out_file
        #add fields: "Mukey_long" type long integer (not needed anymore)
        #            “Max_Type_N”, short integer
        arcpy.AddField_management(out_file, "Max_Type_N", "SHORT")
        # Dictionary lookup for soil class -> Max_Type_N
        max_n_lookup = {"A": 1, "B": 2, "C": 3, "D": 4, None: 0}
        # Get "hydgrp" by mukey
        
        #SLOWER METHOD
        fields = ["Max_Type_N", "MUKEY"]
        with arcpy.da.UpdateCursor(out_file, fields) as cursor:
            for row in cursor:
                try:
                    # Use mukey to list of hydgrps
                    #seems to be returned by percent cover "comppct_r")
                    val_list = utils.getMUKEY_var(row[1], "hydgrp")
                    if val_list[0] is not None:
                        # Get first letter in first hydgrp
                        val1 = val_list[0][0]
                        # Max_Type_N becomes integer value of soil class
                        row[0] = max_n_lookup[val1]
                        cursor.updateRow(row)
                    #else: doesn't get updated if none
                except:
                    utils.message("Could not update {} for {}".format(fields[0], row[1]))

        #Faster Method
        #build table based on unique keys and then join field?
        # Get list of unique mukey
        mukey_list = utils.unique_values(out_file, "MUKEY")
        # Get hydrgrps for unique
        Max_Type_N_list = []
        for val in mukey_list:
            val_list = utils.getMUKEY_var(val, "hydgrp")
            if val_list[0] is not None:
                Max_Type_N_list += [val_list[0][0]]
            else:
                Max_Type_N_list += [None]
        # write values to out_file
        fields = ["Max_Type_N", "MUKEY"]
        with arcpy.da.UpdateCursor(out_file, fields) as cursor:
            for row in cursor:
                i = mukey_list.index(row[1])
                row[0] = max_n_lookup[Max_Type_N_list[i]]
                cursor.updateRow(row)
        # Delete some fields
        for del_field in ["MUKEY", "AREASYMBOL", "SPATIALVER", "MUSYM"]:
            arcpy.DeleteField_management(out_file, del_field)

    
##    #define AOI by envelope
##    """This method is tricky because the geometry must be converted to their SR
##    """
##    aoi = "aoicoords=(({}))".format(utils.getEnvelope(poly))
##
##    #use mapserver
##    """The method doesn't return geometries?
##    """
##    # Query mukey for polygons intersecting poly envelope
##    geo = utils.getEnvelope(poly)
##    geoType = "esriGeometryEnvelope"
##    inSR = utils.getSR(poly)
##    fields = ["Geometry", "mukey"]
##    query = utils.geoQuery(geo, geoType, inSR, fields)
##    
##    #https://server.arcgisonline.com/arcgis/rest/services/Specialty/Soil_Survey_Map/MapServer/0
##    catalog = "server.arcgisonline.com"
##    service = "Specialty/Soil_Survey_Map"
##    layer = "0"
##    response = utils.MapServerRequest(catalog, service, layer, query)
        
def landuse():
    #import default nlcd raster image
    #https://datagateway.nrcs.usda.gov/GDGOrder.aspx - download by state?
def NHD():
    #adapt RBI Tool
def roads(FIPS, directory):
    for FIP in FIPS:
        # Download
        filename = "tl_2013_{}_roads.zip".format(FIP)
        request = "ftp://ftp2.census.gov/geo/tiger/TIGER2013/ROADS/"
        utils.HTTPS_download(request, directory, filename)
        # Make sure download is valid
        utils.Check_archive(directory, filename)
        # Unzip
        z = directory + os.sep + filename
        utils.WinZip_unzip(z)

def main(poly, outDIR):
    county, FIPS = utils.polyFIPS(poly)
    soils(FIPS, outDIR)
    roads(FIPS, outDIR)

#try:
#    main()
#except:

# Polygon from user
poly = r"C:\ArcGIS\Local_GIS\Export_Output.shp"
outDIR = r"C:\ArcGIS\Local_GIS\H2O\soil\auto_test"
# Project in WebMercator (3857) if not projected
main(poly, outDIR)
