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
        
def landuse(FIPS, directory):
    #download nlcd raster image
    url = "http://www.landfire.gov/bulk/downloadfile.php?"
    typ01 = "TYPE=nlcd2011&FNAME="
    FNAME = "nlcd_2011_landcover_2011_edition_2014_10_10.zip"
    contig_file = "{}{}".format(typ01, FNAME)
    file_list = []
    for FIP in FIPS:
        state = utils.getStateName(FIP)
        if state == 'AK':
            #?TYPE=nlcd2011
            FNAME = "ak_nlcd_2011_landcover_1_15_15.zip"
            file_list.append("{}{}".format(typ01, FNAME))
        elif state == 'HI':
            utils.message("Download High Resolution HI landcover from NOAA")
            #file_list.append(FNAME)
        elif state == 'PR':
            utlis.message("PR landuse is hard to find... using 2001")
            typPR = "TYPE=nlcdpr&FNAME="
            FNAME = "PR_landcover_wimperv_10-28-08_se5.zip"
            file_list.append("{}{}".format(typPR, FNAME))
        elif contig_file not in file_list:
            #import default nlcd raster image
            file_list.append(contig_file)
    #Alternative method - download by state
    #https://datagateway.nrcs.usda.gov/GDGOrder.aspx
    #Best Method Enviroatlas image service download

    # Do download
    for filename in file_list:
        utils.HTTPS_download(url, directory, filename)
        # Check zip
        if utils.Check_archive(directory, filename):
            z = directory + os.sep + filename
            
            # Extract desired shp to landuse_file
            utils.WinZip_unzip(z)
    #merge rasters?


def NHD(poly, directory):
    # Use service to get VPU
    #https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/
    #NHDPlus_V2_BoundaryUnit/FeatureServer/0
    #query?where=&objectIds=&time=&geometry=-9705448.14767%2C3587228.92735&geometryType=esriGeometryPoint&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=DrainageID&returnHiddenFields=false&returnGeometry=false&returnCentroid=false&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnDistinctValues=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=html&token=LadFT4-raCdo55z5yM7Q0CLsGjhRXfQCz5Yfk6kc9cm93z1mnppbn-Q0kwnE2miHzz6STI3PbvK4IrVjAe7ds1C8egDxEh-naXhHwLYmV4ii0kyehL7ugNVqnLyJdAZy1wAnNXUy_eN9fBajw15NnQKQThT0zSYUnzd9AfHcEtUCbU-JAIY2pUDBIZ0w5Mk_qFY1ubK_cfqUzxKAUYSmfUwrrAW3yRH8BznPgZmRrbtVPq41rWm-VRwSk2_yR8Nz
    catalog = "services.arcgis.com/cJ9YHowT8TU7DUyn"
    service = "NHDPlus_V2_BoundaryUnit"
    typ = "FeatureServer" #may add this to a map to make it more standardized
    layer = "0"
    
    envelope = utils.getBoundingBox(poly)
    inSR = utils.getSR(poly)
    fields = ["DrainageID", "UnitID"]
    query = utils.geoQuery(envelope, "esriGeometryEnvelope", inSR, fields)

    #t is my token, the service will be made open later    
    res = utils.MapServerRequest(catalog, service, layer, query, typ, t)
    features = res['features']

    # Use results to get VPU code
    ID_list = []
    d_list = []
    for feature in features:
        ID_list += [feature['attributes']['UnitID']]
        d_list += [feature['attributes']['DrainageID']]

    # Download Data
    requests = utils.getNHDrequest(ID_list, d_list)
    for request in requests:
        for f in request[1]:
            utils.HTTPS_download(request[0], directory, f)
            #zip files will not pass Check_archive because it is .7z
            z = directory + os.sep + f
            #update using 7z package if available
            #need to do some kind of check
            #after a user closes the error message it says "Successfully extracted files"
            utils.WinZip_unzip(z)


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
    landuse(FIPS, outDIR)
    NHD(poly, outDIR)

#try:
#    main()
#except:

# Polygon from user
poly = r"C:\ArcGIS\Local_GIS\Export_Output.shp"
outDIR = r"C:\ArcGIS\Local_GIS\H2O\soil\auto_test"
# Project in WebMercator (3857) if not projected
main(poly, outDIR)
