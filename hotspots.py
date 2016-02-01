#make sure to have remapped TCD layer (0-10 as NoData, >10 as 1)
#set indir to AOI (country or other AOI)

import os
import arcpy
from arcpy.sa import *
import time
start = datetime.datetime.now()
#''' Section 1: Set environments ##############################################################################'''
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"

#''' Section 2: Set directories ##############################################################################'''
indir = r'D:\_sam\hot_spot\liberia\split\ID0.shp'
#------------------------------------
maindir = r'D:\_sam\hot_spot\liberia\012816\set_buffer_10k'
outdir = os.path.join(maindir,"outdir")

#'''Section 3: set path to mosaic files #################################################################'''
lossyearmosaic = r'D:\_sam\mosaics.gdb\lossdata_2001_2014'
tcdmosaic = r'D:\_sam\liberia\mosaics.gdb\treecoverdensity_2000'
hansenareamosaic = r'H:\gfw_gis_team_data\mosaics.gdb\hansen_area'

#'''Section 4: Set environments (part 2) #####################################################################'''
scratch_gdb = os.path.join(maindir,"scratch.gdb")
if not os.path.exists(scratch_gdb):
    arcpy.CreateFileGDB_management(maindir,"scratch.gdb")
scratch_workspace = os.path.join(maindir,"scratch.gdb")
arcpy.env.scratchWorkspace = scratch_workspace
arcpy.env.workspace = outdir
arcpy.env.snapRaster = hansenareamosaic

#'''Section 5: main body of script ############################################################################'''
#change buffer distance to suit aoi of script.
print "     buffering aoi"
f = os.path.basename(indir).split(".")[0]
outbuff =os.path.join(maindir,f+"_buff.shp")
arcpy.Buffer_analysis(indir, outbuff, '10 Kilometers')
print str(datetime.datetime.now() - start)
print "     extracting by mask"
outExtractbyMask = ExtractByMask(lossyearmosaic,outbuff)
print str(datetime.datetime.now() - start)
print "     multiplying"
outMult =outExtractbyMask*Raster(tcdmosaic)
print str(datetime.datetime.now() - start)
print "     converting to point"
outpoint = os.path.join(maindir,f+"_hs_points.shp")
arcpy.RasterToPoint_conversion(outMult, outpoint, "VALUE")
print str(datetime.datetime.now() - start)
print "     projecting"
outprj = os.path.join(maindir,f+"_hs_points_prj.shp")
out_coordinate_system = arcpy.SpatialReference('Eckert IV (world)')
arcpy.Project_management(outpoint, outprj, out_coordinate_system)
print str(datetime.datetime.now() - start)
print "     adding columns"
arcpy.AddField_management(outprj, "date", "DATE")
print str(datetime.datetime.now() - start)
print "     calculating date"
layer = arcpy.MakeFeatureLayer_management(outprj, "aoi_lyr")
arcpy.SelectLayerByAttribute_management(layer,"NEW_SELECTION", "GRID_CODE <10")
arcpy.CalculateField_management(layer, field="date", expression=""""1/1/200"+str(!GRID_CODE!)""", expression_type="PYTHON_9.3", code_block="")

arcpy.SelectLayerByAttribute_management(layer,"NEW_SELECTION", "GRID_CODE >=10")
arcpy.CalculateField_management(layer, field="date", expression=""""1/1/20"+str(!GRID_CODE!)""", expression_type="PYTHON_9.3", code_block="")
print str(datetime.datetime.now() - start)
#

# print "     create space time cuuuube"
# netcdf = os.path.join(maindir,f+"_hs.nc")
# arcpy.CreateSpaceTimeCube_stpm(outprj,netcdf,"date","","1 Years","","","2.5 Kilometers")
# print "     create emerging hotspots"
# hotspots = os.path.join(maindir,f+"_hs_final.shp")
# arcpy.EmergingHotSpotAnalysis_stpm(netcdf,"COUNT",hotspots, "",1)

