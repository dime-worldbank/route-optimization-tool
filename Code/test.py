def PerDist_function(Routes, Orders, nameAdd1, nameAdd2, count):
    global Breaks

    #dist =  # Add the logic to define 'dist'

    try:
        # Creating temporary directory if it doesn't exist
        temp_dir = "../Temporary"
        os.makedirs(temp_dir, exist_ok=True)
        print("Created temporary directory:", temp_dir)

        # Creating output directory if it doesn't exist
        output_dir = "../OutputVRP"
        os.makedirs(output_dir, exist_ok=True)
        print("Created output directory:", output_dir)

        # Copying Routes table to the temporary directory
        arcpy.TableToTable_conversion(Routes, temp_dir, "routes_{}".format(dist))
        print("Copied Routes table to temporary directory")

        # Selecting rows in the Routes table
        arcpy.TableSelect_analysis("{}/routes_{}".format(temp_dir, dist), "{}/routesSel_{}".format(temp_dir, dist),
                                   "\"la\" <= {}".format(count))
        print("Selected rows in the Routes table")

        # Copying Breaks table to the temporary directory
        arcpy.TableToTable_conversion(Breaks, temp_dir, "breaks_{}".format(dist))
        print("Copied Breaks table to temporary directory")

        # ... (omitting the rest of the code for brevity)
        listforMergePerDistrict=""
        # Looping through bases
        for base in range(1, count + 1):
            try:
                # Deleting existing geodatabase if it exists
                gdb_path = "Temporary/WorkingWithRoutes{}_dist{}_base{}.gdb".format(nameAdd1, dist, base)
                if arcpy.Exists(gdb_path):
                    arcpy.Delete_management(gdb_path)
                    print("Deleted existing geodatabase:", gdb_path)
            except Exception as e:
                print("Error deleting existing geodatabase:", e)

            try:
                # Creating a new file geodatabase
                arcpy.CreateFileGDB_management("Temporary", "WorkingWithRoutes{}_dist{}_base{}.gdb".format(nameAdd1, dist, base))
                print("Created new geodatabase:", gdb_path)

                # Set the path to the newly created geodatabase
                pathGDB = "../Temporary/WorkingWithRoutes{}_dist{}_base{}.gdb".format(nameAdd1, dist, base)
                print("Base:", base)

                # Removing existing output folder if it exists
                output_folder_path = "C:/Users/idels/Documents/github/route-optimization-tool/OutputVRP/{}/Base{}{}".format(dist, nameAdd2, base)
                if os.path.exists(output_folder_path):
                    shutil.rmtree(output_folder_path)
                    print("Deleted existing output folder:", output_folder_path)

                # Creating a new output folder (or ensuring it exists)
                os.makedirs(output_folder_path, exist_ok=True)
                print("Created new output folder:", output_folder_path)
            except Exception as e:
                print("Error creating geodatabase or output folder:", e)
            except Exception as e:
                print("Error in PerDist_function:", e)

























import sys
import os
import shutil

districts = {
    "1": "ChindeLuabo",
    "2": "Mocubela",
    "3": "Maganja",
    "4": "Morrumbala",
    "5": "Lugela",
    "6": "Pebane",
    "7": "Memba",
    "8": "Erati",
    "9": "Monapo",
    "10": "Mossuril",
    "11": "Mogincual"
}

# Check if a command-line argument is provided
if len(sys.argv) < 2:
    print("Please provide a district key as a command-line argument.")
    sys.exit(1)

dist_key = sys.argv[-1]

# Check if the provided district key exists in the dictionary
if dist_key not in districts:
    print("Invalid district key. Please provide a valid key.")
    sys.exit(1)

dist = districts[dist_key]
print(dist)

base = 1
count = 5  # Replace with your actual count value
name_add2 = "Troco"

folder_path = os.path.abspath(f"..\\OutputVRP\\{dist}\\Base{name_add2}{base}")

# Check if the directory already exists, delete it, and then create it
if os.path.exists(folder_path):
    shutil.rmtree(folder_path)
    print(f"Existing directory deleted: {folder_path}")

# Create the directory
os.makedirs(folder_path)
print(f"Directory created: {folder_path}")










import sys
print(sys.version)

sys.path.append("C:/Program Files (x86)/ArcGIS\Desktop10.7/ArcToolBox/Scripts")
sys.path.append("C:/Program Files (x86)/ArcGIS/Desktop10.7/bin")
sys.path.append("C:/Program Files (x86)/ArcGIS/Desktop10.7/ArcPy")
sys.path.append("C:/Python27/ArcGIS10.7")
sys.path.append("C:/Python27/ArcGIS10.7/lib")
sys.path.append("C:/Python27/ArcGIS10.7/libs")
sys.path.append("C:/Python27/ArcGIS10.7/DLLs")
#sys.path.remove("C:/Windows/SYSTEM32/python27.zip")
#sys.path.remove("C:/Users/tivo9652/AppData/Roaming/Python/Python27/site-packages")
import winsound
duration = 1000  # milliseconds
freq = 440  # Hz
import arcpy, os, shutil, arceditor, glob, csv #, subprocess, time, random
import gpxpy 
import gpxpy.gpx

arcpy.CheckOutExtension("Network")
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *
import arcpy

# Get the current working directory
current_directory = os.getcwd()
print("Current Directory:", current_directory)

# Go up one level to the parent directory
parent_directory = os.path.dirname(current_directory)
print("Parent Directory:", parent_directory)


arcpy.ImportToolbox(os.path.join(parent_directory, 'toolboxes', 'FeaturesToGPX.tbx'))
arcpy.gp.toolbox = os.path.join(parent_directory, 'toolboxes', 'FeaturesToGPX.tbx');
arcpy.ImportToolbox(os.path.join(parent_directory, 'toolboxes', 'SpatialJoinLargestOverlap.tbx'))
arcpy.gp.toolbox = os.path.join(parent_directory, 'toolboxes', 'SpatialJoinLargestOverlap.tbx');
path="Temporary/WorkingWithRoutes4thRound.gdb"

def unique_values(table , field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})
    
def addRanks(table, sort_fields, category_field, rank_field='RANK'):

    # add rank field if it does not already exist
    if not arcpy.ListFields(table, rank_field):
        arcpy.AddField_management(table, rank_field, "SHORT")

    sort_sql = ', '.join(['ORDER BY ' + category_field] + sort_fields)
    query_fields = [category_field, rank_field] + sort_fields

    with arcpy.da.UpdateCursor(table, query_fields,
                               sql_clause=(None, sort_sql)) as cur:
        category_field_val = None
        i = 0
        for row in cur:
            if category_field_val == row[0]:
                i += 1
            else:
                category_field_val = row[0]
                i = 1
            row[1] = i
            cur.updateRow(row)



