# -*- coding: utf-8 -*-
"""Basic download functions

Author: Justin Bousquin
bousquin.justin@epa.gov
"""

import os
from urllib import urlretrieve, urlopen
from shutil import copyfile
from json import loads, load
import zipfile
import subprocess
import arcpy

def message(string):
    print(string)


def HTTPS_download(request, directory, filename):
    """Download HTTP request to filename
    Param request: HTTP request link ending in "/"
    Param directory: Directory where downloaded file will be saved
    Param filename: Name of file for download request and saving
    """

    # Add dir to var zipfile is saved as
    f = directory + os.sep + filename
    r = request + filename
    try:
        urlretrieve(r, f)
        message("HTTP downloaded successfully as:\n" + str(f))
    except:
        message("Error downloading from: " + '\n' + str(r))
        message("Try manually downloading from: " + request)


def geoQuery(geo, geoType, inSR, fields):
    #envelopeQuery("-76.92691,38.846542", "esriGeometryPoint", 4326)
    geo = "geometry={}".format(geo)
    geoType = "geometryType={}".format(geoType)
    inSR = "inSR={}".format(inSR)
    spRel = "spatialRel=esriSpatialRelIntersects"
    limitGeo = "returnGeometry=false"
    outFields = "outFields="
    for f in fields:
        if f == "Geometry":
            limitGeo = "returnGeometry=true"
        else:
            outFields += "{},".format(f)    
    return "{}&{}&{}&{}&{}&{}".format(geo, geoType, inSR, spRel, outFields, limitGeo)


def MapServerRequest(catalog, service, layer, query):
    #catalog = "tigerweb.geo.census.gov"
    #service = "TIGERweb/tigerWMS_Census2010"
    #layer = 98
    que = "query?{}&f=json".format(query)
    r = "https://{}/arcgis/rest/services/{}/MapServer/{}/{}".format(catalog, service, layer, que)
    return loads(api_request(r))


def api_request(request):
    req = urlopen(request)
    return req.read()


def Check_archive(directory, filename):
    f = directory + os.sep + filename
    try:
        # Read in as zipFile
        archive = zipfile.ZipFile(f, 'r')
        message("Zip archive {} is valid.".format(filename))
        return True
    except:
        message("Zip archive {} was invalid.".format(filename))
        os.remove(f)
        message("It was deleted.")
        return False


def archive_list(z):
        # Read in as zipFile
        archive = zipfile.ZipFile(z, 'r')
        return archive.namelist()


def WinZip_unzip(z):
    message("Unzipping {}...".format(z))
    d = os.path.dirname(z)
    try:
        zipExe = r"C:\Program Files\WinZip\WINZIP64.EXE"
        args = zipExe + ' -e ' + z + ' ' + d
        subprocess.call(args, stdout=subprocess.PIPE)
        message("Successfully extracted files.")
    except:
        message("Unable to extact file:\n {}".format(z))


def polyFIPS(poly):
    # Get extent
    envelope = getEnvelope(poly)
    inSR = getSR(poly)
    if inSR == 0: # if 0 -> 4326
        inSR = 4326
    fields = ["NAME", "GEOID"]
    query = geoQuery(envelope, "esriGeometryEnvelope", inSR, fields)
    catalog = "tigerweb.geo.census.gov"
    service = "TIGERweb/tigerWMS_Current"
    layer = 86 #Counties ID: 86
    JSON_result = MapServerRequest(catalog, service, layer, query)
    county = JSON_result['features'][0]['attributes'][fields[0]]
    FIPS = JSON_result['features'][0]['attributes'][fields[1]]
    return county, FIPS


def splitFIPS(FIPS):
    state = str(FIPS[:2])
    county = str(FIPS[2:5])
    return state, county


def getStateName(FIPS):
    return get_states()[str(FIPS)]


def get_states():
    """construct distionary of states
    Notes: this is static so the end user can change scope more easily
    """
    states = {'09': 'CT', '51': 'VA', '50': 'VT', '19': 'IA', '26': 'MI',
              '35': 'NM', '04': 'AZ', '02': 'AK', '25': 'MA', '23': 'ME',
              '01': 'AL', '20': 'KS', '21': 'KY', '48': 'TX', '05': 'AR',
              '46': 'SD', '47': 'TN', '08': 'CO', '45': 'SC', '42': 'PA',
              '29': 'MO', '40': 'OK', '41': 'OR', '27': 'MN', '18': 'IN',
              '28': 'MS', '24': 'MD', '39': 'OH', '38': 'ND', '30': 'MT',
              '06': 'CA', '10': 'DE', '13': 'GA', '12': 'FL', '15': 'HI',
              '22': 'LA', '17': 'IL', '16': 'ID', '55': 'WI', '54': 'WV',
              '31': 'NE', '56': 'WY', '37': 'NC', '36': 'NY', '53': 'WA',
              '34': 'NJ', '33': 'NH', '32': 'NV', '49': 'UT', '44': 'RI'}
    return states


def getSR(fc):
    desc = arcpy.Describe(fc)
    #PCSCode    #GCSCode
    return desc.spatialReference.factoryCode


def getBoundingBox(fc):
    desc = arcpy.Describe(fc)
    xmin = desc.extent.XMin
    xmax = desc.extent.XMax
    ymin = desc.extent.YMin
    ymax = desc.extent.YMax

    return "{},{},{},{}".format(xmin, ymin, xmax, ymax)

def getEnvelope(fc):
    desc = arcpy.Describe(fc)
    xmin = desc.extent.XMin
    xmax = desc.extent.XMax
    ymin = desc.extent.YMin
    ymax = desc.extent.YMax

    return "{0},{1},{2},{1},{0},{3},{2},{3}".format(xmin, ymax, xmax, ymin)


def getJSON(fc):
    """NOT IN USE"""
    # Get JSON for shapefile
    out_json_file= os.path.dirname(fc) + os.sep + "temp.json"
    arcpy.FeaturesToJSON_conversion(fc, out_json_file)

    with open(out_json_file, "r") as f:
        json = load(f)

    geo = json['features'][0]['geometry']
    geoType = json['geometryType']
    geoSR = json['spatialReference']

    return geo, geoType, geoSR
