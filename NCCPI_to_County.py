import arcpy
import decimal


def dec(x):
    """decimal.Decimal"""
    return decimal.Decimal(x)


def unique_values(table, field):
    """Unique Values
    Purpose: returns a sorted list of unique values
    Notes: used to find unique field values in table column
        return sorted({row[0] for row in cursor if row[0]}) #removes zeros
    """
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def percent_cover(poly, bufPoly, units = "SQUAREMETERS"):
    """Percent Cover
    Purpose:"""
    arcpy.MakeFeatureLayer_management(poly, "poly")
    lst=[]
    orderLst=[]
    #add handle for when no overlap?
    with arcpy.da.SearchCursor(bufPoly, ["SHAPE@", "OID@"]) as cursor:
        for row in cursor:
            totalArea = dec(row[0].getArea("PLANAR", units))
            arcpy.SelectLayerByLocation_management("poly", "INTERSECT", row[0])
            lyrLst = []
            with arcpy.da.SearchCursor("polyLyr", ["SHAPE@"]) as cursor2:
                for row2 in cursor2:
                    #dimension = 4 for polygon
                    interPoly = row2[0].intersect(row[0], 4)
                    interArea = dec(interPoly.getArea("PLANAR", units))
                    lyrLst.append((interArea/totalArea)*100)
            lst.append(sum(lyrLst))
            orderLst.append(row[1])
    arcpy.Delete_management("poly")
    #sort by ORIG_FID
    orderLst, lst = (list(x) for x in zip(*sorted(zip(orderLst, lst))))
    
    return lst


def lst_to_field(table, field, lst): #handle empty list
    """Add List to Field
    Purpose:
    Notes: 1 field at a time
    Example: lst_to_field(featureClass, "fieldName", lst)
    """
    if len(lst) ==0:
        print("No values to add to '{}'.".format(field))
    else:
        i=0
        with arcpy.da.UpdateCursor(table, [field]) as cursor:
            for row in cursor:
                row[0] = lst[i]
                i+=1
                cursor.updateRow(row)


#SET UP COUNTIES/RESULTS DATSETS
##counties = r"C:\ArcGIS\Local_GIS\HWBI\HWBI.gdb\TIGER_FULL_prj_smooth"
stField = "STATEFP10"
soils = r'C:\ArcGIS\Local_GIS\HWBI\SSURGO\soilmu_State.gdb\soil_mu_a_US_dissolved'

#list of fields to add to counties
add_field_list = ["NCCPI", "pct_1", "pct_05", "pct_0",
                  "pctearth", "farmClass", "pctNULL"]
#add fields to counties
##for field in add_field_list:
##    arcpy.AddField_management(counties, field, "DOUBLE") 

# Make layer for soils
arcpy.MakeFeatureLayer_management(soils, "soilLyr")

#units for calculations
units = "SQUAREMETERS"

# fields being manipulated
cnty_field_list = ["SHAPE@", "NCCPI", "pctearth", "pct_1", "pct_05", "pct_0",
                   "farmClass", "pctNULL"]
soil_field_list = ["SHAPE@", "nccpi2all", "pctearthmc", "farmlndcl"]

# loop county by county    
with arcpy.da.UpdateCursor(counties, cnty_field_list) as cursor:
    for cnty in cursor:
        cnty_Area = dec(cnty[0].getArea("PLANAR", units))
        arcpy.SelectLayerByLocation_management("soilLyr", "INTERSECT", cnty[0])
        # reset list for this county
        lyrLst = []
        NCCPI_lst = []
        pct_earth_list = []
        area_1_list = []
        area_05_list = []
        area_0_list = []
        
        # loop, survey by survey
        # soil_field_list = ["SHAPE@", "nccpi2all", "pctearthmc", "farmlndcl"]
        with arcpy.da.SearchCursor("soilLyr", soil_field_list) as cursor2:
            for survey in cursor2:
                #get just the area the two intersect
                p = 4 #polygon dimension
                interPoly = survey[0].intersect(cnty[0], p)
                interArea = dec(interPoly.getArea("PLANAR", units))

                #Append area to lists for fields
                #soil survey percent of county area
                pct =(interArea/cnty_Area)

                #NCCPI is value * percent of county area
                NCCPI_lst.append(survey[1]/pct) #pct_list[-1] if append

                #pctearthmc is percent * percent of county area
                pct_earth_list.append(survey[2]/pct)
                
                #depending on field value append to different lists
                #pct_1 (1 case)
                if survey[3].startswith("A"):
                    area_1_list.append(interArea)
                #pct_05 (9 cases)
                elif survey[3].startswith("P"):
                    area_05_list.append(interArea)
                #pct_0 (1 case OR 13 cases)
                elif survey[3].startswith("N") or survey[3].startswith("F"):
                    area_0_list.append(interArea)
                else:
                    print("ERROR: VALUE in farnlndcl is " + str(survey[3]))               
                
        #cnty_field_list = ["SHAPE@", "NCCPI", "pctearth", "pct_1", "pct_05", "pct_0",
        #                   "farmClass", "pctNULL"]
        #sum lists and add to county
        cnty[1] = sum(NCCPI_lst)
        cnty[2] = sum(pct_earth_list)

        #add up measured areas
        tot_area_earth = sum(area_1_list) + sum(area_05_list) + sum(area_0_list)
        cnty[3] = sum(area_1_list)/tot_area_earth
        cnty[4] = sum(area_05_list)/tot_area_earth
        cnty[5] = sum(area_0_list)/tot_area_earth
        cnty[6] = cnty[2]*1 + (cnty[3]*0.5)
        cnty[7] = ((cnty_Area - tot_area_earth)/cnty_Area)*100

        # Update the cursor with the updated list
        cursor.updateRow(cnty)
