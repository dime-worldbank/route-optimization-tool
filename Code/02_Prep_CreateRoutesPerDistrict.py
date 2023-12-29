# -*- coding: cp1252 -*-
import sys
sys.path.append("C:/Program Files (x86)/ArcGIS/Desktop10.7/ArcToolBox/Scripts")
sys.path.append("C:/Program Files (x86)/ArcGIS/Desktop10.7/bin")
sys.path.append("C:/Program Files (x86)/ArcGIS/Desktop10.7/ArcPy")
sys.path.append("C:/Python27/ArcGIS10.7")
sys.path.append("C:/Python27/ArcGIS10.7/lib")
sys.path.append("C:/Python27/ArcGIS10.7/libs")
sys.path.append("C:/Python27/ArcGIS10.7/DLLs")
sys.path.append("C:/Program Files (x86)/ArcGIS/Desktop10.8/ArcToolBox/Scripts")
sys.path.append("C:/Program Files (x86)/ArcGIS/Desktop10.8/bin")
sys.path.append("C:/Program Files (x86)/ArcGIS/Desktop10.8/ArcPy")
sys.path.append("C:/Python27/ArcGIS10.8")
sys.path.append("C:/Python27/ArcGIS10.8/lib")
sys.path.append("C:/Python27/ArcGIS10.8/lib/site-packages/numpy")
sys.path.append("C:/Python27/ArcGIS10.8/libs")
sys.path.append("C:/Python27/ArcGIS10.8/DLLs")
#sys.path.remove("C:/Windows/SYSTEM32/python27.zip")
#sys.path.remove("C:/Users/tivo9652/AppData/Roaming/Python/Python27/site-packages")
import winsound
duration = 1000  # milliseconds
freq = 440  # Hz
import arcpy, os, shutil, arceditor, subprocess, time, random, glob, csv
arcpy.CheckOutExtension("Network")
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *
##from functions import *
arcpy.ImportToolbox("C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Toolboxes/Features_to_GPX/FeaturesToGPX.tbx")
arcpy.gp.toolbox = "C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Toolboxes/Features_to_GPX/FeaturesToGPX.tbx";
arcpy.ImportToolbox("C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Toolboxes/SpatialJoinLargestOverlap/SpatialJoinLargestOverlap.tbx")
arcpy.gp.toolbox = "C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Toolboxes/SpatialJoinLargestOverlap/SpatialJoinLargestOverlap.tbx"
### Set environment ###
# Allow the overwriting of the output files
arcpy.env.overwriteOutput = True # This command is CASE-SENSITIVE
arcpy.env.outputMFlag = "Disabled"
arcpy.env.outputZFlag = "Disabled"
arcpy.env.parallelProcessingFactor = "100%"
work_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(os.path.dirname(os.getcwd()))
arcpy.env.scratchWorkspace = 'C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/scratch'
Scratch='C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/scratch'

print(os.getcwd())

try:
    shutil.rmtree(Scratch)
except:
    pass
os.mkdir(Scratch)

##############
# Parameters #
##############
par_targetCrossingsPerMAGroup=105  # This parameter does ABC; typical value 70
par_averageSpeed=35
par_averageSpeedPaved=51
par_highMACutoff=26000
par_timeAtCrossing=15
par_timeAtHalfway=3

##########
# Inputs #
##########
# roads and districts
distBoundaries = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Input/moz_adm_20190607_shp/moz_admbnda_adm2_ine_20190607.shp"
roads_in_nampula_and_zambezia = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Input/roads_in_nampula_and_zambezia_exclMemba.shp"
startPoints_survey = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Input/startPoints_survey.shp"

# points of interest
LCCkpts = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Imput/pointsForLCCkpts_4thRound.shp"
mktsFor2ndRound = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Input/marketsCleanedFor2ndRound.shp"
feirasFor2ndRound = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Input/feirasCleanedFor4thRound.shp"
allInfo_crossingLevel ="C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Input/allInfo_crossingLevel.shp"
TandCRoads = "Input\TandCRoads.shp"
#for route solver
Routes = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Imput/testRoute.csv"
Breaks = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Imput/testBreak.csv"

