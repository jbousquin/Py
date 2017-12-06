# -*- coding: utf-8 -*-
"""Basic download functions

Author: Justin Bousquin
bousquin.justin@epa.gov
"""

import os
from urllib import urlretrieve, urlopen
from shutil import copyfile
from json import loads
import zipfile
import subprocess

def message(string):
    print(string)


def HTTP_download(request, directory, filename):
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


def pointQuery(geo, geoType, inSR):
    #pointQuery("-76.92691,38.846542", "esriGeometryPoint", 4326)
    geo = "geometry={}".format(geo)
    geoType = "geometryType=geoType"
    inSR = "inSR={}".format(inSR)
    spRel = "spatialRel=esriSpatialRelIntersects"
    limitGeo = "returnGeometry=false"
    return "{}&{}&{}&{}&{}".format(geo, geoType, inSR, spRel, limitGeo)


def envelopeQuery(geo, geoType, inSR):
    #envelopeQuery("-76.92691,38.846542", "esriGeometryPoint", 4326)
    geo = "geometry={}".format(geo)
    geoType = "geometryType=geoType"
    inSR = "inSR={}".format(inSR)
    spRel = "spatialRel=esriSpatialRelIntersects"
    limitGeo = "returnGeometry=false"
    return "{}&{}&{}&{}&{}".format(geo, geoType, inSR, spRel, limitGeo)


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


def point_to_state(x, y):
