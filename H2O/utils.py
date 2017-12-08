# -*- coding: utf-8 -*-
"""Basic download functions

Author: Justin Bousquin
bousquin.justin@epa.gov
"""

import os
from urllib import urlretrieve, urlopen
from shutil import copyfile
from json import loads, load
from math import ceil
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
    outGeo = "returnGeometry=false"
    outFields = "outFields="
    for f in fields:
        if f == "Geometry":
            outGeo = "returnGeometry=true"
        else:
            outFields += "{},".format(f)
    ret = "{}&{}".format(outFields, outGeo)
    return "query?{}&{}&{}&{}&{}".format(geo, geoType, inSR, spRel, ret)


def getServiceInfo(catalog, service):
    #catalog = "enviroatlas.epa.gov"
    #service = "Supplemental/Dasymetric_WMerc"
    f = "f=pjson"
    # Build request
    r = "https://{}/arcgis/rest/services/{}/MapServer?{}".format(catalog, service, f)
    # Send request
    return loads(api_request(r))

def rasterServiceDict(catalog, service):
    sJSON = getServiceInfo(catalog, service)
    maxImage = "{},{}".format(sJSON['maxImageWidth'], sJSON['maxImageHeight'])

    e = sJSON["fullExtent"]
    rasterExtent = "{},{},{},{}".format(e['xmin'],e['ymin'],e['ymax'],e['xmax'])
    #SR = sJSON["spatialReference"]
    return {"maxImage": maxImage, "rasterExtent": rasterExtent}

def rasterPointQuery(geo, inSR, serviceDict):
    #geometry=-9705448.14767,3587228.92735
    geo = "geometry={}".format(geo)
    inSR = "sr={}".format(inSR)
    geoType = "geometryType=esriGeometryPoint"
    tol = "tolerance=1"
    #"mapExtent=-14246360.5296%2C2604051.01388,6737031.01388,-7264070.52956
    ext = "mapExtent={}".format(serviceDict["rasterExtent"])
    #"imageDisplay=4096,4096"
    img = "imageDisplay={}".format(serviceDict["rasterExtent"])
    ret = "returnGeometry=false"
    #"&gdbVersion"

    return "identify?{}&{}&{}&{}&{}&{}&{}".format(geo, geoType, inSR, tol, ext, img, ret)


def queryPoints(catalog, service, AOI, cellx, celly):
    #cellx and celly are min cell width and min cell height in meters
    # Get Spatial Reference for AOI
    inSR = getSR(AOI)
    # Get bounding box for AOI
    bBox = boundingBox(AOI)
    # Get bounding Box points in correct format
    bb_list = [float(a) for a in bBox.split(",")]
    # Determine number of equidistant points
    x_i = int(ceil((bb_list[2] - bb_list[0])/cellx))
    y_i = int(ceil((bb_list[3] - bb_list[1])/celly))
    points = []
    # Start in left lower corner
    startPnt = bb_list[0], bb_list[1]
    for i in range(0, y_i):
        # Increase y by celly x_i times
        y = startPnt[1] + (i * celly)
        for j in range(0, x_i):
            # Increase x by cellx x_i times
            x = startPnt[0] + (j * cellx)
            points += [[x,y]]

    # Get info needed for query
    #catalog = "enviroatlas.epa.gov"
    #service = "Supplemental/Dasymetric_WMerc"
    serviceDict = rasterServiceDict(catalog, service)

    # Get value at each point
    pnt_values = []
    for pnt in points:
        #geo = "-9705448.14767,3587228.92735"
        geo = "{},{}".format(pnt[0], pnt[1])      
        query = rasterPointQuery(geo, inSR, serviceDict)
        JSON_response = MapServerRequest(catalog, service, None, query)
        pnt_values += JSON_response[u'results'][0]['attributes']['Pixel Value']

    # Turn the pont values into a raster

    # Snap/re-project to align with original?

def MapServerRequest(catalog, service, layer, query):
    #catalog = "tigerweb.geo.census.gov"
    #service = "TIGERweb/tigerWMS_Census2010"
    #layer = 98
    if layer is None:
        layer = ""
    else:
        layer = "{}/".format(layer)
    que = "{}&f=json".format(query)
    r = "https://{}/arcgis/rest/services/{}/MapServer/{}{}".format(catalog, service, layer, que)
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