###########
# Outputs #
###########
roadsNetwork_shp = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/roadsNetwork.shp"
roadsNetworkDissolve_shp = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/roadsNetworkDissolve.shp"
roadsNetworkParts_shp = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/roadsNetworkParts.shp"
#network = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/roadsNetwork_ND.nd"
network = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/network.gdb/roadsNetwork/roadsNetwork_ND"
roadIntersectionsAndEndPoints="C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/roadIntersectionsAndEndPoints.shp"
roadsNetworkPartsCentroids="C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/roadsNetworkPartsCentroids.shp"
allInterceptPoints="C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/allInterceptPoints.shp"
distBoundariesUpdated = "C:/Users/Idelson Mindo/Documents/GitHub/routes_RTMOZ/Output/createRouteDistrict/network/distBoundariesUpdated.shp"

try:
    try:
        arcpy.Delete_management("Temporary/WorkingWithRoutes4thRound.gdb")
        print("Delete GDB")
    except:
        pass
    # Process: Create File GDB
    arcpy.CreateFileGDB_management("Temporary", "WorkingWithRoutes4thRound")
    print("Create GDB")
    path="Temporary/WorkingWithRoutes4thRound.gdb"

    # Select Chinde and Luabo features
    arcpy.Select_analysis(distBoundaries, f"{path}/distBoundary_Chinde", '"ADM2_PT" = \'Chinde\'')
    arcpy.Select_analysis(distBoundaries, f"{path}/distBoundary_Luabo", '"ADM2_PT" = \'Luabo\'')

    # Merge Chinde and Luabo features
    arcpy.Merge_management([f"{path}/distBoundary_Chinde", f"{path}/distBoundary_Luabo"], f"{path}/ChindeLuabo")

    # Dissolve the merged features
    arcpy.Dissolve_management(f"{path}/ChindeLuabo", f"{path}/ChindeLuaboDiss", "", "", "MULTI_PART", "DISSOLVE_LINES")

    # Add a new field "ADM2_PT" and calculate its value as 'ChindeLuabo' for all records
    arcpy.AddField_management(f"{path}/ChindeLuaboDiss", "ADM2_PT", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(f"{path}/ChindeLuaboDiss", "ADM2_PT", "'ChindeLuabo'", "PYTHON_9.3", "")
    print("merge Chinde Luabo")


    arcpy.Merge_management("{};{}/ChindeLuaboDiss".format(distBoundaries,path),distBoundariesUpdated)
    print("finishMerge")

    # GENERATE ROAD NETWORK DATASET #
    arcpy.Project_management(roads_in_nampula_and_zambezia, "{}/roadsMergedProjected".format(path), "PROJCS['WGS_1984_UTM_Zone_36S',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',33.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")
    arcpy.Select_analysis("{}/roadsMergedProjected".format(path), "{}/roadsMergedProjectedSelected".format(path), '"LINK_ID_NE" NOT IN (\'T07131\', \'T08553\')') # select only those markets within 1.5km from road
    arcpy.CalculateField_management("{}/roadsMergedProjectedSelected".format(path), "KM", "!Shape_Length! / 1000", "PYTHON", "")
   




    # Define the path to the 'roadsMergedProjectedSelected' feature class
    feature_class = "{}/roadsMergedProjectedSelected".format(path)  # Make sure 'path' is defined in your script

    # Create a SearchCursor to iterate through the features
    #with arcpy.da.SearchCursor(feature_class, ["KM"]) as cursor:
     #   for row in cursor:
            #field1_value = row[0]  # Replace "FIELD1" with the actual field name
            #field2_value = row[1]  # Replace "FIELD2" with the actual field name
      #      km_value = row[0]  # Assuming "KM" is the field name
            #speed4rout_value = row[3]  # Assuming "Speed4Rout" is the field name
            #time_taken_value = row[4]  # Assuming "timeTaken" is the field name

            # Print the values of the fields for each feature
       #     print(f"KM: {km_value}")


 
    arcpy.CopyFeatures_management("{}/roadsMergedProjectedSelected".format(path), roadsNetwork_shp)
    expression = 'speedSet(!SURF_TYP_1!)'
    arcpy.CalculateField_management(roadsNetwork_shp, 'timeTaken', 'expression', 'PYTHON')


    #arcpy.AddField_management(roadsNetwork_shp, "Speed4Rout", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    print("Added field")
   
    codeblock = """
        def speedSet(pavement):
        if pavement == 'Paved':
            return {}
        else:
            return {}
    """.format(par_averageSpeedPaved, par_averageSpeed)

    

    # Calculate the 'KM' field
    #arcpy.CalculateField_management(roadsNetwork_shp, "KM", "!Shape_Length! / 1000", "PYTHON", "")

    # Add the 'timeTaken' field
    #arcpy.AddField_management(roadsNetwork_shp, "timeTaken", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    # Calculate the 'timeTaken' field using 'KM' and 'Speed4Rout'
    #arcpy.CalculateField_management(roadsMergedProjectedSelected, "timeTaken", "[KM] / [Speed4Rout]", "PYTHON", "")


    #arcpy.CalculateField_management(roadsNetwork_shp, "Speed4Rout", expression, "PYTHON_9.3", codeblock)
    #arcpy.AddField_management(roadsNetwork_shp, "timeTaken", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    #arcpy.CalculateField_management(roadsNetwork_shp, "timeTaken", "[KM]/[Speed4Rout]", "PYTHON", "")

    winsound.Beep(freq, duration)
    text = input("Recreate network dataset if necessary. ")
    #text = raw_input("Recreate network dataset if necessary. ") # This step has to be done manually in ArcMap. I'll explain once we have the software running for you.
    
    # Merge `feirasFor2ndRound` with some other dataset and save the result as "mktsAndFeiras"
    arcpy.Merge_management([feirasFor2ndRound], "{}/mktsAndFeiras".format(path))

    # Add a "ServiceTime" field to the "allInfo_crossingLevel" dataset and calculate values for it using the "par_timeAtCrossing" field
    arcpy.AddField_management(allInfo_crossingLevel, "ServiceTim", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(allInfo_crossingLevel, "ServiceTim", "!{}".format(par_timeAtCrossing), "PYTHON")

    # Dissolve lines in the "roadsNetwork_shp" dataset
    arcpy.Dissolve_management(roadsNetwork_shp, roadsNetworkDissolve_shp, "", "", "MULTI_PART", "DISSOLVE_LINES")

    # Convert the vertices to points
    arcpy.FeatureVerticesToPoints_management(roadsNetworkDissolve_shp, roadIntersectionsAndEndPoints, "BOTH_ENDS")

    # Project the resulting points
    arcpy.Project_management(startPoints_survey, "{}\\startPoints_surveyProjected".format(path), "PROJCS['WGS_1984_UTM_Zone_36S',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',33.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")
 
 # ROUTES PER DISTRICT - Snap markets to intersections and endings - all intersections and markets should always be at least road check points - but not river crossings #
    #arcpy.Snap_edit("{}\\startPoints_surveyProjected".format(path), "{} VERTEX '250 Meters'".format(roadIntersectionsAndEndPoints))
    arcpy.Snap_edit("{}\\startPoints_surveyProjected".format(path), 
                    [[roadIntersectionsAndEndPoints, "VERTEX", "250 Meters"], 
                    [roadsNetworkDissolve_shp, "EDGE", "250 Meters"]])
    
    arcpy.Snap_edit(mktsFor2ndRound, 
                    [[roadIntersectionsAndEndPoints, "VERTEX", "500 Meters"], 
                    [roadsNetworkDissolve_shp, "EDGE", "500 Meters"]])
    
    arcpy.Snap_edit(feirasFor2ndRound, 
                        [[roadIntersectionsAndEndPoints, "VERTEX", "500 Meters"], 
                        [roadsNetworkDissolve_shp, "EDGE", "500 Meters"]])
   


    # Define the paths to the feature classes
    intersection_path = roadIntersectionsAndEndPoints
    mkts_and_feiras_path = "{}\\mktsAndFeiras".format(path)
    all_intercept_points_path = allInterceptPoints

    # List of feature classes to merge
    feature_classes_to_merge = [intersection_path, mkts_and_feiras_path]

    # Merge the feature classes
    arcpy.Merge_management(feature_classes_to_merge, all_intercept_points_path)
    arcpy.Integrate_management("Output/createRouteDistrict/network/allInterceptPoints.shp", "500 Meters")

  
    arcpy.DeleteIdentical_management(allInterceptPoints, "Shape", "50 Meters")
    arcpy.Snap_edit(allInterceptPoints, 
                        [[roadIntersectionsAndEndPoints, "VERTEX", "500 Meters"], 
                        [roadsNetworkDissolve_shp, "EDGE", "500 Meters"]])
    
   
    arcpy.SplitLineAtPoint_management(roadsNetworkDissolve_shp, allInterceptPoints, roadsNetworkParts_shp, "10 Meters")
    arcpy.AddGeometryAttributes_management(roadsNetworkParts_shp, "LINE_START_MID_END", "", "", "")
    arcpy.AddField_management(roadsNetworkParts_shp, "RoadSegId", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")



# Assuming that START_Y and END_Y are field names in roadsNetworkParts_shp
    arcpy.CalculateField_management(roadsNetworkParts_shp, "RoadSegId", "str(!START_Y!) + ' and ' + str(!END_Y!)", "PYTHON", "")


    arcpy.FeatureToPoint_management(roadsNetworkParts_shp, roadsNetworkPartsCentroids, "INSIDE")

    arcpy.CopyFeatures_management(mktsFor2ndRound, "{}\\marketsCloseToRoadsPre".format(path), "", "0", "0", "0")

    arcpy.Near_analysis("{}\\marketsCloseToRoadsPre".format(path), roadsNetworkDissolve_shp, "1500 Meters", "", "NO_ANGLE", "GEODESIC")
    arcpy.Select_analysis("{}\\marketsCloseToRoadsPre".format(path), "{}\\marketsCloseToRoads".format(path), "\"NEAR_DIST\" >0") # select only those markets within 1.5km from road

    arcpy.CopyFeatures_management("{}\\mktsAndFeiras".format(path), "{}\\feirasCloseToRoadsPre".format(path), "", "0", "0", "0")

    arcpy.Near_analysis("{}\\feirasCloseToRoadsPre".format(path), roadsNetworkDissolve_shp, "1500 Meters", "", "NO_ANGLE", "GEODESIC")
    arcpy.Select_analysis("{}\\feirasCloseToRoadsPre".format(path), "{}\\feirasCloseToRoads".format(path), "\"NEAR_DIST\" >0") # select only those markets within 1.5km from road
    
    # Road halfway points
    arcpy.FeatureToPoint_management(TandCRoads, "{}\\roadHalfwayPoints".format(path), "INSIDE")
    arcpy.DeleteField_management("{}\\roadHalfwayPoints".format(path), "district")

# Return geoprocessing specific errors
except arcpy.ExecuteError:
    print(arcpy.GetMessages())

# Return any other type of error
except Exception as e:
    print("There is a non-geoprocessing error.")
    print(e)
### Release the memory ###
print("Closing ArcGIS 10")
del arcpy

winsound.Beep(freq, duration)
    
