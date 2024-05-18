import arcpy
import os
import shutil
import re
from PyPDF2 import PdfFileMerger, PdfFileReader
from datetime import date

# Initialize ArcGIS licenses
if arcpy.CheckProduct("ArcInfo") != "Available":
    raise RuntimeError("ArcInfo license is not available")

# Check out necessary extensions
if arcpy.CheckExtension("Network") == "Available":
    arcpy.CheckOutExtension("Network")
else:
    raise RuntimeError("Network Analyst license is not available")

if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")
else:
    raise RuntimeError("Spatial Analyst license is not available")

# Set environment settings
arcpy.env.overwriteOutput = True

# Define paths
mainpath = r"C:\Users\idels\Documents\github\route-optimization-tool\OutputVRP"
output_folder = r"C:\Users\idels\Documents\github\route-optimization-tool\Atlasses"
project_path = r"C:\Users\idels\Documents\github\route-optimization-tool\projectMap.aprx"  # Update with your actual project path
layout_template_path = r"C:\Users\idels\Documents\github\route-optimization-tool\template.pagx"  # Update with your actual template path

# Initialize PDF merger
merger = PdfFileMerger()

# Districts dictionary
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
    #"98": "aroundNampula"
}

def list_layouts(aprx):
    print("Layouts in the project:")
    for layout in aprx.listLayouts():
        print(f"Layout: {layout.name}")

def process_district(dist, bb, b, d):
    try:
        baseName = None  # Initialize baseName to None
        directory = f"{mainpath}\\{dist}\\Base{bb}{b}\\Day{d}"
        if not os.path.exists(directory):
            print(f"Directory does not exist: {directory}")
            return False
        
        for f in os.listdir(directory):
            pattern = f"RoutesMerged_Dist{dist}_Base(.*?)_Day{d}.shp"
            substring = re.search(pattern, f)
            if substring:
                baseName = substring.group(1)
                print("baseName:", baseName)
        
        if baseName is None:
            print(f"No matching files found for District: {dist}, Base: {bb}{b}, Day: {d}")
            return False

        shapefile_path = os.path.join(directory, f"RoutesMerged_Dist{dist}_Base{baseName}_Day{d}.shp")
        if not os.path.exists(shapefile_path):
            print(f"Shapefile does not exist: {shapefile_path}")
            return False

        cursor = arcpy.da.SearchCursor(shapefile_path, "Stage")
        Stages = [row[0] for row in cursor]
        if not Stages:
            print(f"No stages found in {shapefile_path}")
            return False

        print("Stages:", Stages)
        maxStage = max(Stages)
        print("max:", maxStage)
        arcpy.CopyFeatures_management(
            shapefile_path,
            os.path.join(output_folder, f"WorkingGDB{dist}.gdb", f"route{bb}{b}_{d}")
        )
        arcpy.AddField_management(
            os.path.join(output_folder, f"WorkingGDB{dist}.gdb", f"route{bb}{b}_{d}"),
            "maxPerDay", "LONG"
        )
        arcpy.CalculateField_management(
            os.path.join(output_folder, f"WorkingGDB{dist}.gdb", f"route{bb}{b}_{d}"),
            "maxPerDay", maxStage, "Python", ""
        )

        arcpy.AddGeometryAttributes_management(
            os.path.join(output_folder, f"WorkingGDB{dist}.gdb", f"route{bb}{b}_{d}"),
            "LINE_START_MID_END;LENGTH_GEODESIC", "KILOMETERS", "", ""
        )
        arcpy.MakeXYEventLayer_management(
            os.path.join(output_folder, f"WorkingGDB{dist}.gdb", f"route{bb}{b}_{d}"),
            "END_X", "END_Y", "PointLayer", "", ""
        )
        arcpy.CopyFeatures_management(
            "PointLayer",
            f"{mainpath}\\{dist}\\Base{bb}{b}\\Day{d}\\OrdersPoints_Dist{dist}_Base{baseName}_Day{d}.shp"
        )
        arcpy.Select_analysis("PointLayer", f"{mainpath}\\mktsCount.shp", " \"StgType\" =  'Market'")
        arcpy.Select_analysis("PointLayer", f"{mainpath}\\feiraCount.shp", " \"StgType\" =  'Feira'")
        arcpy.Select_analysis("PointLayer", f"{mainpath}\\crossCount.shp", " \"StgType\" =  'Crossing'")
        arcpy.Select_analysis("PointLayer", f"{mainpath}\\LCCkptCount.shp", " \"StgType\" =  'LCCkpt'")
        
        result = arcpy.GetCount_management(f"{mainpath}\\mktsCount.shp")
        mkts = int(result.getOutput(0))
        result = arcpy.GetCount_management(f"{mainpath}\\feiraCount.shp")
        feiras = int(result.getOutput(0))
        result = arcpy.GetCount_management(f"{mainpath}\\crossCount.shp")
        cross = int(result.getOutput(0))
        result = arcpy.GetCount_management(f"{mainpath}\\LCCkptCount.shp")
        ckpts = int(result.getOutput(0))
        result = arcpy.GetCount_management("PointLayer")
        roads = int(result.getOutput(0))
        total_length = 0.0
        with arcpy.da.SearchCursor("PointLayer", ("LENGTH_GEO",)) as cursor:
            for row in cursor:
                total_length += row[0]

        # Import and configure the layout
        try:
            aprx = arcpy.mp.ArcGISProject(project_path)  # Use the specified project path
            print("Opened project from specified path successfully")

            # List existing layouts
            list_layouts(aprx)

            # Import the layout template
            aprx.importDocument(layout_template_path)
            print(f"Imported layout from {layout_template_path}")

            # List layouts again to confirm import
            list_layouts(aprx)

            # Choose a specific map and imported layout
            map_name = "Map"  # Adjust this to the name of your map
            layout_name = "template"  # Adjust this to the name of your layout, the imported layout might have the name 'template'

            selected_map = next((m for m in aprx.listMaps() if m.name == map_name), None)
            selected_layout = next((l for l in aprx.listLayouts() if l.name == layout_name), None)

            if not selected_map:
                raise RuntimeError(f"Map '{map_name}' not found in the project.")
            if not selected_layout:
                raise RuntimeError(f"Layout '{layout_name}' not found in the project.")

            print(f"Using map: {selected_map.name}")
            print(f"Using layout: {selected_layout.name}")

        except Exception as e:
            print(f"Error accessing project elements: {e}")
            return False

        # Ensure map frame exists
        map_frames = selected_layout.listElements("mapframe_element")
        if len(map_frames) == 0:
            print("No map frame found in the layout. Please add a map frame.")
            return False
        map_frame = map_frames[0]
        map_frame.map = selected_map
        print("Set the map for the map frame")

        # Ensure title element exists
        titles = selected_layout.listElements("TEXT_ELEMENT", "Title")
        if len(titles) == 0:
            print("No title element found in the layout. Please add a text element named 'Title'.")
            return False
        title = titles[0]
        title.text = f"Distrito {dist}, Base {baseName}, Dia {d}"
        title.elementPositionX = 2
        title.elementPositionY = 7.5
        title.fontSize = 20
        title.font = "Arial"
        print("Updated title element")

        # Ensure legend element exists
        legends = selected_layout.listElements("LEGEND_ELEMENT")
        if len(legends) == 0:
            print("No legend element found in the layout. Please add a legend element.")
            return False
        legend = legends[0]
        legend.autoAdd = True
        legend.mapFrame = map_frame
        print("Updated legend element")

        # Ensure scale bar element exists
        scale_bars = selected_layout.listElements("MAPSURROUND_ELEMENT", "Scale Bar")
        if len(scale_bars) == 0:
            print("No scale bar element found in the layout. Please add a scale bar element.")
            return False
        scale_bar = scale_bars[0]
        scale_bar.style = "Single Division Scale Bar"
        scale_bar.mapFrame = map_frame
        print("Updated scale bar element")

        # Ensure north arrow element exists
        north_arrows = selected_layout.listElements("MAPSURROUND_ELEMENT", "North Arrow")
        if len(north_arrows) == 0:
            print("No north arrow element found in the layout. Please add a north arrow element.")
            return False
        north_arrow = north_arrows[0]
        north_arrow.style = "North Arrow (Circle)"
        north_arrow.mapFrame = map_frame
        print("Updated north arrow element")

        desc = arcpy.Describe(shapefile_path)
        ext = desc.extent
        map_frame.camera.setExtent(ext)
        map_frame.camera.scale = map_frame.camera.scale * 1.1

        output_pdf = os.path.join(output_folder, f"{dist}", f"Map_Dist{dist}_Base{baseName}_Day{d}.pdf")
        selected_layout.exportToPDF(output_pdf, resolution=75)
        print(f"{output_pdf} generated successfully")

        # Cleanup
        del aprx

    except Exception as e:
        print(f"Error processing District: {dist}, Base: {bb}{b}, Day: {d} - {e}")
        print(f"No Dist{dist}_Base{bb}{b}_Day{d}.pdf")
        return False

    return True

