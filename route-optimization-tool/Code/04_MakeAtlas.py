import arcpy
from arcpy.mp import ArcGISProject
from PyPDF2 import PdfFileMerger, PdfFileReader
import shutil
import re
import os
from datetime import date

# Set the working directory to the directory containing the script
script_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(script_directory)

working_directory = os.path.abspath(os.path.join(script_directory, "Atlasses"))

arcpy.ImportToolbox("toolboxes/FeaturesToGPX.tbx")
arcpy.gp.toolbox = "toolboxes/FeaturesToGPX.tbx"
arcpy.ImportToolbox("toolboxes/SpatialJoinLargestOverlap.tbx")
arcpy.gp.toolbox = "toolboxes/SpatialJoinLargestOverlap.tbx"
arcpy.env.overwriteOutput = True

duration = 1000  # milliseconds
freq = 440  # Hz

arcpy.CheckOutExtension("Network")
arcpy.CheckOutExtension("Spatial")

merger = PdfFileMerger()
mainpath = os.path.join(os.path.dirname(working_directory), "OutputVRP")
mxdPath = os.path.join(os.path.dirname(mainpath), "Atlasses", "projectMap.aprx")
mxd = arcpy.mp.ArcGISProject(mxdPath)

dataFrame = (mxdPath, "COUNTIES")[0]

df = mxd.listMaps("Layers")[0]

sourceLayerRoads = arcpy.mp.LayerFile("Atlasses/Stage_example.lyr")
sourceLayerOrders = arcpy.mp.LayerFile("Atlasses/Orders_Example.lyr")

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
    #"97": "Gurue",
    #"98": "aroundNampula"
}

