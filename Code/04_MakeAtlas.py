import arcpy
from arcpy.mp import ArcGISProject
from PyPDF2 import PdfFileMerger, PdfFileReader
from datetime import date
import os
import shutil
import re

# Set up the paths and environments
working_directory = r'C:\Users\Idelson Mindo\Documents\GitHub\routes_RTMOZ\Atlasses'
mainpath = "OutputVRP"
mxd_path = "AtlasLuabo_upd2023.mxd"
arcpy.env.overwriteOutput = True

# Navigate to the parent directory and then open the "Atlasses" folder
atlasses_directory = os.path.join(os.path.dirname(working_directory), "Atlasses")

# Create a PDF merger
merger = PdfFileMerger()

# Define districts
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

# Function to create a district folder and GDB
def create_district_folder_and_gdb(dist):
    folder_path = os.path.join(atlasses_directory, dist)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    print(f"Created folder for {dist}")

    try:
        arcpy.Delete_management(os.path.join(folder_path, f"WorkingGDB{dist}.gdb"))
    except:
        pass

    # Process: Create File GDB
    arcpy.CreateFileGDB_management(folder_path, f"WorkingGDB{dist}")
    print(f"Created GDB for {dist}")

# Iterate through districts
for dists in range(1, 12):
    dist = districts.get(str(dists))
    if dist:
        create_district_folder_and_gdb(dist)

        for bb in ["Troco", ""]:
            for b in range(1, 5):
                for d in range(1, 27):
                    try:
                        pdf_name = f"Dist{dist}_Base{bb}{b}_Day{d}.pdf"
                        pdf_path = os.path.join(atlasses_directory, dist, pdf_name)

                        # Check if the PDF already exists
                        if os.path.exists(pdf_path):
                            print(f"Skipped existing PDF: {pdf_path}")
                            continue

                        for f in os.listdir(os.path.join(mainpath, dist, f"Base{bb}{b}", f"Day{d}")):
                            pattern = "RoutesMerged_Dist{}_Base(.*?)_Day{}.shp".format(dist, d)
                            substring = re.search(pattern, f)
                            if substring:
                                base_name = substring.group(1)
                                print("Base name:", base_name)

                                cursor = arcpy.da.SearchCursor(os.path.join(mainpath, dist, f"Base{bb}{b}", f"Day{d}", f"RoutesMerged_Dist{dist}_Base{base_name}_Day{d}.shp"), "Stage")
                                stages = [row[0] for row in cursor]
                                max_stage = max(stages)
                                print("Max stage:", max_stage)

                                arcpy.CalculateField_management(os.path.join(mainpath, dist, f"Base{bb}{b}", f"Day{d}", f"RoutesMerged_Dist{dist}_Base{base_name}_Day{d}.shp"), "Base", max_stage, "PYTHON_9.3", "")
                                arcpy.CopyFeatures_management(os.path.join(mainpath, dist, f"Base{bb}{b}", f"Day{d}", f"RoutesMerged_Dist{dist}_Base{base_name}_Day{d}.shp"),
                                                              os.path.join(atlasses_directory, dist, f"WorkingGDB{dist}.gdb", f"route{bb}{b}_{d}"))

                        # Check if the resulting shapefile has valid data
                        if arcpy.management.GetCount(os.path.join(atlasses_directory, dist, f"WorkingGDB{dist}.gdb", f"route{bb}{b}_{d}")) == 0:
                            print(f"No data for {pdf_name}")
                            continue

                        # Your existing code for creating the PDF here

                        print(f"Created PDF: {pdf_path}")
                    except Exception as e:
                        print(e)
                        print(f"Error creating PDF for {pdf_name}: {e}")
                        pass

# Loop for merging district PDFs
merger_district = PdfFileMerger()

for filename in os.listdir(os.path.join(atlasses_directory, dist)):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(atlasses_directory, dist, filename)
        try:
            # Check if the PDF has pages before appending
            with open(pdf_path, 'rb') as source:
                tmp = PdfFileReader(source)
                if tmp.numPages > 0:
                    merger_district.append(tmp)
                    print(f"Appended content from {pdf_path}")
                else:
                    print(f"Skipped empty PDF: {pdf_path}")
        except FileNotFoundError:
            print(f"File not found: {pdf_path}")
        except Exception as e:
            print(f"Error appending PDF {pdf_path}: {e}")

# Check if any PDFs were appended before writing
if merger_district.pages:
    try:
        # Create the merged PDF in the working directory
        merged_pdf_path = os.path.join(working_directory, f"all_{dist}.pdf")
        merger_district.write(merged_pdf_path)
        print(f"Merged PDF created: {merged_pdf_path}")
    except Exception as e:
        print(f"Error writing merged PDF: {e}")
else:
    print(f"No PDFs with content to merge for {dist}")

# Close the merger to release the file handles
merger_district.close()

# Merge district PDFs
today = date.today()
file_path_frontpage = os.path.join(working_directory, 'FrontPage.pdf')

try:
    with open(file_path_frontpage, 'rb') as source:
        tmp = PdfFileReader(source)
        merger.append(tmp)
except FileNotFoundError:
    print(f"FrontPage.pdf not found: {file_path_frontpage}")

for dists in range(1, 12):
    dist = districts.get(str(dists))
    if dist:
        pdf_path_district = os.path.join(atlasses_directory, f"all_{dist}.pdf")
        try:
            with open(pdf_path_district, 'rb') as source:
                tmp = PdfFileReader(source)
                merger.append(tmp)
        except FileNotFoundError:
            print(f"File not found: {pdf_path_district}")

merger.write(os.path.join(working_directory, f"Atlas_allDistricts_{today.strftime('%d%m%Y')}.pdf"))

# Close the final merger to release the file handles
merger.close()
