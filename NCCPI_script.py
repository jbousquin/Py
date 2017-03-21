"""Create fields in FC table for unique values in raster
Then determine area weighted raster coverage for each field
"""
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
    with arcpy.da.SearchCursor(bufPoly, ["SHAPE@", "ORIG_FID"]) as cursor:
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
        message("No values to add to '{}'.".format(field))
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
        message("Spatial reference for " + otherFC + " does not match.")
        try:
            path = os.path.dirname(alphaFC)
            ext = arcpy.Describe(alphaFC).extension
            newName = os.path.basename(otherFC)
            output = path + os.sep + os.path.splitext(newName)[0] + "_prj" + ext
            arcpy.Project_management(otherFC, output, alphaSR)
            fc = output
            message("File was re-projected and saved as " + fc)
        except:
            message("Warning: spatial reference could not be updated.")
            fc = otherFC
    else:
        fc = otherFC
    return fc

########
##VARS##
#inRaster with mukey
inRaster = r"L:\Public\jbousqui\GED\GIS\SSURGO\gSSURGO\soils_GSSURGO_ri_3389290_01\soils\gssurgo_g_ri\gSSURGO_RI.gdb\MapunitRaster_ri_10m"
#mukey
keyID = "MUKEY"
#table with mukey & NCCPI valu
valuTable = r"L:\Public\jbousqui\GED\GIS\SSURGO\gSSURGO\soils_GSSURGO_ri_3389290_01\soils\gssurgo_g_ri\gSSURGO_RI.gdb\valu1"
#NCCPI field
fields = "pctearthmc"
#FC table
FC = "TIGER_FULL"
#outputs
#polygon of raster values
polyRast = r"L:\Public\jbousqui\GED\GIS\HWBI.gdb\polyRast"
#copy of FC table with percent cover
outTbl = r"L:\Public\jbousqui\GED\GIS\HWBI.gdb\results"

###Execute###
#copy outTbl
arcpy.CopyFeatures_management(FC, outTbl)

#join NCCPI field
arcpy.JoinField_management("raster", keyID, valuTable, keyID)
#make raster layer
arcpy.MakeRasterLayer_management(inRaster, "raster")
#convert raster to polygon
arcpy.RasterToPolygon_conversion("raster", polyRast, "NO_SIMPLIFY", fields)

#check spatial reference on polyRast
polyRast = checkSpatialReference(outTbl, polyRast)

#list possible values
field_lst = unique_values(valuTable, fields)
#create a field for each possible value
for val in field_lst:
    name = "pctea_" + str(val)
    arcpy.AddField_management(outTbl, name, "DOUBLE")
    #select polyRast with that value
    arcpy.MakeFeatureLayer_management(polyRast, "polyRast")
    whereClause = "gridcode = '" + val + "'"
    arcpy.SelectLayerByAttribute_management("polyRast", "NEW_SELECTION", whereClause)
    #get percent areas
    val_lst = percent_cover("polyRast", outTbl)
    #add to table
    lst_to_field(outTbl, name, val_lst)