for dists in districts:  # Example: process district 1
    dist = districts["{}".format(dists)]
    try:
        shutil.rmtree(os.path.join(output_folder, dist))
    except Exception as e:
        print(f"Folder {dist} could not be deleted: {e}")
        pass
    os.mkdir(os.path.join(output_folder, dist))
    print(dist)

    try:
        arcpy.Delete_management(os.path.join(output_folder, f"WorkingGDB{dist}.gdb"))
    except Exception as e:
        print(f"Could not delete WorkingGDB{dist}.gdb: {e}")
        pass

    # Create File GDB
    arcpy.CreateFileGDB_management(output_folder, f"WorkingGDB{dist}")
    for bb in ["Troco", ""]:
        for b in range(1, 5):
            for d in range(1, 15):
                if not process_district(dist, bb, b, d):
                    continue

    for filename in os.listdir(os.path.join(output_folder, dist)):
        with open(os.path.join(output_folder, dist, filename), 'rb') as source:
            tmp = PdfFileReader(source)  # Ensure PdfFileReader is defined
            merger.append(tmp)
    merger.write(os.path.join(output_folder, f"all_{dist}.pdf"))
    merger = PdfFileMerger()

today = date.today()
with open(os.path.join(output_folder, "FrontPage.pdf"), 'rb') as source:
    tmp = PdfFileReader(source)
    merger.append(tmp)
for dists in range(1, 12):
    dist = districts["{}".format(dists)]
    print(dist)
    with open(os.path.join(output_folder, f"all_{dist}.pdf"), 'rb') as source:
        tmp = PdfFileReader(source)
        merger.append(tmp)
merger.write(os.path.join(output_folder, f"Atlas_allDistricts_{today.strftime('%d%m%Y')}.pdf"))
merger = PdfFileMerger()
