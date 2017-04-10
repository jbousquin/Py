###FUNCTIONS###
"""Unique Values
Purpose: returns a sorted list of unique values"""
#Function Notes: used to find unique field values in table column
#return sorted({row[0] for row in cursor if row[0]}) #removes zeros
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


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

#make a list of all the FC in gdb
#loop over list
#for each state in TIGER, select, copy, project
#for each state in SSURGO, joinField the "pctearthmc" field
#for each value in joined field, percent cover


#table with mukey & NCCPI valu
valuTable = r"C:\ArcGIS\Local_GIS\HWBI\SSURGO\gSSURGO_RI.gdb\valu1"
#table with mukey & farmland designation
farmTable = r"C:\ArcGIS\Local_GIS\HWBI\SSURGO\gSSURGO_RI.gdb\mapunit"
#NCCPI field in valuTable
fields = "pctearthmc"
#fields = ["pctearthmc","farmlndcl"]


#SET UP COUNTIES/RESULTS DATSETS
cnty = r"C:\ArcGIS\Local_GIS\HWBI\HWBI.gdb\TIGER_FULL_prj"
stField = "STATEFP10"




#database holding state SSURGO data
inGDB = r"C:\ArcGIS\Local_GIS\HWBI\SSURGO\soilmu_State.gdb"
for FC in FC_List:
#each state SSURGO
FC = "soil_mu_a_ri" #delete
inFC = inGDB + os.sep + FC 
#join the data from valu table

#find the corresponding state in counties
arcpy.MakeFeatureLayer_management(inFC, "state_lyr")
arcpy.SelectLayerByAttribute_management("state_lyr", "NEW_SELECTION", "OBJECTID = 1")
arcpy.MakeFeatureLayer_management(cnty, "cnty_lyr")
arcpy.SelectLayerByLocation_management("cnty_lyr", "INTERSECT", "state_lyr")
with arcpy.da.SearchCursor("cnty_lyr", [stField]) as cursor:
    for row in cursor:
        P10 = stField + " = '" + str(row[0]) + "'"

arcpy.SelectLayerByAttribute_management("cnty_lyr", "NEW_SELECTION", P10)
#make output for that state
st_cnty = cnty + "_" + FC[-2:]
arcpy.CopyFeatures_management("cnty_lyr", st_cnty)

#loop over possible values
field_lst = unique_values(valuTable, fields)
for val in field_lst:
    name = "pctea_" + str(val)
    print("Addding " + name + " field...")
    arcpy.AddField_management(st_cnty, name, "DOUBLE")

    #select poly soil with that value
    whereClause = str(fields) + " = " + str(val)
    arcpy.SelectLayerByAttribute_management("state_lyr", "NEW_SELECTION", whereClause)
    #check that the value is in the selection
    if arcpy.GetCount_management("state_lyr") >1:
        #loop over counties in st_cnty, doing percent cover 
        val_lst = percent_cover("state_lyr", st_cnty)
    else:
        val_lst = [0]
    print("Populating " + name + " field...")
    lst_to_field(st_cnty, name, val_lst)
        
