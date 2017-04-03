"""Create fields in FC table for unique values in raster
Then determine area weighted raster coverage for each field
"""
import arcpy
import decimal
from arcpy import da
from decimal import *

###FUNCTIONS###
"""Unique Values
Purpose: returns a sorted list of unique values"""
#Function Notes: used to find unique field values in table column
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor if row[0]})

"""Percent Cover
Purpose:"""
#Function Notes:
def percent_cover(poly, bufPoly):
    arcpy.MakeFeatureLayer_management(poly, "polyLyr")
    lst=[]
    orderLst=[]
    #add handle for when no overlap?
    with arcpy.da.SearchCursor(bufPoly, ["SHAPE@", "OID@"]) as cursor:
        for row in cursor:
            totalArea = Decimal(row[0].getArea("PLANAR", "SQUAREMETERS"))
            arcpy.SelectLayerByLocation_management("polyLyr", "INTERSECT", row[0])
            lyrLst = []
            with arcpy.da.SearchCursor("polyLyr", ["SHAPE@"]) as cursor2:
                for row2 in cursor2:
                    interPoly = row2[0].intersect(row[0], 4) #dimension = 4 for polygon
                    interArea = Decimal(interPoly.getArea("PLANAR", "SQUAREMETERS"))
                    lyrLst.append((interArea/totalArea)*100)
            lst.append(sum(lyrLst))
            orderLst.append(row[1])
    #arcpy.Delete_management(polyD)
    #fix above cleanup
    orderLst, lst = (list(x) for x in zip(*sorted(zip(orderLst, lst)))) #sort by ORIG_FID
    return lst

"""Add List to Field
Purpose: """
#Function Notes: 1 field at a time
#Example: lst_to_field(featureClass, "fieldName", lst)
def lst_to_field(table, field, lst): #handle empty list
    if len(lst) ==0:
        print("No values to add to '{}'.".format(field))
    else:
        i=0
        with arcpy.da.UpdateCursor(table, [field]) as cursor:
            for row in cursor:
                row[0] = lst[i]
                i+=1
                cursor.updateRow(row)

"""Check Spatial Reference
Purpose: checks that a second spatial reference matches the first and re-projects if not."""
#Function Notes: Either the original FC or the re-projected one is returned
def checkSpatialReference(alphaFC, otherFC):
    alphaSR = arcpy.Describe(alphaFC).spatialReference
    otherSR = arcpy.Describe(otherFC).spatialReference
    if alphaSR.name != otherSR.name:
        #e.g. .name = u'WGS_1984_UTM_Zone_19N' for Projected Coordinate System = WGS_1984_UTM_Zone_19N
        print("Spatial reference for " + otherFC + " does not match.")
        try:
            path = os.path.dirname(alphaFC)
            ext = arcpy.Describe(alphaFC).extension
            newName = os.path.basename(otherFC)
            output = path + os.sep + os.path.splitext(newName)[0] + "_prj" + ext
            arcpy.Project_management(otherFC, output, alphaSR)
            fc = output
            print("File was re-projected and saved as " + fc)
        except:
            print("Warning: spatial reference could not be updated.")
            fc = otherFC
    else:
        fc = otherFC
    return fc

########
##VARS##
#inFC with mukey
inFC = r"C:\ArcGIS\Local_GIS\HWBI\SSURGO\soilmu_State.gdb\soil_mu_a_al"
#mukey
keyID = "MUKEY"
#table with mukey & NCCPI valu
valuTable = r"C:\ArcGIS\Local_GIS\HWBI\SSURGO\gSSURGO_RI.gdb\valu1"
#table with mukey & farmland designation
farmTable = r"C:\ArcGIS\Local_GIS\HWBI\SSURGO\gSSURGO_RI.gdb\mapunit"
#NCCPI field in valuTable
fields = "pctearthmc"
#fields = ["pctearthmc","farmlndcl"]
#FC table
FC = r"C:\ArcGIS\Local_GIS\HWBI\HWBI.gdb\TIGER_FULL"
#output
outTbl = r"C:\ArcGIS\Local_GIS\HWBI\HWBI.gdb\results_all"

###Execute###
#check FC reference is the same as soil survey
FC = checkSpatialReference(inFC, FC)

#copy outTbl
arcpy.CopyFeatures_management(FC, outTbl)

#join NCCPI field
arcpy.JoinField_management(inFC, keyID, valuTable, keyID, fields)
#arcpy.JoinField_management(inFC, keyID, farmTable, keyID, fields)

arcpy.MakeFeatureLayer_management(inFC, "lyr")

#list possible values
#for field in fields:
field_lst = unique_values(valuTable, fields)
#create a field for each possible value
for val in field_lst:
    name = "pctea_" + str(val)
    arcpy.AddField_management(outTbl, name, "DOUBLE")
    #select poly soil with that value
    #arcpy.MakeFeatureLayer_management(inFC, "lyr")
    whereClause = str(fields) + " = " + str(val)
    arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", whereClause)
    #get percent areas
    val_lst = percent_cover("lyr", outTbl)
    #add to table
    lst_to_field(outTbl, name, val_lst)
