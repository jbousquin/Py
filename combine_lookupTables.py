# File to copy valu1 table and farm table desired fields into main database.
#Master table in main database with desired fields must already exist.
#All gSSURGO.zip files should be downloaded to dir_name directory.
#zipfiles will not be harmed, unzipped geodatabases will be deleted.
import os
import zipfile
import shutil
import arcpy

master = r"C:\ArcGIS\Local_GIS\HWBI\HWBI.gdb\Valu1"
keyID = "mukey"

#download request?
#unzip all in folder
dir_name = r"C:\ArcGIS\Local_GIS\HWBI\SSURGO\gSSURGO" #directory
ext = ".zip" #extension

#loop through files in folder
for item in os.listdir(dir_name):
    #check files for extension
    if item.endswith(ext):
        #name of zip zip file
        file_name = dir_name + os.sep + item
        #create folder using filename
        #new_folder = item[:-4]
        #if not os.path.exists(new_folder):
            #os.makedirs(new_folder)
        #create zipfile obj
        zip_obj = zipfile.ZipFile(file_name)
        #extract it to the directory
        zip_obj.extractall(dir_name)
        zip_obj.close() #close file
        #delete original zip file
        #os.remove(file_name)

#loop through each state
for state in os.listdir(dir_name):
    #check that folder is a gdb
    if item.endswith(".gdb"):
        state_gdb = dir_name + os.sep + item
        #table with mukey & NCCPI valu
        valuTable = state_gdb + "Valu1"
        #table with mukey & farmland designation
        farmTable = state_gdb + "mapunit"
        #Join farm class to valu1 in state gdb
        arcpy.JoinField_management(valuTable, keyID, farmTable, keyID, ["farmlndcl"])
        #append joined table to master
        arcpy.Append_management(valuTable, master, schema_type="NO_TEST")
        #delete state_gdb and contents
        shutil.rmtree(state_gdb)
