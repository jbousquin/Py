import os, sys
import arcpy
from arcpy import env

arcpy.env.workspace = r"L:\Public\jbousqui\GED\GIS\SSURGO\SSURGO_Batch"
output_gdb=r"L:\Public\jbousqui\GED\GIS\SSURGO\SSURGO_Batch\soilmu_State.gdb"
#list of states
state_lst = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi','id', 'il', 'in',
             'ia', 'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv',
             'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn',
             'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy']
#for state in states_lst:
for state in state_lst:
    output_file = output_gdb + os.sep + "soil_mu_a_" + state
    file_name = "soil_" + state + "*"
    file_lst = []
    #create list of all folders using state*
    folder_lst = arcpy.ListFiles(file_name)
    for folder in folder_lst:
        fileString = str(folder) + os.sep + "spatial" + os.sep + "soilmu_a_" + folder[5:] + ".shp"
        file_lst.append(fileString)
    arcpy.Merge_management(file_lst, output= output_file)

#combine all into one continuous
output_US = output_gdb + os.sep + "soil_mu_a_US"
arcpy.env.workspace = r"L:\Public\jbousqui\GED\GIS\SSURGO\SSURGO_Batch\soilmu_State.gdb"
state_layer_list = arcpy.ListFeatureClasses()
arcpy.Merge_management(state_layer_list, output= output_US)
