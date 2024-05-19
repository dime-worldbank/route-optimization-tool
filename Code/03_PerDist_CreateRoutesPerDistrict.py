import sys
import os
import shutil
import csv
import gpxpy
import gpxpy.gpx
import logging
import arcpy
from arcpy.sa import *
import arcpy.mp
import arcpy.na

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to check if a file exists
def check_file_exists(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

# Function to get unique values from a field in a table
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

# Function to add rank field to a table
def add_ranks(table, sort_fields, category_field, rank_field='RANK'):
    if not arcpy.ListFields(table, rank_field):
        arcpy.AddField_management(table, rank_field, "SHORT")
    sort_sql = ', '.join(['ORDER BY ' + category_field] + sort_fields)
    query_fields = [category_field, rank_field] + sort_fields
    with arcpy.da.UpdateCursor(table, query_fields, sql_clause=(None, sort_sql)) as cur:
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

# Function to generate GPX files
def generate_gpx(in_list_for_merge, in_path, in_dist, in_base, in_d, in_stage_pre, in_seg_type, in_count, in_subseq, in_list_seg_type,
                 in_list_seg_id, in_list_seg_base, in_list_seg_base_end, in_base_name, in_base_name_end, in_list_seg_end_lat, in_list_seg_end_lon):
    logger.info(f"Full Debug: Inp_listforMerge contents: {in_list_for_merge}")
    
    if in_stage_pre < 10:
        in_stage = f"0{in_stage_pre}"
    else:
        in_stage = f"{in_stage_pre}"

    list_for_merge = [item for item in in_list_for_merge if item]
    if isinstance(in_list_for_merge, list):
        in_list_for_merge = ';'.join(in_list_for_merge)

    if in_list_for_merge:
        list_for_merge = in_list_for_merge.split(';')
        list_for_merge = [path.strip('\"').strip() for path in list_for_merge if path.strip()]
        logger.info(f"Processed listforMerge: {list_for_merge}")
    else:
        list_for_merge = []
        logger.info("Inp_listforMerge is empty. No files to merge.")

    output_path = os.path.join(in_path, f"RoutesMerged_Dist{in_dist}_Base{in_base_name}_Day{in_d}_Stage{in_stage}")
    try:
        if list_for_merge:
            arcpy.management.Merge(list_for_merge, output_path)
            arcpy.CalculateField_management(f"{output_path}", "FIRST_Name", f"'Trk_Dist{in_dist}_B{in_base_name}_D{in_d}_St{in_stage}'", "PYTHON_9.3")
            arcpy.Dissolve_management(f"{output_path}", f"{output_path.replace('Merged', 'MergedDissolved')}", ["FIRST_Name"], "", "MULTI_PART", "DISSOLVE_LINES")
            arcpy.conversion.FeaturesToGPX(f"{output_path.replace('Merged', 'MergedDissolved')}", f"OutputVRP\\{in_dist}\\Base{in_base}{in_base_name}\\Day{in_d}\\Trk_Dist{in_dist}_B{in_base_name}_D{in_d}_St{in_stage}Pre.gpx", "FIRST_Name", "Shape_Length")
            logger.info(f"FeaturesToGPX D{in_d} St{in_stage}")
    except arcpy.ExecuteError:
        logger.error(arcpy.GetMessages())
        logger.error(f"Failed to execute Merge: {list_for_merge}")

    orig = f"OutputVRP\\{in_dist}\\Base{in_base}{in_base_name}\\Day{in_d}\\Trk_Dist{in_dist}_B{in_base_name}_D{in_d}_St{in_stage}Pre.gpx"
    txt = f'Temporary\\inter{in_dist}.txt'
    txt2 = f'Temporary\\inter2{in_dist}.txt'
    tgt = f"OutputVRP\\{in_dist}\\Base{in_base}{in_base_name}\\Day{in_d}\\Trk_Dist{in_dist}_B{in_base_name}_D{in_d}_St{in_stage}.gpx"
    
    if os.path.exists(orig):
        shutil.copyfile(orig, txt)
    else:
        logger.error(f"Error: Source file {orig} does not exist.")
    
    check_file_exists(orig)
    gpx_file = open(orig, 'rt')
    gpx_file_new = open(txt2, 'wt') 
    gpx = gpxpy.parse(gpx_file)
    
    last = ""
    for track in gpx.tracks: 
        for segment in track.segments: 
            for point in segment.points:
                last = f'<wpt lat="{point.latitude}" lon="{point.longitude}">\n<ele>1</ele>\n<name>Esta agora a 50 metros do final do etapa {in_stage}. Esta agora a 50 metros do final do etapa {in_stage}. Esta agora a 50 metros do final do etapa {in_stage}.</name>\n</wpt>'
    
    for line in open(txt, 'rt'):
        gpx_file_new.write(line.replace('<trk>', last+'\n<trk>'))
    
    gpx_file.close()
    gpx_file_new.close()
    shutil.copyfile(txt2, tgt)
    os.remove(orig)    
    os.remove(txt)    
    os.remove(txt2)    
    
    arcpy.AddField_management(f"{output_path.replace('Merged', 'MergedDissolved')}", "StgType", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(f"{output_path.replace('Merged', 'MergedDissolved')}", "StgType", f"'{in_seg_type}'", "PYTHON_9.3", "")
    arcpy.AddField_management(f"{output_path.replace('Merged', 'MergedDissolved')}", "Stage", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(f"{output_path.replace('Merged', 'MergedDissolved')}", "Stage", in_stage_pre, "PYTHON_9.3", "")
    arcpy.CopyFeatures_management(f"{output_path.replace('Merged', 'MergedDissolved')}", f"OutputVRP\\{in_dist}\\Base{in_base}{in_base_name}\\Day{in_d}\\final_Dist{in_dist}_Base{in_base_name}_Day{in_d}_Stage{in_stage}.shp", "", "0", "0", "0")
    arcpy.AddGeometryAttributes_management(f"OutputVRP\\{in_dist}\\Base{in_base}{in_base_name}\\Day{in_d}\\final_Dist{in_dist}_Base{in_base_name}_Day{in_d}_Stage{in_stage}.shp", "LINE_START_MID_END", "", "", "")
    
    cursor = arcpy.da.SearchCursor(f"OutputVRP\\{in_dist}\\Base{in_base}{in_base_name}\\Day{in_d}\\final_Dist{in_dist}_Base{in_base_name}_Day{in_d}_Stage{in_stage}.shp", "END_Y")
    end_lat = [row[0] for row in cursor]
    cursor = arcpy.da.SearchCursor(f"OutputVRP\\{in_dist}\\Base{in_base}{in_base_name}\\Day{in_d}\\final_Dist{in_dist}_Base{in_base_name}_Day{in_d}_Stage{in_stage}.shp", "END_X")
    end_lon = [row[0] for row in cursor]
    
    in_list_seg_type.append(in_seg_type if in_subseq == in_count else "Road")
    in_list_seg_id.append(f"Trk_Dist{in_dist}_B{in_base_name}_D{in_d}_St{in_stage}")
    in_list_seg_base.append(in_base_name)    
    in_list_seg_base_end.append(in_base_name_end)    
    in_list_seg_end_lon.append(end_lon[-1])    
    in_list_seg_end_lat.append(end_lat[-1])    
    
    return in_list_seg_type, in_list_seg_id, in_list_seg_base, in_list_seg_base_end, in_list_seg_end_lon, in_list_seg_end_lat

# Main function
def per_dist_function(routes, orders, name_add1, name_add2, count):
    global Breaks
    arcpy.TableToTable_conversion(routes, path, f"routes_{dist}")
    arcpy.TableSelect_analysis(f"{path}/routes_{dist}", f"{path}/routesSel_{dist}", f"\"la\" <={count}")
    arcpy.TableToTable_conversion(Breaks, path, f"breaks_{dist}")
    
    orders = arcpy.GetParameterValue("SolveVehicleRoutingProblem_na", 0)
    orders.load(orders)
    logger.info("Load orders")

    depots = arcpy.GetParameterValue("SolveVehicleRoutingProblem_na", 1)
    depots.load(f"{path}/startPoints_{dist}")
    logger.info("Load depots")

    routes = f"{path}/routesSel_{dist}"
    routes = arcpy.GetParameterValue("SolveVehicleRoutingProblem_na", 2)
    routes.load(routes)
    logger.info("Load routes")

    Breaks = f"{path}/breaks_{dist}"
    breaks = arcpy.GetParameterValue("SolveVehicleRoutingProblem_na", 3)
    breaks.load(Breaks)
    logger.info("Load breaks")
    
    try:
        output_dir = Scratch
        arcpy.env.workspace = os.path.join(output_dir, "Output.gdb")
        arcpy.env.overwriteOutput = True

        travel_modes = arcpy.na.GetTravelModes(network)
        logger.info("Available Travel Modes: %s", travel_modes)

        layer_name = "SurveyRoute"
        travel_mode = "New Travel Mode"
        time_units = "minutes"
        distance_units = "kilometers"
        default_date = "2019/10/01"
        time_zone_for_time_fields = None
        line_shape = "ALONG_NETWORK"
        time_window_factor = None
        excess_transit_factor = None
        generate_directions_on_solve = True
        spatial_clustering = "NO_CLUSTER"
        ignore_invalid_locations = True

        #output_layer_file = os.path.join(output_dir, f"{layer_name}.lyrx")

        # Create a unique subdirectory for each district within the Scratch folder
       # scratch_district_path = os.path.join(Scratch, f"{dist}")
        #if not os.path.exists(scratch_district_path):
         #   os.makedirs(scratch_district_path)

        #output_layer_file = os.path.join(scratch_district_path, f"{layer_name}_{dist}.lyrx")
        #scratch_gdb = os.path.join(scratch_district_path, f"scratch_{dist}.gdb")

        # Set arcpy environment workspace to the new scratch geodatabase path
        #arcpy.env.workspace = scratch_gdb


        result_object = arcpy.na.MakeVehicleRoutingProblemAnalysisLayer(
            network, layer_name, travel_mode, time_units, distance_units, default_date,
            time_zone_for_time_fields, line_shape, time_window_factor, excess_transit_factor,
            generate_directions_on_solve, spatial_clustering, ignore_invalid_locations)

        if result_object:
            logger.info("VRP Analysis Layer created successfully.")
            layer_object = result_object.getOutput(0)
            logger.info("Layer Name: %s", layer_object.name)
        else:
            logger.error("Failed to create VRP Analysis Layer. Check the result object for more details.")
            logger.error(result_object.getMessages())

        sub_layer_names = arcpy.na.GetNAClassNames(layer_object)
        orders_layer_name = sub_layer_names["Orders"]
        depots_layer_name = sub_layer_names["Depots"]
        routes_layer_name = sub_layer_names["Routes"]

        in_orders = Orders
        in_depots = depots
        in_routes = Routes

        # Correctly add locations to the VRP layer
        orders_layer_name = sub_layer_names["Orders"]
        depots_layer_name = sub_layer_names["Depots"]
        routes_layer_name = sub_layer_names["Routes"]

        candidate_fields = arcpy.ListFields(in_orders)
        order_field_mappings = arcpy.na.NAClassFieldMappings(layer_object, orders_layer_name, False, candidate_fields)
        arcpy.na.AddLocations(layer_object, orders_layer_name, in_orders, order_field_mappings, "")

        depot_field_mappings = arcpy.na.NAClassFieldMappings(layer_object, depots_layer_name)
        arcpy.na.AddLocations(layer_object, depots_layer_name, in_depots, depot_field_mappings, "")

        routes_field_mappings = arcpy.na.NAClassFieldMappings(layer_object, routes_layer_name)
        arcpy.na.AddLocations(layer_object, routes_layer_name, in_routes, routes_field_mappings, "")

        arcpy.na.Solve(layer_object)
        arcpy.management.SaveToLayerFile(layer_object, output_layer_file, "RELATIVE")
        logger.info("Script Completed and layer saved Successfully")

        for layer in arcpy.na.GetNAClassNames(layer_object):
            logger.info(f"Survey layer: {layer}")

        routes_layer = arcpy.na.GetNAClassNames(layer_object)["Routes"]
        arcpy.management.CopyFeatures(
            in_features="{}/{}".format(layer_object, routes_layer),
            out_feature_class="{}/vrp".format(pathGDB, d, Step)
        )

        vrp_layer = "C:/Users/idels/Documents/github/route-optimization-tool/Scratch/SurveyRoute.lyrx"
        vrp_lyr_obj = arcpy.mp.LayerFile(vrp_layer)
        vrp_orders_lyr = vrp_lyr_obj.listLayers('Orders')[0]
        vrp_depots_lyr = vrp_lyr_obj.listLayers('Depots')[0]
        vrp_routes_lyr = vrp_lyr_obj.listLayers('Routes')[0]
        arcpy.CopyFeatures_management(vrp_orders_lyr, "{}\\OrdersAll_{}".format(path, dist))
        arcpy.CopyFeatures_management(vrp_depots_lyr, "{}\\DepotsAll_{}".format(path, dist))
        arcpy.CopyFeatures_management(vrp_routes_lyr, "{}\\RoutesAll_{}".format(path, dist))
        arcpy.Select_analysis("{}\\OrdersAll_{}".format(path, dist), "{}\\OrdersServiced_{}".format(path, dist), "\"FromPrevTravelTime\" >  0")
        arcpy.Select_analysis("{}\\OrdersServiced_{}".format(path, dist), "{}\\OrdersServicedSelect_{}".format(path, dist), "\"Sequence\" >  0")
        RouteValues = unique_values("{}\\OrdersServicedSelect_{}".format(path, dist), 'RouteName')
        logger.info(f"Route: {RouteValues}")

        listforMergePerDistrict = []

        for base in range(1, count + 1):
            # Delete existing geodatabase if it exists
            try:
                arcpy.Delete_management("Temporary/WorkingWithRoutes{}_dist{}_base{}.gdb".format(name_add1, dist, base))
                logger.info("Deleted existing geodatabase")
            except:
                pass
            # Create a new file geodatabase
            arcpy.CreateFileGDB_management("Temporary", "WorkingWithRoutes{}_dist{}_base{}.gdb".format(name_add1, dist, base))
            logger.info("Created new geodatabase")

            pathGDB = "C:/Users/idels/Documents/github/route-optimization-tool/Temporary/WorkingWithRoutes{}_dist{}_base{}.gdb".format(name_add1, dist, base)
            logger.info(f"Base: {base}")

            # Create a new output folder (or ensure it exists)
            output_folder_path = "OutputVRP/{}/Base{}{}".format(dist, name_add2, base)
            os.makedirs(output_folder_path, exist_ok=True)
            logger.info("Created new output folder")

            try:
                shutil.rmtree("OutputVRP/{}/Base{}{}".format(dist, name_add2, base))
                logger.info("Deleted existing output folder")
            except:
                logger.warning(f"Folder Base{base} could not be deleted")

            output_folder_path = "OutputVRP/{}/Base{}{}".format(dist, name_add2, base)
            os.makedirs(output_folder_path, exist_ok=True)

            for d in range(1, count + 1):
                try:
                    os.mkdir(os.path.join(output_folder_path, "Day{}".format(d)))
                except:
                    logger.warning(f"Day{d} folder could not be created for Base{base}")

            for d in range(1, 27):
                logger.info(f"Try now day {d}")
                if "Route{}{}_{}".format(name_add1, base, d) in RouteValues:
                    arcpy.Select_analysis("{}/RoutesAll_{}".format(path, dist), "{}/{}_RouteToday".format(pathGDB, dist), " \"Name\" =  'Route{}{}_{}'".format(name_add1, base, d))
                    cursor = arcpy.da.SearchCursor("{}/{}_RouteToday".format(pathGDB, dist), "StartDepotName")
                    StartDepotName = [row[0] for row in cursor]
                    logger.info(f"StartDepotName: {StartDepotName}")
                    arcpy.Select_analysis("{}/DepotsAll_{}".format(path, dist), "{}/{}_startLoc_start".format(pathGDB, dist), " \"Name\" =  '{}'".format(StartDepotName[-1]))
                    arcpy.SpatialJoin_analysis("{}/{}_startLoc_start".format(pathGDB, dist), "{}/startPoints_{}".format(path, dist),
                                               "{}/{}_startLoc_withName".format(pathGDB, dist),
                                               "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "", "")
                    cursor = arcpy.da.SearchCursor("{}/{}_startLoc_withName".format(pathGDB, dist), "Base")
                    BaseName = [row[0] for row in cursor]
                    logger.info(f"BaseNameStart: {BaseName}")
                    BaseName = BaseName[-1] + name_add2
                    cursor = arcpy.da.SearchCursor("{}/{}_RouteToday".format(pathGDB, dist), "EndDepotName")
                    EndDepotName = [row[0] for row in cursor]
                    logger.info(f"EndDepotName: {EndDepotName}")
                    arcpy.Select_analysis("{}/DepotsAll_{}".format(path, dist), "{}/{}_startLoc_end".format(pathGDB, dist), " \"Name\" =  '{}'".format(EndDepotName[-1]))
                    arcpy.SpatialJoin_analysis("{}/{}_startLoc_end".format(pathGDB, dist), "{}/startPoints_{}".format(path, dist),
                                               "{}/{}_endLoc_withName".format(pathGDB, dist),
                                               "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "", "")
                    cursor = arcpy.da.SearchCursor("{}/{}_endLoc_withName".format(pathGDB, dist), "Base")
                    BaseNameEnd = [row[0] for row in cursor]
                    logger.info(f"BaseNameEnd: {BaseNameEnd}")
                    BaseNameEnd = BaseNameEnd[-1]
                    logger.info(f"Route from {BaseName} to {BaseNameEnd}")
                    d = d + 1
                    logger.info(f"Day: {d}")
                    listforMergePerDay = []
                    listSegID = []
                    listSegType = []
                    listSegBase = []
                    listSegBaseEnd = []
                    listSegEndLat = []
                    listSegEndLon = []
                    output_directory = "OutputVRP/{}/Base{}{}/Day{}".format(dist, name_add2, base, d)
                    if not os.path.exists(output_directory):
                        os.mkdir(output_directory)
                        logger.info(f"Directory created: {output_directory}")
                    else:
                        logger.info(f"Directory already exists: {output_directory}")

                    day_folder_path = os.path.join("OutputVRP", str(dist), "Base{}{}".format(name_add2, base), "Day{}".format(d))
                    try:
                        shutil.rmtree(day_folder_path)
                    except:
                        logger.warning(f"Folder Day{d} could not be deleted")
                        pass
                    os.makedirs(day_folder_path, exist_ok=True)

                    arcpy.Select_analysis("{}/OrdersServicedSelect_{}".format(path, dist), "{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB, dist, BaseName, d), " \"RouteName\" =  'Route{}{}_{}'".format(name_add1, base, d))
                    arcpy.CopyFeatures_management("{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB, dist, BaseName, d), "OutputVRP/{}/Base{}{}/Day{}/Orders_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d), "", "0", "0", "0")

                    add_ranks("{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB, dist, BaseName, d), ['Sequence'], 'RouteName', 'orderInDay')

                    cursor = arcpy.da.SearchCursor("{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB, dist, BaseName, d), "orderInDay")

                    listname = []
                    logger.info("Initializing/resetting listname")
                    listOfCkpts = []

                    for row in cursor:
                        listname.append(int(row[0]))

                    try:
                        maxSeq = max(listname)
                        logger.info(f'SequenceMax: {maxSeq}')
                    except ValueError:
                        logger.warning("listname is empty. Continuing with the next steps...")

                    arcpy.AddField_management("{}/{}_startLoc_start".format(pathGDB, dist), "orderInDay", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                    arcpy.CalculateField_management("{}/{}_startLoc_start".format(pathGDB, dist), "orderInDay", "0", "VB", "")
                    arcpy.AddField_management("{}/{}_startLoc_end".format(pathGDB, dist), "orderInDay", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                    arcpy.CalculateField_management("{}\\{}_startLoc_end".format(pathGDB, dist), "orderInDay", "{}".format(max(listname) + 1), "VB", "")

                    arcpy.Merge_management(["{}/{}_startLoc_start".format(pathGDB, dist), "{}/{}_startLoc_end".format(pathGDB, dist), "{}/OrdersServicedSelect_{}_Base{}_Day{}".format(pathGDB, dist, BaseName, d)],
                                           "{}/ordersMerged_{}_Base{}_Day{}".format(pathGDB, dist, BaseName, d))

                    listforMerge = []
                    Step = 0
                    Stage = 1
                    prevRoadSegId = ""
                    listname = []
                    logger.info(f"maxseq: {maxSeq}")
                    for seq in range(0, maxSeq + 1):
                        logger.info(f"seq: {seq}")
                        Step += 1
                        arcpy.Select_analysis("{}/ordersMerged_{}_Base{}_Day{}".format(pathGDB, dist, BaseName, d),
                                              "{}/start".format(pathGDB), " \"orderInDay\" =  {}".format(seq))
                        arcpy.Select_analysis("{}/ordersMerged_{}_Base{}_Day{}".format(pathGDB, dist, BaseName, d),
                                              "{}/end".format(pathGDB), " \"orderInDay\" =  {}".format(seq + 1))
                        cursor = arcpy.da.SearchCursor("{}/end".format(pathGDB), "ServiceTime")
                        for row in cursor:
                            if row[0] == par_timeAtHalfway:
                                segTypeWhole = "Halfway"
                            elif row[0] == par_timeAtFeira:
                                segTypeWhole = "Feira"
                            elif row[0] == par_timeAtCrossing:
                                segTypeWhole = "Crossing"
                            elif row[0] == par_timeAtLC:
                                segTypeWhole = "LCCkpt"
                            elif row[0] == 1:
                                segTypeWhole = "Vertice"
                            else:
                                segTypeWhole = "Road"

                        arcpy.env.workspace = pathGDB
                        arcpy.env.overwriteOutput = True

                        closest_fac_layer = arcpy.na.MakeClosestFacilityAnalysisLayer(
                            network_data_source=network,
                            travel_mode="New Travel Mode",
                            travel_direction="TO_FACILITIES",
                            cutoff="",
                            number_of_facilities_to_find=1,
                            time_zone="",
                            time_of_day_usage="",
                            line_shape="ALONG_NETWORK",
                            generate_directions_on_solve=True,
                            ignore_invalid_locations=True
                        ).getOutput(0)

                        arcpy.na.AddLocations(
                            in_network_analysis_layer=closest_fac_layer,
                            sub_layer="Incidents",
                            in_table="{}\\start".format(pathGDB),
                            search_tolerance="10 Meters",
                            search_criteria=[],
                            append="CLEAR",
                            snap_to_position_along_network="NO_SNAP",
                            exclude_restricted_elements="INCLUDE",
                            search_query=""
                        )

                        arcpy.na.AddLocations(
                            in_network_analysis_layer=closest_fac_layer,
                            sub_layer="Facilities",
                            in_table="{}\\end".format(pathGDB),
                            search_tolerance="10 Meters",
                            search_criteria=[],
                            append="CLEAR",
                            snap_to_position_along_network="NO_SNAP",
                            exclude_restricted_elements="INCLUDE",
                            search_query=""
                        )

                        arcpy.na.Solve(closest_fac_layer, "SKIP", "CONTINUE")

                        routes_layer = arcpy.na.GetNAClassNames(closest_fac_layer)["CFRoutes"]
                        arcpy.management.CopyFeatures(
                            in_features="{}/{}".format(closest_fac_layer, routes_layer),
                            out_feature_class="{}/RoutesPre_Day{}_Step{}".format(pathGDB, d, Step)
                        )

                        arcpy.CheckInExtension("Network")
                        arcpy.management.Project("{}/RoutesPre_Day{}_Step{}".format(pathGDB, d, Step), "{}/Routes_Day{}_Step{}".format(pathGDB, d, Step), "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "", "PROJCS['WGS_1984_UTM_Zone_36S',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',33.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")
                        arcpy.management.DeleteField("{}/Routes_Day{}_Step{}".format(pathGDB, d, Step), "Name")
                        arcpy.AddField_management("{}/Routes_Day{}_Step{}".format(pathGDB, d, Step), "Name", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                        arcpy.Delete_management("{}/Directions".format(pathGDB), "")
                        arcpy.Delete_management("{}/ClosestFacilities".format(pathGDB), "")
                        arcpy.SplitLineAtPoint_management("{}/Routes_Day{}_Step{}".format(pathGDB, d, Step), allInterceptPoints,
                                                        "{}/RoutesOrderSplitPre_Day{}_Step{}".format(pathGDB, d, Step), "500 Meters")
                        arcpy.Select_analysis("{}/RoutesOrderSplitPre_Day{}_Step{}".format(pathGDB, d, Step), "{}/RoutesOrderSplit_Day{}_Step{}".format(pathGDB, d, Step), "\"Shape_Length\" >0.00001")
                        arcpy.CreateRandomPoints_management(pathGDB, "RandomPointsAlongSeg_Day{}_Step{}".format(d, Step), "{}/Routes_Day{}_Step{}".format(pathGDB, d, Step), "0 0 250 250", "100000", "250 Meters", "POINT", "0")
                        arcpy.AddField_management("{}/RandomPointsAlongSeg_Day{}_Step{}".format(pathGDB, d, Step), "copy_fid", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                        arcpy.CalculateField_management("{}/RandomPointsAlongSeg_Day{}_Step{}".format(pathGDB, d, Step), "copy_fid", "!OID!", "PYTHON", "")
                        arcpy.SpatialJoin_analysis("{}/RoutesOrderSplit_Day{}_Step{}".format(pathGDB, d, Step), "{}/RandomPointsAlongSeg_Day{}_Step{}".format(pathGDB, d, Step),
                                                "{}/RoutesSplitPreSortPreDiss_Day{}_Step{}".format(pathGDB, d, Step), "JOIN_ONE_TO_MANY", "KEEP_ALL",
                                                "FacilityCurbApproach \"FacilityCurbApproach\" true true false 4 Long 0 0 ,First,#,C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Output/createRouteDistrict/network/{}/RoutesOrderSplit_Day{}_Step{},FacilityCurbApproach,-1,-1;Name \"Name\" true true false 255 Text 0 0 ,First,#,C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Output/createRouteDistrict/{}/RoutesOrderSplit_Day{}_Step{},Name,-1,-1;copy_fid \"copy_fid\" true true false 4 Long 0 0 ,First,#,C:/Users/Idelson Mindo/Desktop/CreateRoutesPerDistrict_Idelson/Output/createRouteDistrict/{}/RandomPointsAlongSeg_Day{}_Step{},copy_fid,-1,-1".format(pathGDB, d, Step, pathGDB, d, Step, pathGDB, d, Step),
                                                "WITHIN_A_DISTANCE", "1 Meters", "")
                        arcpy.Dissolve_management("{}/RoutesSplitPreSortPreDiss_Day{}_Step{}".format(pathGDB, d, Step), "{}/RoutesSplitPreSort_Day{}_Step{}".format(pathGDB, d, Step), "TARGET_FID", "copy_fid MEAN;Name FIRST;FacilityCurbApproach FIRST", "SINGLE_PART", "DISSOLVE_LINES")
                        arcpy.Sort_management("{}/RoutesSplitPreSort_Day{}_Step{}".format(pathGDB, d, Step),
                                            "{}/RoutesSplit_Day{}_Step{}".format(pathGDB, d, Step), [["MEAN_copy_fid", "ASCENDING"]])
                        arcpy.FeatureToPoint_management("{}/RoutesSplit_Day{}_Step{}".format(pathGDB, d, Step), "{}/RoutesSplitCentroid_Day{}_Step{}".format(pathGDB, d, Step), "INSIDE")
                        arcpy.SpatialJoin_analysis("{}/RoutesSplitCentroid_Day{}_Step{}".format(pathGDB, d, Step), roadsNetworkParts_shp,
                                                "{}/RoutesSplitCentroidJoined_Day{}_Step{}".format(pathGDB, d, Step), "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "50 Meters")
                        arcpy.SpatialJoin_analysis("{}/RoutesSplit_Day{}_Step{}".format(pathGDB, d, Step), "{}/RoutesSplitCentroidJoined_Day{}_Step{}".format(pathGDB, d, Step),
                                            "{}/RoutesSplitWithID_Day{}_Step{}".format(pathGDB, d, Step), "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST", "50 Meters")
                        result = arcpy.GetCount_management("{}/RoutesSplitWithID_Day{}_Step{}".format(pathGDB, d, Step))
                        count = int(result.getOutput(0))
                        arcpy.Delete_management("{}/RoutesSplitPreSort_Day{}_Step{}".format(pathGDB, d, Step), "")
                        arcpy.Delete_management("{}/RoutesSplitCentroidJoined_Day{}_Step{}".format(pathGDB, d, Step), "")
                        arcpy.Delete_management("{}/RoutesOrderSplitDissolveVertices_Day{}_Step{}".format(pathGDB, d, Step), "")
                        arcpy.Delete_management("{}/RoutesOrderSplitPre_Day{}_Step{}", "")

                        for subseq in range(1, count + 1):
                            if subseq == count:
                                segType = segTypeWhole
                            else:
                                segType = "Road"
                            logger.info(f"segType: {segType}")
                            arcpy.Select_analysis(
                                "{}/RoutesSplitWithID_Day{}_Step{}".format(pathGDB, d, Step),
                                "{}/RoutesSplit_Day{}_Step{}_sub{}".format(pathGDB, d, Step, subseq),
                                "\"OBJECTID\" =  {}".format(subseq)
                            )
                            logger.info(f"d: {d}, Step: {Step}, subseq: {subseq}")
                            pathForMerge = "{}/RoutesSplit_Day{}_Step{}_sub{}".format(pathGDB, d, Step, subseq)
                            logger.info(f"pathForMerge: {pathForMerge}")
                            cursor = arcpy.da.SearchCursor(pathForMerge, "RoadSegId")
                            for row in cursor:
                                logger.info(row[0])
                                listname.append(row)
                            curbPrev = ""
                            cursor = arcpy.da.SearchCursor(pathForMerge, "FIRST_FacilityCurbApproach")
                            for row in cursor:
                                Curb = row[0]
                                logger.info(f"Curb: {Curb}")
                            countInter = 0
                            try:
                                arcpy.Intersect_analysis(
                                    "{} #; {} #".format(pathForMerge, "{}/last".format(pathGDB)),
                                    "{}/intersect".format(pathGDB), "ALL", "", "INPUT"
                                )
                                intersects = arcpy.GetCount_management("{}/intersect".format(pathGDB))
                                countInter = int(intersects.getOutput(0))
                                logger.info(f"countInter: {countInter}")
                            except arcpy.ExecuteError:
                                logger.error(arcpy.GetMessages())
                                logger.warning("Couldn't compute intersection")
                                pass
                            if prevRoadSegId == "" and segType != "Crossing":
                                listforMerge.append("{}".format(pathForMerge))
                                logger.info("prevRoadSegId empty")
                                prevRoadSegId = listname[-1]
                                segTypePrev = segType
                                curbPrev = Curb
                            elif prevRoadSegId == "" and segType == "Crossing":
                                logger.info("cat b")
                                listforMerge.append("{}".format(pathForMerge))
                                generate_gpx(listforMerge, pathGDB, dist, base, d, Stage, segType, count, subseq, listSegType, listSegID,
                                             listSegBase, listSegBaseEnd, BaseName, BaseNameEnd, listSegEndLat, listSegEndLon)
                                StageEnter = "0{}".format(Stage) if Stage < 10 else "{}".format(Stage)
                                listforMergePerDay.append("OutputVRP\\{}\\Base{}{}\\Day{}\\final_Dist{}_Base{}_Day{}_Stage{}.shp".format(
                                    dist, name_add2, base, d, dist, BaseName, d, StageEnter))
                                Stage = Stage + 1
                                listforMerge = []

                            elif prevRoadSegId == listname[-1] and segType == "Road" and countInter == 0 or (
                                    prevRoadSegId == listname[-1] and segType == "Road" and countInter > 0 and len(listforMerge) == 0):
                                logger.info("identical roadsegId, along Road")
                                listforMerge.append("{}".format(pathForMerge))
                                prevRoadSegId = listname[-1]

                            elif countInter > 0 and len(listforMerge) > 0:
                                logger.info("identical roadsegId, along Road, turning")
                                generate_gpx(listforMerge, pathGDB, dist, base, d, Stage, prevSegType, count, subseq, listSegType,
                                             listSegID, listSegBase, listSegBaseEnd, BaseName, BaseNameEnd, listSegEndLat, listSegEndLon)
                                StageEnter = "0{}".format(Stage) if Stage < 10 else "{}".format(Stage)
                                listforMergePerDay.append("OutputVRP\\{}\\Base{}{}\\Day{}\\final_Dist{}_Base{}_Day{}_Stage{}.shp".format(
                                    dist, name_add2, base, d, dist, BaseName, d, StageEnter))
                                listforMerge = []
                                Stage = Stage + 1
                                prevRoadSegId = listname[-1]
                                listname = []
                                listforMerge.append("{}".format(pathForMerge))
                            elif prevRoadSegId == listname[-1] and segType != "Road":
                                logger.info("identical roadsegId, point of Interest")
                                if pathForMerge:
                                    listforMerge.append(pathForMerge)
                                    generate_gpx(listforMerge, pathGDB, dist, base, d, Stage, segType, count, subseq, listSegType, listSegID,
                                                 listSegBase, listSegBaseEnd, BaseName, BaseNameEnd, listSegEndLat, listSegEndLon)
                                    StageEnter = "0{}".format(Stage) if Stage < 10 else "{}".format(Stage)
                                    listforMergePerDay.append("OutputVRP\\{}\\Base{}{}\\Day{}\\final_Dist{}_Base{}_Day{}_Stage{}.shp".format(
                                        dist, name_add2, base, d, dist, BaseName, d, StageEnter))
                                    Stage = Stage + 1
                                    prevRoadSegId = ""
                                else:
                                    logger.warning("Warning: Empty or invalid pathForMerge. Skipping Merge operation.")
                            elif prevRoadSegId != listname[-1] and prevSegType == "Road" and segType == "Road":
                                logger.info("different roadsegId, not first point")
                                generate_gpx(listforMerge, pathGDB, dist, base, d, Stage, segType, count, subseq, listSegType, listSegID,
                                             listSegBase, listSegBaseEnd, BaseName, BaseNameEnd, listSegEndLat, listSegEndLon)
                                StageEnter = "0{}".format(Stage) if Stage < 10 else "{}".format(Stage)
                                listforMergePerDay.append("OutputVRP\\{}\\Base{}{}\\Day{}\\final_Dist{}_Base{}_Day{}_Stage{}.shp".format(
                                    dist, name_add2, base, d, dist, BaseName, d, StageEnter))
                                Stage = Stage + 1
                                prevRoadSegId = listname[-1]
                                listname = []
                                listforMerge.append("{}".format(pathForMerge))

                            elif prevRoadSegId != listname[-1] and prevSegType != "Road" and segType == "Road":
                                logger.info("different roadsegId, first point of new segment")
                                listforMerge.append("{}".format(pathForMerge))
                                prevRoadSegId = listname[-1]

                            elif prevRoadSegId != listname[-1] and segType != "Road":
                                logger.info("different roadsegId, point of interest")
                                if len(listforMerge) > 5:
                                    generate_gpx(listforMerge, pathGDB, dist, base, d, Stage, prevSegType, count, subseq, listSegType, listSegID,
                                                 listSegBase, listSegBaseEnd, BaseName, BaseNameEnd, listSegEndLat, listSegEndLon)
                                    StageEnter = "0{}".format(Stage) if Stage < 10 else "{}".format(Stage)
                                    listforMergePerDay.append("OutputVRP\\{}\\Base{}{}\\Day{}\\final_Dist{}_Base{}_Day{}_Stage{}.shp".format(
                                        dist, name_add2, base, d, dist, BaseName, d, StageEnter))
                                    Stage = Stage + 1
                                listforMerge.append("{}".format(pathForMerge))
                                generate_gpx(listforMerge, pathGDB, dist, base, d, Stage, segType, count, subseq, listSegType, listSegID,
                                             listSegBase, listSegBaseEnd, BaseName, BaseNameEnd, listSegEndLat, listSegEndLon)
                                StageEnter = "0{}".format(Stage) if Stage < 10 else "{}".format(Stage)
                                listforMergePerDay.append("OutputVRP\\{}\\Base{}{}\\Day{}\\final_Dist{}_Base{}_Day{}_Stage{}.shp".format(
                                    dist, name_add2, base, d, dist, BaseName, d, StageEnter))
                                Stage = Stage + 1
                                prevRoadSegId = listname[-1]
                                listname = []
                            arcpy.CopyFeatures_management(pathForMerge, "{}\\last".format(pathGDB), "", "0", "0", "0")

                            if seq == maxSeq and subseq == count:
                                segType = "ReturnToBase"
                                generate_gpx(listforMerge, pathGDB, dist, base, d, Stage, segType, count, subseq, listSegType, listSegID,
                                             listSegBase, listSegBaseEnd, BaseName, BaseNameEnd, listSegEndLat, listSegEndLon)
                                StageEnter = "0{}".format(Stage) if Stage < 10 else "{}".format(Stage)
                                listforMergePerDay.append("OutputVRP\\{}\\Base{}{}\\Day{}\\final_Dist{}_Base{}_Day{}_Stage{}.shp".format(
                                    dist, name_add2, base, d, dist, BaseName, d, StageEnter))
                                listname = []
                            prevSegType = segType
                            logger.info(f'prevSegType: {prevSegType}')

                            if segType == "LCCkpt":
                                listOfCkpts.append(Stage - 1)

                    logger.info(f'listOfCkpts: {listOfCkpts}')
                    listOfCkpts = list(set(listOfCkpts))
                    logger.info(f'listOfCkpts: {listOfCkpts}')

                    for stgCrsPre in listOfCkpts:
                        stgCrs = "0{}".format(stgCrsPre) if stgCrsPre < 10 else "{}".format(stgCrsPre)
                        try:
                            arcpy.AddGeometryAttributes_management("C:/Users/idels/Documents/github/route-optimization-tool/OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist, name_add2, base, d, dist, BaseName, d, stgCrs), "LINE_START_MID_END", "", "", "")
                        except Exception as e:
                            logger.error(f"Error in AddGeometryAttributes: {e}")

                        try:
                            arcpy.MakeXYEventLayer_management("OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist, name_add2, base, d, dist, BaseName, d, stgCrs), "END_X", "END_Y", "{}/end_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs), "", "")
                        except Exception as e:
                            logger.error(f"Error in MakeXYEventLayer: {e}")

                        try:
                            arcpy.Buffer_analysis("{}/end_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs), "{}/endBufferedMax_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs),
                                                  "{} Meters".format(par_maxRangeFromCrossing), "FULL", "FLAT", "NONE", "", "PLANAR")
                        except Exception as e:
                            logger.error(f"Error in Buffer_analysis (Max): {e}")

                        try:
                            arcpy.Buffer_analysis("{}/end_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs), "{}/endBufferedMin_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs),
                                                  "{} Meters".format(par_minRangeFromCrossing), "FULL", "FLAT", "NONE", "", "PLANAR")
                        except Exception as e:
                            logger.error(f"Error in Buffer_analysis (Min): {e}")

                        try:
                            arcpy.Clip_analysis("OutputVRP/{}/Base{}{}/Day{}/final_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist, name_add2, base, d, dist, BaseName, d, stgCrs),
                                                "{}/endBufferedMax_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs),
                                                "{}/RouteClipMax_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs), "")
                        except Exception as e:
                            logger.error(f"Error in Clip_analysis: {e}")

                        try:
                            arcpy.Erase_analysis("{}/RouteClipMax_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs), "{}/endBufferedMin_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs),
                                                 "{}/RouteClip_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs), "")
                        except Exception as e:
                            logger.error(f"Error in Erase_analysis: {e}")

                        try:
                            arcpy.CreateRandomPoints_management(pathGDB, "Dist{}_Base{}_Day{}_Stage{}_RandomPoints".format(dist, BaseName, d, stgCrs),
                                                                "{}/RouteClip_Dist{}_Base{}_Day{}_Stage{}".format(pathGDB, dist, BaseName, d, stgCrs), "", "{}".format(par_maxPointsPerCrossing),
                                                                "{} Meters".format(par_minSpacingBetweenPoints), "POINT", "0")
                        except Exception as e:
                            logger.error(f"Error in CreateRandomPoints: {e}")

                        try:
                            arcpy.SpatialJoin_analysis("{}/Dist{}_Base{}_Day{}_Stage{}_RandomPoints".format(pathGDB, dist, BaseName, d, stgCrs), "{}/end".format(pathGDB),
                                                       "{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDist".format(pathGDB, dist, BaseName, d, stgCrs),
                                                       "JOIN_ONE_TO_ONE", "KEEP_ALL", "[ORIG_FID]", "CLOSEST_GEODESIC", "", "DistCros")
                        except Exception as e:
                            logger.error(f"Error in SpatialJoin_analysis: {e}")

                        try:
                            arcpy.Sort_management("{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDist".format(pathGDB, dist, BaseName, d, stgCrs),
                                                  "{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDistSort".format(pathGDB, dist, BaseName, d, stgCrs), [["DistCros", "ASCENDING"]])
                        except Exception as e:
                            logger.error(f"Error in Sort_management: {e}")

                        try:
                            arcpy.conversion.FeaturesToGPX("{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDistSort".format(pathGDB, dist, BaseName, d, stgCrs),
                                                           "C:/Users/idels/Documents/github/route-optimization-tool/OutputVRP/{}/Base{}{}/Day{}/Ckpts_Dist{}_B{}_D{}_St{}.gpx".format(dist, name_add2, base, d, dist, BaseName, d, stgCrs), None, None, None, None)
                        except Exception as e:
                            logger.error(f"Error in FeaturesToGPX: {e}")

                        try:
                            arcpy.CopyFeatures_management("{}/Dist{}_Base{}_Day{}_Stage{}_RandomPointsWithDistSort".format(pathGDB, dist, BaseName, d, stgCrs),
                                                          "OutputVRP/{}/Base{}{}/Day{}/ckpts_Dist{}_Base{}_Day{}_Stage{}.shp".format(dist, name_add2, base, d, dist, BaseName, d, stgCrs), "", "0", "0", "0")
                        except Exception as e:
                            logger.error(f"Error in CopyFeatures: {e}")

                        logger.info(f"FeaturesToCkpts D{d} St{stgCrs}")

                    logger.info(f"imput to merge: {listforMergePerDay}")
                    arcpy.management.Merge(listforMergePerDay, "OutputVRP\\{}\\Base{}{}\\Day{}\\RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d))
                    arcpy.AddField_management("OutputVRP\\{}\\Base{}{}\\Day{}\\RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d), "Day", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                    arcpy.CalculateField_management("OutputVRP\\{}\\Base{}{}\\Day{}\\RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d), "Day", "{}".format(d), "VB", "")
                    arcpy.AddField_management("OutputVRP\\{}\\Base{}{}\\Day{}\\RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d), "Base", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                    arcpy.CalculateField_management("OutputVRP\\{}\\Base{}{}\\Day{}\\RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d), "Base", "{}".format(BaseName), "VB", "")
                    arcpy.AddField_management("OutputVRP\\{}\\Base{}{}\\Day{}\\RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d), "District", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                    arcpy.CalculateField_management("OutputVRP\\{}\\Base{}{}\\Day{}\\RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d), "District", "{}".format(dist), "VB", "")

                    listforMergePerDistrict.append("OutputVRP\\{}\\Base{}{}\\Day{}\\RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, name_add2, base, d, dist, BaseName, d))

                    rowsForCSV = zip(listSegID, listSegType, listSegBase, listSegBaseEnd, listSegEndLat, listSegEndLon)
                    with open("OutputVRP\\{}\\Base{}{}\\Day{}\\schedule_Dist{}_Base{}_Day{}.csv".format(dist, name_add2, base, d, dist, BaseName, d), "w", newline='') as f:
                        writer = csv.writer(f)
                        for row in rowsForCSV:
                            writer.writerow(row)
                    arcpy.Delete_management("{}\\last".format(pathGDB))

        arcpy.Merge_management(listforMergePerDistrict, "OutputVRP\\{}\\RoutesMerged_Dist{}{}.shp".format(dist, dist, name_add2))

    except Exception as e:
        tb = sys.exc_info()[2]
        logger.error(f"An error occurred on line {tb.tb_lineno}: {str(e)}")

if __name__ == '__main__':
    arcpy.CheckOutExtension("Network")
    arcpy.CheckOutExtension("Spatial")

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
        "11": "Mogincual",
        "98": "aroundNampula"
    }
    par_timeAtMarket = 90
    par_timeAtCrossing = 15
    par_timeAtLC = 16
    par_timeAtFeira = 60
    par_timeAtHalfway = 3
    par_maxRangeFromCrossing = 500
    par_minRangeFromCrossing = 100
    par_maxPointsPerCrossing = 10
    par_minSpacingBetweenPoints = 50

    distBoundaries = "Input/moz_adm_20190607_shp/moz_admbnda_adm2_ine_20190607.shp"
    distBoundariesUpdated = "Output/createRouteDistrict/network/distBoundariesUpdated.shp"
    startPoints_survey = "Input/startPoints_survey.shp"
    LCCkpts = "Input/pointsForLCCkpts_4thRound.shp"
    TandCRoads = "Input/TandCRoads.shp"
    Breaks = "Input/testBreak.csv"
    roads_in_nampula_and_zambezia = "Imput/roads_in_nampula_and_zambezia_exclMemba.shp"
    allInfo_crossingLevel = "Input/allInfo_crossingLevel.shp"
    roadsNetwork_shp = "Output/createRouteDistrict/network/roadsNetwork.shp"
    roadsNetworkDissolve_shp = "Output/createRouteDistrict/network/roadsNetworkDissolve.shp"
    roadsNetworkParts_shp = "Output/createRouteDistrict/network/roadsNetworkParts.shp"
    network = "C:/Users/idels/Documents/github/route-optimization-tool/Output/createRouteDistrict/network/roadsDatasetNet.gdb/roads/roadNet"
    roadIntersectionsAndEndPoints = "Output/createRouteDistrict/network/roadIntersectionsAndEndPoints.shp"
    roadsNetworkPartsCentroids = "Output/createRouteDistrict/network/roadsNetworkPartsCentroids.shp"
    allInterceptPoints = "Output/createRouteDistrict/network/allInterceptPoints.shp"

    path = "Temporary/WorkingWithRoutes4thRound.gdb"

    arcpy.env.overwriteOutput = True
    arcpy.env.outputMFlag = "Disabled"
    arcpy.env.outputZFlag = "Disabled"
    arcpy.env.parallelProcessingFactor = "100%"
    work_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(os.path.dirname(os.getcwd()))
    arcpy.env.scratchWorkspace = 'Scratch'
    
    Scratch = 'Scratch'
    #try:
     #   shutil.rmtree(Scratch)
    #except:
    #    pass
    #os.mkdir(Scratch)
    try:
            shutil.rmtree(Scratch)
    except:
            pass
    os.mkdir(Scratch)

    for dist_key, dist_name in districts.items():
        dist = dist_name
        try:
            scratch_district_path = os.path.join(Scratch, f"{dist_name}")
            if not os.path.exists(scratch_district_path):
                os.makedirs(scratch_district_path)

            output_layer_file = os.path.join(scratch_district_path, f"SurveyRoute_{dist_name}.lyrx")
            scratch_gdb = os.path.join(scratch_district_path, f"scratch_{dist_name}.gdb")
            arcpy.env.workspace = scratch_gdb

            # Ensure the scratch geodatabase exists
            if not arcpy.Exists(scratch_gdb):
                arcpy.CreateFileGDB_management(scratch_district_path, f"scratch_{dist_name}.gdb")

            arcpy.env.workspace = scratch_gdb

            logger.info(dist_name)
            try:
                shutil.rmtree(f"OutputVRP\\{dist_name}")
            except:
                logger.warning(f"Folder {dist_name} could not be deleted")
                pass
            os.mkdir(f"OutputVRP\\{dist_name}")
           

            arcpy.Select_analysis(distBoundariesUpdated, "{}/distBoundary_{}".format(path, dist), "\"ADM2_PT\"= '{}'".format(dist))
            arcpy.SimplifyPolygon_cartography("{}/distBoundary_{}".format(path, dist), "{}/distBoundarySimple_{}".format(path, dist),
                                            "POINT_REMOVE", "100 Meters", "0 SquareMeters", "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS", "")
            arcpy.Select_analysis("{}/startPoints_surveyProjected".format(path), "{}/startPoints_{}".format(path, dist), "\"district\" ='{}'".format(dist))
            result = arcpy.GetCount_management("{}/startPoints_{}".format(path, dist))
            count = int(result.getOutput(0))

            dist_boundaries_input = distBoundariesUpdated
            dist_boundaries_output = "{}/distBoundary_{}".format(path, dist)
            arcpy.Select_analysis(dist_boundaries_input, dist_boundaries_output, "\"ADM2_PT\"= '{}'".format(dist))

            dist_boundary_simple_output = "{}/distBoundarySimple_{}".format(path, dist)
            arcpy.cartography.SimplifyPolygon(dist_boundaries_output, dist_boundary_simple_output,
                                            "POINT_REMOVE", "100 Meters", "0 SquareMeters",
                                            "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS", "")

            start_points_input = "{}/startPoints_surveyProjected".format(path)
            start_points_output = "{}/startPoints_{}".format(path, dist)
            arcpy.Select_analysis(start_points_input, start_points_output, "\"district\" ='{}'".format(dist))
            result = arcpy.GetCount_management(start_points_output)
            count = int(result.getOutput(0))
            logger.info(f"Selected features count for district {dist}: {count}")
            logger.info(f"This many start points: {count}")
            arcpy.Intersect_analysis("{} #;{} #".format(TandCRoads, "{}/distBoundarySimple_{}".format(path, dist)), "{}/TandCRoads_{}".format(path, dist), "ALL", "", "INPUT")
            arcpy.CreateRandomPoints_management(path, "VisitPointsRoadsPreNear_{}".format(dist), "{}/TandCRoads_{}".format(path, dist), "0 0 250 250", "100000", "2000 Meters", "POINT", "0")
            arcpy.Near_analysis("{}/VisitPointsRoadsPreNear_{}".format(path, dist), "{}/mktsAndFeiras".format(path), "500 Meters", "", "NO_ANGLE", "GEODESIC")
            arcpy.Select_analysis("{}/VisitPointsRoadsPreNear_{}".format(path, dist), "{}/VisitPointsRoads_{}".format(path, dist), "\"NEAR_DIST\" <0")
            arcpy.FeatureVerticesToPoints_management("{}/TandCRoads_{}".format(path, dist), "{}/TandCRoads_VerticesPreNear{}".format(path, dist), "BOTH_ENDS")
            arcpy.Integrate_management("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "500 Meters")
            arcpy.DeleteIdentical_management("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "Shape", "50 Meters")
            arcpy.AddField_management("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.CalculateField_management("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "ServiceTime", "1", "PYTHON", "")
            arcpy.Near_analysis("{}/TandCRoads_VerticesPreNear{}".format(path, dist), allInterceptPoints, "500 Meters", "", "NO_ANGLE", "GEODESIC")
            arcpy.Select_analysis("{}/TandCRoads_VerticesPreNear{}".format(path, dist), "{}/TandCRoads_VerticesPreNearII{}".format(path, dist), "\"NEAR_DIST\" <0")
            arcpy.Near_analysis("{}/TandCRoads_VerticesPreNearII{}".format(path, dist), "{}/marketsCloseToRoads".format(path), "500 Meters", "", "NO_ANGLE", "GEODESIC")
            arcpy.Select_analysis("{}/TandCRoads_VerticesPreNearII{}".format(path, dist), "{}/TandCRoads_VerticesPreNearIII{}".format(path, dist), "\"NEAR_DIST\" <0")
            arcpy.Near_analysis("{}/TandCRoads_VerticesPreNearIII{}".format(path, dist), "{}/VisitPointsRoads_{}".format(path, dist), "500 Meters", "", "NO_ANGLE", "GEODESIC")
            arcpy.Select_analysis("{}/TandCRoads_VerticesPreNearIII{}".format(path, dist), "{}/TandCRoads_Vertices{}".format(path, dist), "\"NEAR_DIST\" <0")
            arcpy.AddField_management("{}/VisitPointsRoads_{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.CalculateField_management("{}/VisitPointsRoads_{}".format(path, dist), "ServiceTime", "0", "PYTHON", "")
            arcpy.Intersect_analysis("'{}' #;{} #".format("{}/marketsCloseToRoads".format(path), "{}/distBoundarySimple_{}".format(path, dist)), "{}/markets_{}".format(path, dist), "ALL", "", "INPUT")
            arcpy.AddField_management("{}/markets_{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.CalculateField_management("{}/markets_{}".format(path, dist), "ServiceTime", "{}".format(par_timeAtMarket), "PYTHON", "")
            arcpy.Intersect_analysis("'{}' #;{} #".format("{}/feirasCloseToRoads".format(path), "{}/distBoundarySimple_{}".format(path, dist)), "{}/feiras_{}".format(path, dist), "ALL", "", "INPUT")
            arcpy.AddField_management("{}/feiras_{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.CalculateField_management("{}/feiras_{}".format(path, dist), "ServiceTime", "{}".format(par_timeAtFeira), "PYTHON", "")
            arcpy.Intersect_analysis("'{}' #;{} #".format(LCCkpts, "{}/distBoundarySimple_{}".format(path, dist)), "{}/lcckpts_{}".format(path, dist), "ALL", "", "INPUT")
            arcpy.AddField_management("{}/lcckpts_{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.CalculateField_management("{}/lcckpts_{}".format(path, dist), "ServiceTime", "{}".format(par_timeAtLC), "PYTHON", "")
            arcpy.Intersect_analysis("'{}' #;{} #".format("{}\\roadHalfwayPoints".format(path), "{}\\distBoundarySimple_{}".format(path, dist)), "{}\\roadHalfwayPoints{}".format(path, dist), "ALL", "", "INPUT")
            arcpy.AddField_management("{}/roadHalfwayPoints{}".format(path, dist), "ServiceTime", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.CalculateField_management("{}/roadHalfwayPoints{}".format(path, dist), "ServiceTime", "{}".format(par_timeAtHalfway), "PYTHON", "")
            arcpy.management.DeleteField("{}/roadHalfwayPoints{}".format(path, dist), "AVG_COND")
            arcpy.management.DeleteField("{}/roadHalfwayPoints{}".format(path, dist), "Merge_Info")
            arcpy.Intersect_analysis("'{}' #;{} #".format(allInfo_crossingLevel, "{}/distBoundarySimple_{}".format(path, dist)), "{}/crossings_{}".format(path, dist), "ALL", "", "INPUT")

            arcpy.Merge_management("{};{};{};{};{};{}".format("{}/lcckpts_{}".format(path, dist), "{}/feiras_{}".format(path, dist), "{}/TandCRoads_Vertices{}".format(path, dist), "{}/VisitPointsRoads_{}".format(path, dist), "{}/roadHalfwayPoints{}".format(path, dist), "{}/crossings_{}".format(path, dist)), "{}/orders_{}".format(path, dist))
            try:
                arcpy.management.DeleteField("{}/orders_{}".format(path, dist), "name")
            except:
                pass
                logger.warning("could not delete name field")
            Routes = "RouteImputs/transferRoutes{}.csv".format(dist)
            logger.info(f"Routes: {Routes}")
            Orders = "{}/orders_{}".format(path, dist)

            nameAdd1 = "T"
            nameAdd2 = "Troco"
            logger.info("Start Vehicle Routing Problem for Troco")

            per_dist_function(Routes, Orders, nameAdd1, nameAdd2, count)

            datasets = [
                "{}/lcckpts_{}".format(path, dist),
                "{}/feiras_{}".format(path, dist),
                "{}/TandCRoads_Vertices{}".format(path, dist),
                "{}/VisitPointsRoads_{}".format(path, dist),
                "{}/roadHalfwayPoints{}".format(path, dist),
                "{}/crossings_{}".format(path, dist)
            ]

            for dataset in datasets:
                if arcpy.Exists(dataset):
                    logger.info(f"Dataset exists: {dataset}")
                else:
                    logger.warning(f"Dataset does not exist: {dataset}")

            input_datasets = ";".join(datasets)
            output_dataset = "{}/ordersSecondPre_{}".format(path, dist)
            arcpy.Merge_management(input_datasets, output_dataset)

            try:
                arcpy.management.DeleteField("{}/ordersSecondPre_{}".format(path, dist), "Join_Count")
                arcpy.management.DeleteField("{}/ordersSecondPre_{}".format(path, dist), "name")
            except:
                pass
                logger.warning("could not delete Join_Count field")
            arcpy.SpatialJoin_analysis("{}/ordersSecondPre_{}".format(path, dist), "{}/OrdersServiced_{}".format(path, dist),
                                    "{}/ordersSecondPre1_{}".format(path, dist),
                                    "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "WITHIN_A_DISTANCE", "50 Meters", "")
            arcpy.Select_analysis("{}/ordersSecondPre1_{}".format(path, dist), "{}/ordersReturnBase_{}".format(path, dist), "\"Join_Count\" =0")
            try:
                arcpy.management.DeleteField("{}/ordersReturnBase_{}".format(path, dist), "name")
            except:
                pass
                logger.warning("could not delete name field")
            Orders = "{}/ordersReturnBase_{}".format(path, dist)
            Routes = "RouteInputs/baseReturn.csv"
            nameAdd1 = ""
            nameAdd2 = ""

            per_dist_function(Routes, Orders, nameAdd1, nameAdd2, count)

        except arcpy.ExecuteError:
            logger.error(arcpy.GetMessages())

        except Exception as e:
            logger.error("There is a non-geoprocessing error.")
            logger.error(e)

    logger.info("Closing ArcGIS 10")
    del arcpy