def generateGPX(Inp_listforMerge, Inp_path, Inp_dist, Inp_base, Inp_d, Inp_StagePre, Inp_segType, Inp_count, Inp_subseq,
                Inp_listSegType, Inp_listSegID, Inp_listSegBase, Inp_listSegBaseEnd, Inp_BaseName, Inp_BaseNameEnd,
                Inp_listSegEndLat, Inp_listSegEndLon):
    # Convert list to a string for arcpy.Merge_management
    listforMerge = "\"" + Inp_listforMerge[1:1000000] + "\""

    # Ensure the stage is formatted with leading zeros if needed
    Inp_Stage = "{:02d}".format(Inp_StagePre)

    # Define output subfolders
    output_subfolders = ["OutputVRP", "OutputVRP/base", "OutputVRP/day", "Temporary"]

    # Create folders if they do not exist
    for folder in output_subfolders:
        folder_path = os.path.join(Inp_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Merge features
    arcpy.Merge_management(listforMerge, os.path.join(Inp_path, "RoutesMerged_Dist{}_Base{}_Day{}_Stage{}"
                                                       .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)))

    # Calculate field
    arcpy.CalculateField_management(os.path.join(Inp_path, "RoutesMerged_Dist{}_Base{}_Day{}_Stage{}"
                                                  .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                                    "FIRST_Name", "'Trk_Dist{}_B{}_D{}_St{}'".format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage),
                                    "PYTHON_9.3")

    # Dissolve features
    arcpy.Dissolve_management(os.path.join(Inp_path, "RoutesMerged_Dist{}_Base{}_Day{}_Stage{}"
                                           .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                              os.path.join(Inp_path, "RoutesMergedDissolved_Dist{}_Base{}_Day{}_Stage{}"
                                           .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)), ["FIRST_Name"], "",
                              "MULTI_PART", "DISSOLVE_LINES")

    # Convert dissolved features to GPX
    arcpy.gp.FeaturesToGPX(os.path.join(Inp_path, "RoutesMergedDissolved_Dist{}_Base{}_Day{}_Stage{}"
                                         .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                           os.path.join(Inp_path, "OutputVRP/{}/Base{}{}/Day{}/Trk_Dist{}_B{}_D{}_St{}Pre.gpx"
                                        .format(Inp_dist, nameAdd2, Inp_base, Inp_d, Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                           True, True)

    print("FeaturesToGPX D{} St{}".format(Inp_d, Inp_Stage))

    # File manipulation
    orig = os.path.join(Inp_path, "OutputVRP/{}/Base{}{}/Day{}/Trk_Dist{}_B{}_D{}_St{}Pre.gpx"
                        .format(Inp_dist, nameAdd2, Inp_base, Inp_d, Inp_dist, Inp_BaseName, Inp_d, Inp_Stage))
    txt = 'Temporary/inter{}.txt'.format(Inp_dist)
    txt2 = 'Temporary/inter2{}.txt'.format(Inp_dist)
    tgt = os.path.join(Inp_path, "OutputVRP/{}/Base{}{}/Day{}/Trk_Dist{}_B{}_D{}_St{}.gpx"
                       .format(Inp_dist, nameAdd2, Inp_base, Inp_d, Inp_dist, Inp_BaseName, Inp_d, Inp_Stage))

    shutil.copyfile(orig, txt)

    gpx_file = open(orig, 'rt')
    gpx_fileNew = open(txt2, 'wt')

    gpx = gpxpy.parse(gpx_file)
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                last = '<wpt lat="{}" lon="{}"> \n <ele>1</ele> \n <name>Esta agora a 50 metros do final do etapa {}. ........... Esta agora a 50 metros do final do etapa {}. ........... Esta agora a 50 metros do final do etapa {}. </name> \n </wpt>'.format(point.latitude, point.longitude, Inp_Stage, Inp_Stage, Inp_Stage)

    for line in open(txt, 'rt'):
        gpx_fileNew.write(line.replace('<trk>', last+'\n <trk>'))

    gpx_file.close()
    gpx_fileNew.close()
    shutil.copyfile(txt2, tgt)
    os.remove(orig)
    os.remove(txt)
    os.remove(txt2)

    # Additional arcpy operations
    arcpy.AddField_management(os.path.join(Inp_path, "RoutesMergedDissolved_Dist{}_Base{}_Day{}_Stage{}"
                                           .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)), "StgType", "TEXT", "", "", "",
                              "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(os.path.join(Inp_path, "RoutesMergedDissolved_Dist{}_Base{}_Day{}_Stage{}"
                                                  .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                                    "StgType", """'{}'""".format(Inp_segType), "PYTHON_9.3", "")

    arcpy.AddField_management(os.path.join(Inp_path, "RoutesMergedDissolved_Dist{}_Base{}_Day{}_Stage{}"
                                           .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)), "Stage", "SHORT", "", "", "",
                              "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(os.path.join(Inp_path, "RoutesMergedDissolved_Dist{}_Base{}_Day{}_Stage{}"
                                                  .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                                    "Stage", Inp_StagePre, "PYTHON_9.3", "")

    arcpy.CopyFeatures_management(os.path.join(Inp_path, "RoutesMergedDissolved_Dist{}_Base{}_Day{}_Stage{}"
                                               .format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                                  os.path.join(Inp_path, "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp"
                                               .format(Inp_dist, nameAdd2, Inp_base, Inp_d, Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                                  "", "0", "0", "0")

    arcpy.AddGeometryAttributes_management(os.path.join(Inp_path, "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp"
                                                        .format(Inp_dist, nameAdd2, Inp_base, Inp_d, Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                                          "LINE_START_MID_END", "", "", "")

    cursor = arcpy.da.SearchCursor(os.path.join(Inp_path, "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp"
                                                 .format(Inp_dist, nameAdd2, Inp_base, Inp_d, Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                                   "END_Y")
    EndLat = []
    for row in cursor:
        EndLat.append(row[0])

    cursor = arcpy.da.SearchCursor(os.path.join(Inp_path, "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp"
                                                 .format(Inp_dist, nameAdd2, Inp_base, Inp_d, Inp_dist, Inp_BaseName, Inp_d, Inp_Stage)),
                                   "END_X")
    EndLon = []
    for row in cursor:
        EndLon.append(row[0])

    listSegType = Inp_listSegType
    listSegID = Inp_listSegID
    listSegBase = Inp_listSegBase
    listSegBaseEnd = Inp_listSegBaseEnd
    listSegEndLat = Inp_listSegEndLat
    listSegEndLon = Inp_listSegEndLon

    if Inp_subseq == Inp_count:
        listSegType.append(Inp_segType)
    else:
        listSegType.append("Road")

    listSegID.append("Trk_Dist{}_B{}_D{}_St{}".format(Inp_dist, Inp_BaseName, Inp_d, Inp_Stage))
    listSegBase.append(Inp_BaseName)
    listSegBaseEnd.append(Inp_BaseNameEnd)
    listSegEndLon.append(EndLon[-1])
    listSegEndLat.append(EndLat[-1])

    return listSegType, listSegID, listSegBase, listSegEndLon, listSegEndLat

def PerDist_function(Routes,Orders, nameAdd1, nameAdd2,count):
    global  Breaks
    arcpy.TableToTable_conversion(Routes, "{}".format(path), "routes_{}".format(dist))
    arcpy.TableSelect_analysis("{}/routes_{}".format(path,dist), "{}/routesSel_{}".format(path,dist), "\"la\" <={}".format(count))
    arcpy.TableToTable_conversion(Breaks, "{}".format(path), "breaks_{}".format(dist))
    # run VRP
    orders = arcpy.GetParameterValue("SolveVehicleRoutingProblem_na",0)    
    orders.load(Orders)
    print("Load orders")

    depots = arcpy.GetParameterValue("SolveVehicleRoutingProblem_na",1)
    depots.load("{}/startPoints_{}".format(path, dist))
    print("Load depots")

    Routes = "{}/routesSel_{}".format(path,dist)
    routes = arcpy.GetParameterValue("SolveVehicleRoutingProblem_na",2)    
    routes.load(Routes)
    print("Load routes")

    Breaks = "{}/breaks_{}".format(path,dist)
    breaks = arcpy.GetParameterValue("SolveVehicleRoutingProblem_na",3)    
    breaks.load(Breaks)
    print("load breaks")

    result=arcpy.na.SolveVehicleRoutingProblem(orders, depots, routes, breaks , "Minutes", "Kilometers", network, "{}".format(path), default_date="2019/10/01", save_output_layer="SAVE_OUTPUT_LAYER", populate_route_lines="ROUTE_LINES")
    arcpy.TableToTable_conversion("{}/Stops".format(path), "OutputVRP", "Stops_{}.csv".format(dist))
    arcpy.TableToTable_conversion("{}/UnassignedStops".format(path), "OutputVRP", "UnassignedStops_{}.csv".format(dist))

    solveSucceeded = result.getOutput(0)
    print("Solve Succeeded: {0}".format(solveSucceeded))
    print("Messages from solver are printed below.")
    print(result.getMessages(1))
    print(result)

    # Convert VRP output into routes 
    list_of_files = glob.glob("{}/*".format(Scratch)) 
    latest_file = max(list_of_files, key=os.path.getctime)
    vrp_lyr_obj=arcpy.mapping.Layer(latest_file)
    vrp_orders_lyr = arcpy.mapping.ListLayers(vrp_lyr_obj, 'Orders')[0]
    vrp_depots_lyr = arcpy.mapping.ListLayers(vrp_lyr_obj, 'Depots')[0]
    vrp_routes_lyr = arcpy.mapping.ListLayers(vrp_lyr_obj, 'Routes')[0]
    arcpy.CopyFeatures_management(vrp_orders_lyr, "{}/OrdersAll_{}".format(path,dist))
    arcpy.CopyFeatures_management(vrp_depots_lyr, "{}/DepotsAll_{}".format(path,dist))
    arcpy.CopyFeatures_management(vrp_routes_lyr, "{}/RoutesAll_{}".format(path,dist))
    arcpy.Select_analysis("{}/OrdersAll_{}".format(path,dist), "{}/OrdersServiced_{}".format(path,dist), " \"FromPrevTravelTime\" >  0")
    arcpy.SaveToLayerFile_management(vrp_lyr_obj, "{}/Layer_{}".format(path,dist), "ABSOLUTE")
    arcpy.Select_analysis("{}/OrdersServiced_{}".format(path,dist), "{}/OrdersServicedSelect_{}".format(path,dist), " \"Sequence\" >  0")
    RouteValues = unique_values(r"{}/OrdersServicedSelect_{}".format(path,dist) , 'RouteName')
    print(RouteValues)

    listforMergePerDistrict = ""

    for base in range(1, count + 1):
        # Delete existing geodatabase if it exists
        try:
            arcpy.Delete_management("Temporary/WorkingWithRoutes{}_dist{}_base{}.gdb".format(nameAdd1, dist, base))
            print("Deleted existing geodatabase")
        except:
            pass

        # Create a new file geodatabase
        arcpy.CreateFileGDB_management("Temporary", "WorkingWithRoutes{}_dist{}_base{}.gdb".format(nameAdd1, dist, base))
        print("Created new geodatabase")

        # Set the path
        #  to the newly created geodatabase
        pathGDB = "../Temporary/WorkingWithRoutes{}_dist{}_base{}.gdb".format(nameAdd1, dist, base)
        print("Base:", base)

        # Remove existing output folder if it exists
        try:
            shutil.rmtree("OutputVRP/{}/Base{}{}".format(dist, nameAdd2, base))
            print("Deleted existing output folder")
        except:
            print("Folder Base{} could not be deleted".format(base))

        # Create a new output folder (or ensure it exists)
        output_folder_path = "../OutputVRP/{}/Base{}{}".format(dist, nameAdd2, base)
        os.makedirs(output_folder_path, exist_ok=True)

        # Now, the inner loop for 'd' (assuming 'd' is defined somewhere in your code)
        for d in range(1, count + 1):
            try:
                os.mkdir(os.path.join(output_folder_path, "Day{}".format(d)))
            except:
                print("Day{} folder could not be created for Base{}".format(d, base))

        for d in range(1, 27):
            print("try now day {}".format(d))

            if "Route{}{}_{}".format(nameAdd1,base, d) in RouteValues:
                arcpy.Select_analysis("{}/RoutesAll_{}".format(path,dist), "{}/{}_RouteToday".format(pathGDB,dist), " \"Name\" =  'Route{}{}_{}'".format(nameAdd1,base, day))
                cursor = arcpy.da.SearchCursor("{}/{}_RouteToday".format(pathGDB,dist), "StartDepotName")
                StartDepotName = []
                for row in cursor:
                    StartDepotName.append(row[0])
                print('StartDepotName', StartDepotName)
                arcpy.Select_analysis("{}/DepotsAll_{}".format(path,dist), "{}/{}_startLoc_start".format(pathGDB,dist), " \"Name\" =  '{}'".format(StartDepotName[-1]))
                arcpy.SpatialJoin_analysis("{}/{}_startLoc_start".format(pathGDB,dist), "{}/startPoints_{}".format(path, dist),
                                               "{}/{}_startLoc_withName".format(pathGDB,dist),
                                               "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "", "")
                cursor = arcpy.da.SearchCursor("{}/{}_startLoc_withName".format(pathGDB,dist), "Base")
                BaseName = []
                for row in cursor:
                    BaseName.append(row[0])
                print('BaseNameStart',BaseName)
                BaseName=BaseName[-1]+nameAdd2
                
                cursor = arcpy.da.SearchCursor("{}/{}_RouteToday".format(pathGDB,dist), "EndDepotName")
                EndDepotName = []
                for row in cursor:
                    EndDepotName.append(row[0])
                print('EndDepotName', EndDepotName)

                arcpy.Select_analysis("{}/DepotsAll_{}".format(path,dist), "{}/{}_startLoc_end".format(pathGDB,dist), " \"Name\" =  '{}'".format(EndDepotName[-1]))
                arcpy.SpatialJoin_analysis("{}/{}_startLoc_end".format(pathGDB,dist), "{}/startPoints_{}".format(path, dist),
                                               "{}/{}_endLoc_withName".format(pathGDB,dist),
                                               "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "", "")
                cursor = arcpy.da.SearchCursor("{}/{}_endLoc_withName".format(pathGDB,dist), "Base")
                BaseNameEnd = []
                for row in cursor:
                    BaseNameEnd.append(row[0])
                print('BaseNameEnd',BaseNameEnd)
                BaseNameEnd=BaseNameEnd[-1]
                #print("Route from {} to {}".format(BaseName, BaseNameEnd))
                #d=d+1
                #print("Day", d)
                listforMergePerDay=""
                listSegID=[]
                listSegType=[]
                listSegBase=[]
                listSegBaseEnd=[]
                listSegEndLat=[]
                listSegEndLon=[]
                #os.mkdir("OutputVRP/{}/Base{}{}/Day{}".format(dist,nameAdd2,base,d))
                #os.mkdir(os.path.join("OutputVRP", str(dist), "Base{}{}".format(nameAdd2, base), "Day{}".format(d)), exist_ok=True)
                
                 # Print statements for debugging
                print("Route from {} to {}".format(BaseName, BaseNameEnd))
                print("Day", d)

                # Folder paths
                day_folder_path = os.path.join("../OutputVRP", str(dist), "Base{}{}".format(nameAdd2, base), "Day{}".format(d))

                try:
                    # Remove existing folder if it exists
                    shutil.rmtree(day_folder_path)
                except:
                    print("Folder Day{} could not be deleted".format(d))
                    pass

                # Create a new folder
                os.makedirs(day_folder_path, exist_ok=True)

                arcpy.Select_analysis("{}/OrdersServicedSelect_{}".format(path,dist), "{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB,dist,BaseName,d), " \"RouteName\" =  'Route{}{}_{}'".format(nameAdd1,base,day))
                arcpy.CopyFeatures_management("{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB,dist,BaseName,d), "OutputVRP/{}/Base{}{}/Day{}/Orders_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d), "", "0", "0", "0")

                if __name__ == '__main__':
                    addRanks("{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB,dist,BaseName,d), ['Sequence'], 'RouteName', 'orderInDay')
                cursor = arcpy.da.SearchCursor("{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB,dist,BaseName,d), "orderInDay")
                listname = []
                listOfCkpts=[]
                for row in cursor:
                    listname.append(int(row[0]))
            
                print('SequenceMax, {0}'.format(max(listname)))
                maxSeq=max(listname)
                # add base location as start and end point for daily route
                arcpy.AddField_management("{}/{}_startLoc_start".format(pathGDB,dist), "orderInDay", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                arcpy.CalculateField_management("{}/{}_startLoc_start".format(pathGDB,dist), "orderInDay", "0", "PYTHON", "")
                arcpy.AddField_management("{}/{}_startLoc_end".format(pathGDB,dist), "orderInDay", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                arcpy.CalculateField_management("{}/{}_startLoc_end".format(pathGDB,dist), "orderInDay", "{}".format(max(listname)+1), "PYTHON", "")
                arcpy.Merge_management(["{}/{}_startLoc_start".format(pathGDB,dist),"{}/{}_startLoc_end".format(pathGDB,dist),"{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB,dist,BaseName,d)]
                                       , "{}/ordersMerged_{}_Base{}_Day{}".format(pathGDB,dist, BaseName,d)) 

                Stage=1
                listforMerge=""
                Step=0
                prevRoadSegId =""
                listname=[]
                for seq in range(0,maxSeq+1): # loop over all orders - from - to
                    print("seq", seq)
                    Step=Step+1
                    arcpy.Select_analysis("{}/ordersMerged_{}_Base{}_Day{}".format(pathGDB,dist, BaseName,d),
                                          "{}/start".format(pathGDB), " \"orderInDay\" =  {}".format(seq))
                    arcpy.Select_analysis("{}/ordersMerged_{}_Base{}_Day{}".format(pathGDB,dist, BaseName,d),
                                          "{}/end".format(pathGDB), " \"orderInDay\" =  {}".format(seq+1))
                    cursor = arcpy.da.SearchCursor("{}/end".format(pathGDB), "ServiceTime")
                    for row in cursor:
                        if row[0]==par_timeAtHalfway:
                            segTypeWhole="Halfway"
                        if row[0]==par_timeAtFeira:
                            segTypeWhole="Feira"
                        elif row[0]==par_timeAtCrossing:
                            segTypeWhole="Crossing"
                        elif row[0]==par_timeAtLC:
                            segTypeWhole="LCCkpt"
                        elif row[0]==1:
                            segTypeWhole="Vertice" # to make sure that rotues go to endpoints of roads
                        else:
                            segTypeWhole="Road"

                    # create route shapefile
                    arcpy.FindClosestFacilities_na("{}/start".format(pathGDB), "{}/end".format(pathGDB), "Hours",
                                  network, "{}".format(pathGDB), "RoutesPre_Day{}_Step{}".format(d,Step),  "Directions", "ClosestFacilities",
                                  "1", "", "TRAVEL_TO", "", "NOT_USED", "GEO_LOCAL", "ALLOW_UTURNS", "",
                                                                  "", "", "time", "Hours", "Kilometers", "Kilometers", "NO_HIERARCHY", "", "", "", "", "", "TRUE_LINES_WITHOUT_MEASURES", "10 Meters",
                                                                  "", "", "", "NA Desktop", "", "", "", "", "", "", "", "NO_SAVE_OUTPUT_LAYER", "CUSTOM", "", "NO_SAVE_ROUTE_DATA")
                                                    arcpy.Project_management("{}/RoutesPre_Day{}_Step{}".format(pathGDB,d,Step), "{}/Routes_Day{}_Step{}".format(pathGDB,d,Step), "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "", "PROJCS['WGS_1984_UTM_Zone_36S',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',33.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")
                                                    arcpy.DeleteField_management("{}/Routes_Day{}_Step{}".format(pathGDB,d, Step), "Name")
                                                    arcpy.AddField_management("{}/Routes_Day{}_Step{}".format(pathGDB,d, Step), "Name", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                                                    arcpy.Delete_management("{}/Directions".format(pathGDB), "")
                                                    arcpy.Delete_management("{}/ClosestFacilities".format(pathGDB), "")
                                                    arcpy.SplitLineAtPoint_management("{}/Routes_Day{}_Step{}".format(pathGDB,d, Step), allInterceptPoints,
                                                                                      "{}/RoutesOrderSplitPre_Day{}_Step{}".format(pathGDB,d, Step), "500 Meters") # split at all intersections to get information per road segment
                                                    arcpy.Select_analysis("{}/RoutesOrderSplitPre_Day{}_Step{}".format(pathGDB,d, Step), "{}/RoutesOrderSplit_Day{}_Step{}".format(pathGDB,d, Step), "\"Shape_Length\" >0.00001")
                                                    arcpy.CreateRandomPoints_management(pathGDB, "RandomPointsAlongSeg_Day{}_Step{}".format(d, Step), "{}/Routes_Day{}_Step{}".format(pathGDB,d, Step), "0 0 250 250", "100000", "250 Meters", "POINT", "0")
                                                    arcpy.AddField_management("{}/RandomPointsAlongSeg_Day{}_Step{}".format(pathGDB,d, Step), "copy_fid", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                                                    arcpy.CalculateField_management("{}/RandomPointsAlongSeg_Day{}_Step{}".format(pathGDB,d, Step), "copy_fid", "[OID]", "PYTHON", "")
                                                    arcpy.SpatialJoin_analysis("{}/RoutesOrderSplit_Day{}_Step{}".format(pathGDB,d, Step), "{}/RandomPointsAlongSeg_Day{}_Step{}".format(pathGDB,d, Step),
                                                                               "{}/RoutesSplitPreSortPreDiss_Day{}_Step{}".format(pathGDB,d, Step), "JOIN_ONE_TO_MANY", "KEEP_ALL",
                                                                               "FacilityCurbApproach \"FacilityCurbApproach\" true true false 4 Long 0 0 ,First,#,C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Output/createRouteDistrict/network/{}/RoutesOrderSplit_Day{}_Step{},FacilityCurbApproach,-1,-1;Name \"Name\" true true false 255 Text 0 0 ,First,#,C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Output/createRouteDistrict/{}/RoutesOrderSplit_Day{}_Step{},Name,-1,-1;copy_fid \"copy_fid\" true true false 4 Long 0 0 ,First,#,C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Output/createRouteDistrict/{}/RandomPointsAlongSeg_Day{}_Step{},copy_fid,-1,-1".format(pathGDB,d, Step,pathGDB,d, Step,pathGDB,d, Step),
                                                                               "WITHIN_A_DISTANCE", "1 Meters", "")

                                                    arcpy.Dissolve_management("{}/RoutesSplitPreSortPreDiss_Day{}_Step{}".format(pathGDB,d, Step), "{}/RoutesSplitPreSort_Day{}_Step{}".format(pathGDB,d, Step), "TARGET_FID", "copy_fid MEAN;Name FIRST;FacilityCurbApproach FIRST", "SINGLE_PART", "DISSOLVE_LINES")


                                                    arcpy.Sort_management("{}/RoutesSplitPreSort_Day{}_Step{}".format(pathGDB,d, Step),
                                                                          "{}/RoutesSplit_Day{}_Step{}".format(pathGDB,d, Step), [["MEAN_copy_fid", "ASCENDING"]])
                                                    # wrong order
                                                    arcpy.FeatureToPoint_management("{}/RoutesSplit_Day{}_Step{}".format(pathGDB,d, Step), "{}/RoutesSplitCentroid_Day{}_Step{}".format(pathGDB,d, Step), "INSIDE")
                                                    arcpy.SpatialJoin_analysis("{}/RoutesSplitCentroid_Day{}_Step{}".format(pathGDB,d, Step), roadsNetworkParts_shp,
                                                                               "{}/RoutesSplitCentroidJoined_Day{}_Step{}".format(pathGDB,d, Step),"JOIN_ONE_TO_ONE", "KEEP_ALL","", "CLOSEST","50 Meters")
                                                    arcpy.SpatialJoin_analysis("{}/RoutesSplit_Day{}_Step{}".format(pathGDB,d, Step), "{}/RoutesSplitCentroidJoined_Day{}_Step{}".format(pathGDB,d, Step),
                                                                           "{}/RoutesSplitWithID_Day{}_Step{}".format(pathGDB,d,Step),"JOIN_ONE_TO_ONE", "KEEP_ALL","", "CLOSEST","50 Meters")
                                                    #RoadSegIds = unique_values(r"{}/RoutesSplitCentroidJoined_Day{}_Step{}".format(pathGDB,d, Step) , 'RoadSegId')
                                                    result = arcpy.GetCount_management("{}/RoutesSplitWithID_Day{}_Step{}".format(pathGDB,d,Step))
                                                    count = int(result.getOutput(0))
                                                    arcpy.Delete_management("{}/RoutesSplitPreSort_Day{}_Step{}".format(pathGDB,d, Step), "")
                                                    arcpy.Delete_management("{}/RoutesSplitCentroidJoined_Day{}_Step{}".format(pathGDB,d, Step), "")
                                                    arcpy.Delete_management("{}/RoutesOrderSplitDissolveVertices_Day{}_Step{}".format(pathGDB,d, Step), "")
                                                    arcpy.Delete_management("{}/RoutesOrderSplitPre_Day{}_Step{}", "")

                                                    for subseq in range(1,count+1): # merge subsegments between orders if these orders are not points to actually collect data at and if they are part of the same road segment
                                                        if subseq==count:
                                                            segType=segTypeWhole
                                                        else:
                                                            segType="Road"
                                                        
                                                        print("segType:", segType)
                                                        arcpy.Select_analysis("{}/RoutesSplitWithID_Day{}_Step{}".format(pathGDB,d,Step), "{}/RoutesSplit_Day{}_Step{}_sub{}".format(pathGDB,d, Step,subseq), " \"OBJECTID\" =  {}".format(subseq))
                                                        pathForMerge="{}/RoutesSplit_Day{}_Step{}_sub{}".format(pathGDB,d, Step,subseq)
                                                        cursor = arcpy.da.SearchCursor("{}/RoutesSplit_Day{}_Step{}_sub{}".format(pathGDB,d, Step,subseq), "RoadSegId")
                                                        for row in cursor:
                                                            print(row[0])
                                                            listname.append(row)
                                                        curbPrev=""
                                                        cursor = arcpy.da.SearchCursor("{}/RoutesSplit_Day{}_Step{}_sub{}".format(pathGDB,d, Step,subseq), "FIRST_FacilityCurbApproach")
                                                        for row in cursor:
                                                            Curb=row[0]
                                                            print("Curb:", Curb)
                                                        countInter=0 # to get at routes ending at road checkpoints and returning on the same route, which let#s the two segmetns have the same roadsegID
                                                        try:
                                                            arcpy.Intersect_analysis("{} #; {} #".format(pathForMerge, "{}/last".format(pathGDB)), "{}/intersect".format(pathGDB), "ALL", "", "INPUT")
                                                            intersects = arcpy.GetCount_management("{}/intersect".format(pathGDB))
                                                            countInter = int(intersects.getOutput(0))
                                                            print("countInter:", countInter)
                                                        except arcpy.ExecuteError:
                                                            print(arcpy.GetMessages())
                                                            print("Couldn't compute intersection")
                                                            pass
                                                        
                                                        if prevRoadSegId=="" and segType!="Crossing":  
                                                            listforMerge += ";" + "\"" + pathForMerge + "\""
                                                            print("prevRoadSegId empty")
                                                            prevRoadSegId=listname[-1]
                                                            segTypePrev=segType
                                                            curbPrev=Curb
                                                        elif prevRoadSegId=="" and segType=="Crossing": # if first point on new segment is crossing, treat separately, because roads are not always split at crossings
                                                            print("cat b")
                                                            listforMerge += ";" + "\"" + pathForMerge + "\""
                                                            generateGPX(listforMerge,pathGDB,dist,base,d,Stage, segType,count, subseq, listSegType, listSegID, listSegBase,listSegBaseEnd,BaseName,BaseNameEnd, listSegEndLat, listSegEndLon)
                                                            if Stage <10:
                                                                StageEnter="0{}".format(Stage)
                                                            else:
                                                                StageEnter="{}".format(Stage)
                                                            listforMergePerDay+= ";" + "\"" + "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,StageEnter) + "\""
                                                            Stage=Stage+1
                                                            listforMerge = ""
                                                        elif prevRoadSegId==listname[-1] and segType =="Road" and  countInter==0 or prevRoadSegId==listname[-1] and segType =="Road" and  countInter>0 and len(listforMerge)==0: # to split Uturns at ends of project roads where no checkpoint is. 
                                                            print("identical roadsegId, along Road")
                                                            listforMerge += ";" + "\"" + pathForMerge + "\""
                                                            prevRoadSegId=listname[-1]
                                                        elif countInter>0 and len(listforMerge)>0:  #                         elif prevRoadSegId==listname[-1] and segType =="Road" and  countInter>0 and len(listforMerge)>0:
                                                            print("identical roadsegId, along Road, turning")
                                                            generateGPX(listforMerge,pathGDB,dist,base,d,Stage, prevSegType,count, subseq, listSegType, listSegID, listSegBase,listSegBaseEnd,BaseName,BaseNameEnd,  listSegEndLat, listSegEndLon)
                                                            if Stage <10:
                                                                StageEnter="0{}".format(Stage)
                                                            else:
                                                                StageEnter="{}".format(Stage)
                                                            listforMergePerDay+= ";" + "\"" + "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,StageEnter) + "\""
                                                            
                                                            listforMerge = ""
                                                            Stage=Stage+1
                                                            prevRoadSegId=listname[-1]
                            listname=[]

                            listforMerge += ";" + "\"" + pathForMerge + "\""
                        elif prevRoadSegId==listname[-1] and segType !="Road": # Merge all until the current one, because current one is POI
                            print("identical roadsegId, point of Interest")
                            listforMerge += ";" + "\"" + pathForMerge + "\""
                            generateGPX(listforMerge,pathGDB,dist,base,d,Stage, segType,count, subseq, listSegType, listSegID, listSegBase,listSegBaseEnd,BaseName,BaseNameEnd, listSegEndLat, listSegEndLon)
                            if Stage <10:
                                StageEnter="0{}".format(Stage)
                            else:
                                StageEnter="{}".format(Stage)
                            listforMergePerDay+= ";" + "\"" + "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,StageEnter) + "\""

                            listforMerge = ""
                            Stage=Stage+1
                            prevRoadSegId=""

                        elif prevRoadSegId!=listname[-1] and prevSegType=="Road" and segType=="Road" : # Merge the previous one, start new collection
                            print("different roadsegId, not first point")
                            generateGPX(listforMerge,pathGDB,dist,base,d,Stage, prevSegType,count, subseq, listSegType, listSegID, listSegBase,listSegBaseEnd,BaseName,BaseNameEnd,  listSegEndLat, listSegEndLon)
                            if Stage <10:
                                StageEnter="0{}".format(Stage)
                            else:
                                StageEnter="{}".format(Stage)
                            listforMergePerDay+= ";" + "\"" + "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,StageEnter) + "\""
                            
                            listforMerge = ""
                            Stage=Stage+1
                            prevRoadSegId=listname[-1]
                            listname=[]

                            listforMerge += ";" + "\"" + pathForMerge + "\""
                        elif prevRoadSegId!=listname[-1] and prevSegType!="Road" and segType=="Road" : # Merge the previous one, start new collection
                            print("different roadsegId, first point of new segment")


                            listforMerge += ";" + "\"" + pathForMerge + "\""

                            prevRoadSegId=listname[-1]

                        elif prevRoadSegId!=listname[-1] and segType!="Road": # Merge the previous one, export current one because it is POI
                            print("different roadsegId, point of interest")

                            if len(listforMerge)>5: #prevSegType=="Road" merge roads leading here. If previous one was also POI, don't do this
                                generateGPX(listforMerge,pathGDB,dist,base,d,Stage, prevSegType,count, subseq, listSegType, listSegID, listSegBase,listSegBaseEnd,BaseName,BaseNameEnd,  listSegEndLat, listSegEndLon)
                                if Stage <10:
                                    StageEnter="0{}".format(Stage)
                                else:
                                    StageEnter="{}".format(Stage)
                                listforMergePerDay+= ";" + "\"" + "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,StageEnter) + "\""
                                
                                Stage=Stage+1

                            listforMerge = ""
                            listforMerge += ";" + "\"" + pathForMerge + "\""
                            generateGPX(listforMerge,pathGDB,dist,base,d,Stage, segType,count, subseq, listSegType, listSegID, listSegBase,listSegBaseEnd,BaseName,BaseNameEnd,  listSegEndLat, listSegEndLon)
                            if Stage <10:
                                StageEnter="0{}".format(Stage)
                            else:
                                StageEnter="{}".format(Stage)
                            listforMergePerDay+= ";" + "\"" + "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,StageEnter) + "\""
                            
                            listforMerge = ""
                            Stage=Stage+1
                            prevRoadSegId=listname[-1]
                            listname=[]

                        arcpy.CopyFeatures_management(pathForMerge, "{}/last".format(pathGDB), "", "0", "0", "0")

                            
                        if seq == maxSeq and subseq==count:
                            segType="ReturnToBase"
                            generateGPX(listforMerge,pathGDB,dist,base,d,Stage, segType,count, subseq, listSegType, listSegID,listSegBase,listSegBaseEnd,BaseName,BaseNameEnd,  listSegEndLat, listSegEndLon)
                            if Stage <10:
                                StageEnter="0{}".format(Stage)
                            else:
                                StageEnter="{}".format(Stage)
                            listforMergePerDay+= ";" + "\"" + "OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,StageEnter) + "\""
                            listname=[]
                        prevSegType=segType
                        print('prevSegType',prevSegType)

                        if segType =="LCCkpt":
                            listOfCkpts.append(Stage-1)

                print('listOfCkpts',listOfCkpts)
                listOfCkpts = list(set(listOfCkpts))
                print('listOfCkpts',listOfCkpts)

                for stgCrsPre in listOfCkpts:
                    if stgCrsPre <10:
                        stgCrs="0{}".format(stgCrsPre)
                    else:
                        stgCrs="{}".format(stgCrsPre)
                    arcpy.AddGeometryAttributes_management("OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,stgCrs), "LINE_START_MID_END", "", "", "")
                    arcpy.MakeXYEventLayer_management("OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,stgCrs), "END_X", "END_Y",
                                                      "{}/end_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs),"", "")
                    arcpy.Buffer_analysis("{}/end_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs), "{}/endBufferedMax_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs),
                          "{} Meters".format(par_maxRangeFromCrossing), "FULL", "FLAT", "NONE", "", "PLANAR")
                    arcpy.Buffer_analysis("{}/end_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs), "{}/endBufferedMin_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs),
                          "{} Meters".format(par_minRangeFromCrossing), "FULL", "FLAT", "NONE", "", "PLANAR")
                    arcpy.Clip_analysis("OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,stgCrs),
                                        "{}/endBufferedMax_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs),
                                        "{}/RouteClipMax_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs), "")
                    arcpy.Erase_analysis("{}/RouteClipMax_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs), "{}/endBufferedMin_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs),
                                         "{}/RouteClip_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs), "")
                    arcpy.CreateRandomPoints_management(pathGDB, "Dist{}_Base{}_Day{}_Stage{}_RandomPoints".format(dist,BaseName,d,stgCrs),
                                        "{}/RouteClip_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB,dist,BaseName,d,stgCrs), "", "{}".format(par_maxPointsPerCrossing),
                                                        "{} Meters".format(par_minSpacingBetweenPoints), "POINT", "0")
                    arcpy.SpatialJoin_analysis("{}/Dist{}_Base{}_Day{}_Stage{}_RandomPoints".format(pathGDB,dist,BaseName,d,stgCrs), "{}/end".format(pathGDB),
                                               "{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDist".format(pathGDB,dist,BaseName,d,stgCrs),
                                   "JOIN_ONE_TO_ONE", "KEEP_ALL", "[ORIG_FID]", "CLOSEST_GEODESIC", "", "DistCros")

                    arcpy.Sort_management("{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDist".format(pathGDB,dist,BaseName,d,stgCrs),
                                          "{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDistSort".format(pathGDB,dist,BaseName,d,stgCrs), [["DistCros", "ASCENDING"]])
                    arcpy.gp.FeaturesToGPX("{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDistSort".format(pathGDB,dist,BaseName,d,stgCrs),
                        "OutputVRP/{}/Base{}{}/Day{}/Ckpts_Dist{}_B{}_D{}_St{}.gpx".format(dist,nameAdd2,base,d,dist,BaseName,d,stgCrs), True, True)
                    arcpy.CopyFeatures_management("{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDistSort".format(pathGDB,dist,BaseName,d,stgCrs),
                      "OutputVRP/{}/Base{}{}/Day{}/ckpts_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist,nameAdd2,base,d,dist,BaseName,d,stgCrs), "", "0", "0", "0")

                    print("FeaturesToCkpts D{} St{}".format(d,stgCrs))

                listforMergePerDay="\""+listforMergePerDay[1:1000000]+"\""
                print(listforMergePerDay)
                arcpy.Merge_management(listforMergePerDay, "OutputVRP/{}/Base{}{}/Day{}/RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist, BaseName,d))
                arcpy.AddField_management("OutputVRP/{}/Base{}{}/Day{}/RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist, BaseName,d), "Day", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                arcpy.CalculateField_management("OutputVRP/{}/Base{}{}/Day{}/RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist, BaseName,d), "Day", "{}".format(d), "PYTHON", "")
                arcpy.AddField_management("OutputVRP/{}/Base{}{}/Day{}/RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist, BaseName,d), "Base", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                arcpy.CalculateField_management("OutputVRP/{}/Base{}{}/Day{}/RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist, BaseName,d), "Base", "{}".format(BaseName), "PYTHON", "")
                arcpy.AddField_management("OutputVRP/{}/Base{}{}/Day{}/RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist, BaseName,d), "District", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                arcpy.CalculateField_management("OutputVRP/{}/Base{}{}/Day{}/RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist, BaseName,d), "District", "{}".format(dist), "PYTHON", "")
                listforMergePerDistrict += ";" + "\"" + "OutputVRP/{}/Base{}{}/Day{}/RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,nameAdd2,base,d,dist, BaseName,d) + "\""

                rowsForCSV=zip(listSegID,listSegType, listSegBase,  listSegBaseEnd, listSegEndLat, listSegEndLon)

                with open("OutputVRP/{}/Base{}{}/Day{}/schedule_Dist{}_Base{}_Day{}.csv".format(dist, nameAdd2,base,d,dist, BaseName,d), "wb") as f:
                    writer = csv.writer(f)
                    for row in rowsForCSV:
                        writer.writerow(row)
                        
                arcpy.Delete_management("{}/last".format(pathGDB))
                
    listforMergePerDistrict="\""+listforMergePerDistrict[1:1000000]+"\""
    arcpy.Merge_management(listforMergePerDistrict, "OutputVRP/{}/RoutesMerged_Dist{}{}.shp".format(dist,dist,nameAdd2))

### Set environment ###

# Allow the overwriting of the output files
arcpy.env.overwriteOutput = True # This command is CASE-SENSITIVE
arcpy.env.outputMFlag = "Disabled"
arcpy.env.outputZFlag = "Disabled"
arcpy.env.parallelProcessingFactor = "100%"
work_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(os.path.dirname(os.getcwd()))
arcpy.env.scratchWorkspace = '/Scratch'
Scratch='Output/createRouteDistrict/Scratch'
try:
    shutil.rmtree(Scratch)
except:
    pass
os.mkdir(Scratch)         

districts={
    "1": "ChindeLuabo",
    "2": "Mocubela",
    "3": "Maganja",
    "4": "Morrumbala",
    "5": "Lugela",
    "6": "Pebane",
    "7": "Memba",
    "8": "Erati",
    "9": "Monapo",
    "10": "Mossuril",
    "11": "Mogincual"
    }

par_timeAtMarket=90
par_timeAtCrossing=15
par_timeAtLC=16
par_timeAtFeira=60
par_timeAtHalfway=3

par_maxRangeFromCrossing=500
par_minRangeFromCrossing=100
par_maxPointsPerCrossing=10
par_minSpacingBetweenPoints=50
# Local variables:

#Inputs
distBoundaries = "Input/moz_adm_20190607_shp/moz_admbnda_adm2_ine_20190607.shp"
distBoundariesUpdated = "Output/createRouteDistrict/network/distBoundariesUpdated.shp"
startPoints_survey = "Input/startPoints_survey.shp"
LCCkpts = "Input/pointsForLCCkpts_4thRound.shp"

TandCRoads = "Input/TandCRoads.shp"
#TandCRoads = "/Imput/TandCRoads_exclChinde.shp" #the file is not available in the folder 

Breaks = "Input/testBreak.csv"
roads_in_nampula_and_zambezia = "Imput/roads_in_nampula_and_zambezia_exclMemba.shp"
allInfo_crossingLevel = "Input/allInfo_crossingLevel.shp"


#Outputs
roadsNetwork_shp = "Output/createRouteDistrict/network/roadsNetwork.shp"
roadsNetworkDissolve_shp = "Output/createRouteDistrict/network/roadsNetworkDissolve.shp"
roadsNetworkParts_shp = "Output/createRouteDistrict/network/roadsNetworkParts.shp"
#network = "/Output/createRouteDistrict/network/roadsNetwork_ND.nd"
network = "Output/createRouteDistrict/network/roadsNetwork.gdb/roadsNetwork_drive/roadsNetwork_drive_ND"
roadIntersectionsAndEndPoints="Output/createRouteDistrict/network/roadIntersectionsAndEndPoints.shp"
roadsNetworkPartsCentroids="Output/createRouteDistrict/network/roadsNetworkPartsCentroids.shp"
allInterceptPoints="Output/createRouteDistrict/network/allInterceptPoints.shp"

path="Temporary/WorkingWithRoutes4thRound.gdb"

print(districts)
print(sys.argv)

try:  # first solve transfer routes (manually defined for transferring from base location to base location, then solve routes from base location to remianing points of interest.
    dist=districts[sys.argv[-1]]
    print(dist)
    try:
        shutil.rmtree("OutputVRP/{}".format(dist))
    except:
        print("Folder  {} could not be deleted".format(dist))
        pass
    os.mkdir("OutputVRP/{}".format(dist))

    # prepare input for VRP
    #arcpy.Select_analysis(distBoundariesUpdated, "{}/distBoundary_{}".format(path, dist), "\"ADM2_PT\"= '{}'".format(dist))
    ##arcpy.SimplifyPolygon_cartography("{}/distBoundary_{}".format(path, dist), "{}/distBoundarySimple_{}".format(path, dist),
     #                                 "POINT_REMOVE", "100 Meters", "0 SquareMeters", "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS", "")
   # arcpy.Select_analysis("{}/startPoints_surveyProjected".format(path), "{}/startPoints_{}".format(path, dist), "\"district\" ='{}'".format(dist))
   # result = arcpy.GetCount_management("{}/startPoints_{}".format(path, dist))
  #  count = int(result.getOutput(0))

# Select features from distBoundariesUpdated based on ADM2_PT
    dist_boundaries_input = distBoundariesUpdated
    dist_boundaries_output = "{}/distBoundary_{}".format(path, dist)
    arcpy.Select_analysis(dist_boundaries_input, dist_boundaries_output, "\"ADM2_PT\"= '{}'".format(dist))

    # Simplify the geometry of distBoundary features
    dist_boundary_simple_output = "{}/distBoundarySimple_{}".format(path, dist)
    arcpy.cartography.SimplifyPolygon(dist_boundaries_output, dist_boundary_simple_output,
                                                  "POINT_REMOVE", "100 Meters", "0 SquareMeters",
                                                  "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS", "")

    # Select features from startPoints_surveyProjected based on district
    start_points_input = "{}/startPoints_surveyProjected".format(path)
    start_points_output = "{}/startPoints_{}".format(path, dist)
    arcpy.Select_analysis(start_points_input, start_points_output, "\"district\" ='{}'".format(dist))

    # Get the count of selected features in startPoints
    result = arcpy.GetCount_management(start_points_output)
    count = int(result.getOutput(0))

    print("Selected features count for district {}: {}".format(dist, count))




    print("This many start points: {}".format(count))

    arcpy.Intersect_analysis("{} #;{} #".format(TandCRoads,"{}/distBoundarySimple_{}".format(path, dist)), "{}/TandCRoads_{}".format(path, dist), "ALL", "", "INPUT")
    arcpy.CreateRandomPoints_management(path, "VisitPointsRoadsPreNear_{}".format(dist), "{}/TandCRoads_{}".format(path, dist), "0 0 250 250", "100000", "2000 Meters", "POINT", "0")
    arcpy.Near_analysis("{}/VisitPointsRoadsPreNear_{}".format(path, dist), "{}/mktsAndFeiras".format(path), "500 Meters", "", "NO_ANGLE", "GEODESIC")
    arcpy.Select_analysis("{}/VisitPointsRoadsPreNear_{}".format(path, dist), "{}/VisitPointsRoads_{}".format(path, dist), "\"NEAR_DIST\" <0") # select only those relatively far from points where routes get cut to avoid very short route parts.

    arcpy.FeatureVerticesToPoints_management("{}/TandCRoads_{}".format(path, dist), "{}/TandCRoads_VerticesPreNear{}".format(path, dist), "BOTH_ENDS")
    arcpy.Integrate_management("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "500 Meters")
    arcpy.DeleteIdentical_management("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "Shape", "50 Meters")
    arcpy.AddField_management("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "ServiceTime", "1", "PYTHON", "")
    arcpy.Near_analysis("{}/TandCRoads_VerticesPreNear{}".format(path, dist), allInterceptPoints, "500 Meters", "", "NO_ANGLE", "GEODESIC")
    arcpy.Select_analysis("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "{}/TandCRoads_VerticesPreNearII{}".format(path, dist), "\"NEAR_DIST\" <0") # select only those relatively far from points where routes get cut.
    arcpy.Near_analysis("{}/TandCRoads_VerticesPreNearII{}".format(path, dist), "{}/marketsCloseToRoads".format(path), "500 Meters", "", "NO_ANGLE", "GEODESIC")
    arcpy.Select_analysis("{}/TandCRoads_VerticesPreNearII{}".format(path, dist), "{}/TandCRoads_VerticesPreNearIII{}".format(path, dist), "\"NEAR_DIST\" <0") # select only those relatively far from points where routes get cut.
    arcpy.Near_analysis("{}/TandCRoads_VerticesPreNearIII{}".format(path, dist), "{}/VisitPointsRoads_{}".format(path, dist), "500 Meters", "", "NO_ANGLE", "GEODESIC")
    arcpy.Select_analysis("{}/TandCRoads_VerticesPreNearIII{}".format(path, dist), "{}/TandCRoads_Vertices{}".format(path, dist), "\"NEAR_DIST\" <0") # select only those relatively far from points where routes get cut.

    arcpy.AddField_management("{}/VisitPointsRoads_{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management("{}/VisitPointsRoads_{}".format(path, dist), "ServiceTime", "0", "PYTHON", "")

    arcpy.Intersect_analysis("'{}' #;{} #".format("{}/marketsCloseToRoads".format(path),"{}/distBoundarySimple_{}".format(path, dist)), "{}/markets_{}".format(path, dist), "ALL", "", "INPUT")
    arcpy.AddField_management("{}/markets_{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management("{}/markets_{}".format(path, dist), "ServiceTime", "{}".format(par_timeAtMarket), "PYTHON", "")

    arcpy.Intersect_analysis("'{}' #;{} #".format("{}/feirasCloseToRoads".format(path),"{}/distBoundarySimple_{}".format(path, dist)), "{}/feiras_{}".format(path, dist), "ALL", "", "INPUT")
    arcpy.AddField_management("{}/feiras_{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management("{}/feiras_{}".format(path, dist), "ServiceTime", "{}".format(par_timeAtFeira), "PYTHON", "")

    arcpy.Intersect_analysis("'{}' #;{} #".format(LCCkpts,"{}/distBoundarySimple_{}".format(path, dist)), "{}/lcckpts_{}".format(path, dist), "ALL", "", "INPUT")
    arcpy.AddField_management("{}/lcckpts_{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management("{}/lcckpts_{}".format(path, dist), "ServiceTime", "{}".format(par_timeAtLC), "PYTHON", "")

    arcpy.Intersect_analysis("'{}' #;{} #".format("{}\\roadHalfwayPoints".format(path),"{}\\distBoundarySimple_{}".format(path, dist)), "{}\\roadHalfwayPoints{}".format(path, dist), "ALL", "", "INPUT")
    #arcpy.Intersect_analysis("'{}' #;{} #".format(roadsNetworkPartsCentroids,"{}/distBoundarySimple_{}".format(path, dist)), "{}/roadHalfwayPoints{}".format(path, dist), "ALL", "", "INPUT")
    arcpy.AddField_management("{}/roadHalfwayPoints{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management("{}/roadHalfwayPoints{}".format(path, dist), "ServiceTime", "{}".format(par_timeAtHalfway), "PYTHON", "")
    arcpy.management.DeleteField("{}/roadHalfwayPoints{}".format(path, dist), "AVG_COND")
    arcpy.management.DeleteField("{}/roadHalfwayPoints{}".format(path, dist), "Merge_Info")

    arcpy.Intersect_analysis("'{}' #;{} #".format(allInfo_crossingLevel,"{}/distBoundarySimple_{}".format(path, dist)), "{}/crossings_{}".format(path, dist), "ALL", "", "INPUT")
    arcpy.Merge_management("{};{};{};{};{};{}".format("{}/lcckpts_{}".format(path, dist),"{}/feiras_{}".format(path, dist),"{}/TandCRoads_Vertices{}".format(path, dist),"{}/VisitPointsRoads_{}".format(path, dist),"{}/roadHalfwayPoints{}".format(path, dist),"{}/crossings_{}".format(path, dist)), "{}/orders_{}".format(path, dist))

    try:
        arcpy.DeleteField_management("{}/orders_{}".format(path, dist), "name")
    except:
        pass
        print("could not delete name field")

    Routes = "RouteImputs/transferRoutes{}.csv".format(dist)
    print("Routes", Routes)
    Orders = "{}/orders_{}".format(path, dist)
    nameAdd1 = "T"
    nameAdd2 = "Troco"
    print("Start Vehicle Routing Problem for Troco") # https://desktop.arcgis.com/en/arcmap/latest/extensions/network-analyst/vehicle-routing-problem.htm

    PerDist_function(Routes, Orders, nameAdd1, nameAdd2,count)

    arcpy.Merge_management("{};{};{};{};{};{}".format("{}/lcckpts_{}".format(path, dist),"{}/feiras_{}".format(path, dist),"{}/TandCRoads_Vertices{}".format(path, dist),"{}/VisitPointsRoads_{}".format(path, dist),"{}/roadHalfwayPoints{}".format(path, dist),"{}/crossings_{}".format(path, dist)), "{}/ordersSecondPre_{}".format(path, dist))

    try:
        arcpy.DeleteField_management("{}/ordersSecondPre_{}".format(path, dist), "Join_Count")
        arcpy.DeleteField_management("{}/ordersSecondPre_{}".format(path, dist), "name")
    except:
        pass
        print("could not delete Join_Count field")
    arcpy.SpatialJoin_analysis("{}/ordersSecondPre_{}".format(path, dist), "{}/OrdersServiced_{}".format(path,dist),
                       "{}/ordersSecondPre1_{}".format(path, dist),
                       "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "WITHIN_A_DISTANCE", "50 Meters", "")

    arcpy.Select_analysis("{}/ordersSecondPre1_{}".format(path, dist), "{}/ordersReturnBase_{}".format(path, dist), "\"Join_Count\" =0")
    try:
        arcpy.DeleteField_management("{}/ordersReturnBase_{}".format(path, dist), "name")
    except:
        pass
        print("could not delete name field")
    Orders="{}/ordersReturnBase_{}".format(path, dist)

    Routes = "/RouteInputs/baseReturn.csv"
    nameAdd1 = ""
    nameAdd2 = ""

    PerDist_function(Routes, Orders, nameAdd1, nameAdd2,count)

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