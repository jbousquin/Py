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
########
##VARS##
#inRaster with mukey
inRaster = r"L:\Public\jbousqui\GED\GIS\SSURGO\gSSURGO\soils_GSSURGO_ri_3389290_01\soils\gssurgo_g_ri\gSSURGO_RI.gdb\MapunitRaster_ri_10m"
#mukey
keyID = "MUKEY"
#table with mukey & NCCPI valu
valuTable = r"L:\Public\jbousqui\GED\GIS\SSURGO\gSSURGO\soils_GSSURGO_ri_3389290_01\soils\gssurgo_g_ri\gSSURGO_RI.gdb\valu1"
#NCCPI field
fields = ["pctearthmc"]
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
#convert raster to polygon
arcpy.RasterToPolygon_conversion(inRaster, polyRast, "NO_SIMPLIFY", keyID)

#join NCCPI field
arcpy.JoinField_management(polyRast, keyID, valuTable, keyID, fields)

#list possible values
field_lst = unique_values(valuTable, fields[0])
#create a field for each possible value
for val in field_lst:
    name = "pctea_" + str(val)
    arcpy.AddField_management(outTbl, name, "DOUBLE")
    #select polyRast with that value
    arcpy.MakeFeatureLayer_management(polyRast, "polyRast")
    whereClause = fields[0] + " = '" + val + "'"
    arcpy.SelectLayerByAttribute_management("polyRast", "NEW_SELECTION", whereClause)
    #get percent areas
    val_lst = percent_cover("polyRast", outTbl)
    #add to table
    lst_to_field(outTbl, name, val_lst)
    
#arcpy.RasterToPolygon_conversion(in_raster="MapunitRaster_ri_10m", out_polygon_features="L://Public//jbousqui//GED//GIS//HWBI.gdb/polyRast", simplify="NO_SIMPLIFY", raster_field="Valu1.pctearthmc")
