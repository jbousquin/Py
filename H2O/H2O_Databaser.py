# -*- coding: utf-8 -*-
"""H2O pyt

Author: Justin Bousquin
bousquin.justin@epa.gov
"""

import os
import json
import utils

def soils(FIPS, outDIR):
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
            #https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_FL113_[2017-10-06].zip
            WSS_url = "https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/"
            filename = "wss_SSA_{}_[{}].zip".format(SSA, date_year_mo_da)
            # Get zip
            utils.HTTPS_download(WSS_url, directory, filename)
            # Check zip
            if utils.Check_archive(directory, filename):
                z = directory + os.sep + filename
                utils.WinZip_unzip(z)

            # Instead get geometries and create polygons?


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