for dists in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
    dist = districts["{}".format(dists)]
    try:
        shutil.rmtree(os.path.join("Atlasses", dist))
    except:
        print("Folder  {} could not be deleted".format(dist))
        pass

    os.mkdir(os.path.join("Atlasses", dist))
    print(dist)

    try:
        arcpy.Delete_management("Atlasses/WorkingGDB{}.gdb".format(dist))
    except:
        pass

    arcpy.CreateFileGDB_management("Atlasses", "WorkingGDB{}".format(dist))
    for bb in ["Troco", ""]:
        for b in range(1, 5):
            for d in range(1, 27):
                try:
                    for f in os.listdir(os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d))):
                        pattern = "RoutesMerged_Dist{}_Base(.*?)_Day{}.shp".format(dist, d)
                        substring = re.search(pattern, f)
                        if substring:
                            baseName = substring.group(1)
                            print("baseName:", baseName)

                    cursor = arcpy.da.SearchCursor(os.path.join(mainpath, dist, "Base{}{}".format(bb, b),
                                                                "Day{}".format(d),
                                                                "RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist,
                                                                                                              baseName,
                                                                                                              d)),
                                                   "Stage")
                    Stages = []
                    for row in cursor:
                        Stages.append(row[0])
                    print("Stages:", Stages)
                    maxStage = max(Stages)
                    print("max:", maxStage)

                    arcpy.CalculateField_management(
                        os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                     "RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, baseName, d)),
                        "Base", maxStage, "PYTHON_9.3", "")

                    arcpy.CopyFeatures_management(
                        os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                     "RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, baseName, d)),
                        "Atlasses/WorkingGDB{}.gdb/route{}{}_{}".format(dist, bb, b, d), "", "0", "0", "0")

                    arcpy.AddGeometryAttributes_management(
                        os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                     "RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, baseName, d)),
                        "LINE_START_MID_END;LENGTH_GEODESIC", "KILOMETERS", "", "")

                    arcpy.MakeXYEventLayer_management(
                        os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                     "RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, baseName, d)), "END_X",
                        "END_Y",
                        "PointLayer", "", "")

                    arcpy.CopyFeatures_management("PointLayer",
                                                  os.path.join(mainpath, dist, "Base{}{}".format(bb, b),
                                                               "Day{}".format(d),
                                                               "OrdersPoints_Dist{}_Base{}_Day{}.shp".format(dist,
                                                                                                             baseName,
                                                                                                             d)),
                                                  "", "0", "0", "0")

                    arcpy.Select_analysis(os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                                       "PointLayer"), "{}/mktsCount.shp".format(mainpath),
                                          " \"StgType\" =  'Market'")
                    arcpy.Select_analysis(os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                                       "PointLayer"), "{}/feiraCount.shp".format(mainpath),
                                          " \"StgType\" =  'Feira'")
                    arcpy.Select_analysis(os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                                       "PointLayer"), "{}/crossCount.shp".format(mainpath),
                                          " \"StgType\" =  'Crossing'")
                    arcpy.Select_analysis(os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                                       "PointLayer"), "{}/LCCkptCount.shp".format(mainpath),
                                          " \"StgType\" =  'LCCkpt'")

                    result = arcpy.GetCount_management("{}/mktsCount.shp".format(mainpath))
                    mkts = int(result.getOutput(0))

                    result = arcpy.GetCount_management("{}/feiraCount.shp".format(mainpath))
                    feiras = int(result.getOutput(0))

                    result = arcpy.GetCount_management("{}/crossCount.shp".format(mainpath))
                    cross = int(result.getOutput(0))

                    result = arcpy.GetCount_management("{}/LCCkptCount.shp".format(mainpath))
                    ckpts = int(result.getOutput(0))

                    result = arcpy.GetCount_management(
                        os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d), "PointLayer"))
                    roads = int(result.getOutput(0))

                    total_length = 0.0
                    with arcpy.da.SearchCursor(
                            os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d), "PointLayer"),
                            ("LENGTH_GEO")) as cursor:
                        for row in cursor:
                            total_length += row[0]

                    newlayerRoads = arcpy.mapping.Layer(
                        os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                     "RoutesMerged_Dist{}_Base{}_Day{}.shp".format(dist, baseName, d)))
                    newlayerOrders = arcpy.mapping.Layer(
                        os.path.join(mainpath, dist, "Base{}{}".format(bb, b), "Day{}".format(d),
                                     "OrdersPoints_Dist{}_Base{}_Day{}.shp".format(dist, baseName, d)))
                    arcpy.mapping.AddLayer(df, newlayerRoads, "TOP")
                    arcpy.mapping.AddLayer(df, newlayerOrders, "TOP")

                    updateLayerRoads = arcpy.mapping.ListLayers(mxd, "RoutesMerged_Dist{}_Base{}_Day{}".format(dist,
                                                                                                              baseName,
                                                                                                              d),
                                                               df)[0]
                    updateLayerOrders = arcpy.mapping.ListLayers(mxd, "OrdersPoints_Dist{}_Base{}_Day{}".format(dist,
                                                                                                                baseName,
                                                                                                                d),
                                                                df)[0]

                    arcpy.mapping.UpdateLayer(df, updateLayerRoads, sourceLayerRoads, symbology_only=False)

                    updateLayerRoads.replaceDataSource("Atlasses/WorkingGDB{}.gdb".format(dist),
                                                       "FILEGDB_WORKSPACE", "route{}{}_{}".format(bb, b, d))

                    for lblClass in updateLayerRoads.labelClasses:
                        lblClass.expression = "(" + "[Stage]" + ")"
                    updateLayerRoads.showLabels = True

                    arcpy.mapping.UpdateLayer(df, updateLayerOrders, sourceLayerOrders, symbology_only=True)

                    ext = updateLayerRoads.getExtent()
                    df.extent = ext
                    df.scale = df.scale * 1.1

                    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapTitle")[0]
                    elm.text = "Distrito {}, Base {}, Dia {} ".format(dist, baseName, d)
                    elm.fontSize = 25
                    updateLayerRoads.name = "Rota de hoje"
                    updateLayerOrders.name = "Tarefas de hoje"
                    arcpy.RefreshActiveView()

                    listLayers = arcpy.mapping.ListLayers(mxd)
                    legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT")[0]
                    legend.removeItem(updateLayerOrders)
                    legend.removeItem(updateLayerRoads)

                    mxd.saveACopy(os.path.join("Atlasses", "Copy.mxd"))

                    #PDF = os.path.join("Atlasses", "{}/Map_Dist{}_Base{}_Day{}.pdf".format(dist, dist, baseName, d))
                    PDF = os.path.join("Atlasses", "{}_Map_Dist{}_Base{}_Day{}.pdf".format(dist, dist, baseName, d))
                    arcpy.mapping.ExportToPDF(mxd, PDF, "PAGE_LAYOUT", resolution=75, df_export_width=1100,
                                              df_export_height=800)

                    print("Dist{}_Base{}{}_Day{}.pdf".format(dist, bb, b, d))

                    arcpy.mapping.UpdateLayer(df, updateLayerRoads, sourceLayerRoads, symbology_only=True)
                    arcpy.mapping.RemoveLayer(df, newlayerRoads)
                    arcpy.mapping.RemoveLayer(df, updateLayerRoads)
                    arcpy.mapping.RemoveLayer(df, newlayerOrders)
                    arcpy.mapping.RemoveLayer(df, updateLayerOrders)

                except Exception as e:
                    print(e)
                    print("No Dist{}_Base{}{}_Day{}.pdf".format(dist, bb, b, d))
                    pass
    for filename in os.listdir(os.path.join("Atlasses", dist)):
        with open(os.path.join("Atlasses", dist, filename), 'rb') as source:
            tmp = PdfFileReader(source)
            merger.append(tmp)

    merger.write(os.path.join("Atlasses", "all_{}.pdf".format(dist)))
    merger = PdfFileMerger()

today = date.today()

with open(os.path.join("Atlasses", "FrontPage.pdf"), 'rb') as source:
    tmp = PdfFileReader(source)
    merger.append(tmp)

for dists in range(1, 12):
    dist = districts["{}".format(dists)]
    print(dist)

    with open(os.path.join("Atlasses", "all_{}.pdf".format(dist)), 'rb') as source:
        tmp = PdfFileReader(source)
        merger.append(tmp)

merger.write(os.path.join("Atlasses", "Atlas_allDistricts_{}.pdf".format(today.strftime("%d%m%Y"))))
merger = PdfFileMerger()

del mxd
