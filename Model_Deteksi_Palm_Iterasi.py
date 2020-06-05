# Import Module
import arcpy
from arcpy.ia import *
import glob
from sys import argv
import os
import shutil


#CheckSystem
arcpy.env.overwriteOutput = False
arcpy.CheckOutExtension("ImageAnalyst")

#Mendefinisikan Variable
in_raster = "D:\\SANDI\\DEEP LEARNING\\TEST CMD\\*.jp2"
in_model_definition = "C:/tensorflow/models/research/object_detection/PalmDetection/PalmDetection.emd"
model_arguments = "padding 0; score_threshold 0.6; batch_size 4"
run_nms = "NMS"
confidence_score_field = "Confidence"
class_value_field = "Class"
max_overlap_ratio = 0.15
processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"


#Definisikan Output
dataset = glob.glob(in_raster)
print("Daftar Proses:")

for raster in dataset:
    print("Deteksi:", raster)
	
#Membuat Directory Output
for raster in dataset:
    try:
        outputraw = raster[:-14] + "\RAW"
        outputfinal =raster[:-14] + "\HASIL"
        os.mkdir(outputraw)
        os.mkdir(outputfinal)
        
        arcpy.CreateFileGDB_management("D:\SANDI\DEEP LEARNING\TEST CMD\RAW", "RAW.gdb")
        arcpy.CreateFileGDB_management("D:\SANDI\DEEP LEARNING\TEST CMD\FINAL", "FINAL.gdb")
        
        
    except FileExistsError:
        pass


#Proses Deteksi
for raster in dataset:
    
    #Membuat Variable Input Output
    outputraw = raster[:-14] + "\RAW"
    outputfinal =raster[:-14] + "\HASIL"
    outputrawgdb = outputraw + "\RAW.gdb"
    outputfinalgdb = outputfinal + "\FINAL.gdb"

    try:
        print("Proses Deteksi:", raster)
        with arcpy.EnvManager(extent="DEFAULT"):
            DetectObjectsUsingDeepLearning(raster, outputrawgdb + raster[-14:-4] +"_Detected",
                                           in_model_definition, model_arguments, run_nms, confidence_score_field,
                                           class_value_field, max_overlap_ratio)
    except AttributeError:
        pass



#Proses PostProcessing
#for raster in dataset:
    
    print("Post_Processing:", raster)
    
    #Membuat Variable Input Output
    outputraw = raster[:-14] + "\RAW"
    outputfinal =raster[:-14] + "\HASIL"
    
    shpdata = outputrawgdb + raster[-14:-4]+"_Detected"
    shppoint = outputrawgdb + raster[-14:-4]+"_Point"
    dissolve = outputrawgdb + raster[-14:-4]+"_Dissolve"
    shpsj = outputrawgdb + raster[-14:-4]+"_SJ.shp"
    finalresult = outputfinalgdb + raster[-14:-4]+"_Crown"
    
    #Post Processing Lokasi
    arcpy.FeatureToPoint_management(in_features=shpdata,
                                    out_feature_class=shppoint, point_location="CENTROID")
    arcpy.AddField_management(in_table=shppoint,
                              field_name="LONGITUDE",
                              field_type="DOUBLE", field_precision=None, field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.AddField_management(in_table=shppoint,
                              field_name="LATITUDE",
                              field_type="DOUBLE", field_precision=None, field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.Integrate_management(in_features=[[shppoint, ""]], cluster_tolerance="2.2 Meters")
    arcpy.CalculateGeometryAttributes_management(in_features=shppoint, geometry_property=[["LONGITUDE", "POINT_X"], ["LATITUDE", "POINT_Y"]],
                                                 length_unit="", area_unit="",
                                                 coordinate_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
    with arcpy.EnvManager(XYTolerance="1 Meters"):
        arcpy.Dissolve_management(in_features=shppoint, out_feature_class=dissolve,
                                  dissolve_field=["LONGITUDE", "LATITUDE"], statistics_fields=[["LONGITUDE", "FIRST"], ["LATITUDE", "FIRST"]], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.DeleteIdentical_management(in_dataset=dissolve, fields=["LONGITUDE", "LATITUDE"], xy_tolerance="1 Meters", z_tolerance=0)
    arcpy.Near_analysis(in_features=dissolve, near_features=[dissolve], search_radius="2 Meters", location="NO_LOCATION", angle="NO_ANGLE", method="PLANAR")
    arcpy.DeleteIdentical_management(in_dataset=dissolve,
                                     fields=["LONGITUDE", "LATITUDE", "NEAR_DIST"], xy_tolerance="", z_tolerance=0)
    
    #Post Processing Atribut
    arcpy.AddField_management(in_table=shpdata,
                              field_name="Xmin", field_type="DOUBLE", field_precision=None, field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.AddField_management(in_table=shpdata,
                              field_name="Xmax", field_type="DOUBLE", field_precision=None, field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.AddField_management(in_table=shpdata,
                              field_name="Ymin", field_type="DOUBLE", field_precision=None, field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.AddField_management(in_table=shpdata,
                              field_name="Ymax", field_type="DOUBLE", field_precision=None, field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.AddField_management(in_table=shpdata,
                              field_name="Dg", field_type="DOUBLE", field_precision=None, field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.AddField_management(in_table=shpdata,
                              field_name="R", field_type="DOUBLE", field_precision=None, field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.CalculateGeometryAttributes_management(in_features=shpdata,
                                                 geometry_property=[["Xmin", "EXTENT_MIN_X"], ["Xmax", "EXTENT_MAX_X"], ["Ymin", "EXTENT_MIN_Y"], ["Ymax", "EXTENT_MAX_Y"]], length_unit="", area_unit="",
                                                 coordinate_system="PROJCS['WGS_1984_UTM_Zone_49S',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]")
    arcpy.CalculateField_management(in_table=shpdata,
                                    field="Dg", expression="math.sqrt(((!Xmax!-!Xmin!)**2)+((!Ymax! - !Ymin!)**2))", expression_type="PYTHON3", code_block="")
    arcpy.CalculateField_management(in_table=shpdata, field="R", expression="!Dg!/(2*math.sqrt(2))", expression_type="PYTHON3", code_block="")
    
    arcpy.SelectLayerByLocation_management(in_layer=[shpdata], overlap_type="INTERSECT", select_features=dissolve, search_distance="", selection_type="NEW_SELECTION", invert_spatial_relationship="INVERT")
 
    
    
    #Spatial Join
    arcpy.SpatialJoin_analysis(target_features=dissolve, join_features=shpdata,
                               out_feature_class=shpsj,
                               join_operation="JOIN_ONE_TO_ONE",
                               join_type="KEEP_ALL",
                               field_mapping="LONGITUDE \"LONGITUDE\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,LONGITUDE,-1,-1;LATITUDE \"LATITUDE\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,LATITUDE,-1,-1;FIRST_LONGITUDE \"FIRST_LONGITUDE\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,FIRST_LONGITUDE,-1,-1;FIRST_LATITUDE \"FIRST_LATITUDE\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,FIRST_LATITUDE,-1,-1;NEAR_FID \"NEAR_FID\" true true false 0 Long 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,NEAR_FID,-1,-1;NEAR_DIST \"NEAR_DIST\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,NEAR_DIST,-1,-1;Class \"Class\" true true false 1024 Text 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Class,0,1024;Confidence \"Confidence\" true true false 8 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Confidence,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Shape_Area,-1,-1;Xmin \"Xmin\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Xmin,-1,-1;Xmax \"Xmax\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Xmax,-1,-1;Ymin \"Ymin\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Ymin,-1,-1;Ymax \"Ymax\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Ymax,-1,-1;Dg \"Dg\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Dg,-1,-1;R \"R\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,R,-1,-1;LONGITUDE_1 \"LONGITUDE\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,LONGITUDE,-1,-1;LATITUDE_1 \"LATITUDE\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,LATITUDE,-1,-1;FIRST_LONGITUDE_1 \"FIRST_LONGITUDE\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,FIRST_LONGITUDE,-1,-1;FIRST_LATITUDE_1 \"FIRST_LATITUDE\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,FIRST_LATITUDE,-1,-1;NEAR_FID_1 \"NEAR_FID\" true true false 0 Long 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,NEAR_FID,-1,-1;NEAR_DIST_1 \"NEAR_DIST\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\LOKASI_PALM,NEAR_DIST,-1,-1;Class_1 \"Class\" true true false 1024 Text 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Class,0,1024;Confidence_1 \"Confidence\" true true false 8 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Confidence,-1,-1;Shape_Length_1 \"Shape_Length\" false true true 8 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Shape_Length,-1,-1;Shape_Area_1 \"Shape_Area\" false true true 8 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Shape_Area,-1,-1;Xmin_1 \"Xmin\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Xmin,-1,-1;Xmax_1 \"Xmax\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Xmax,-1,-1;Ymin_1 \"Ymin\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Ymin,-1,-1;Ymax_1 \"Ymax\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Ymax,-1,-1;Dg_1 \"Dg\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,Dg,-1,-1;R_1 \"R\" true true false 0 Double 0 0,First,#,D:\\DEEP LEARNING\\SANDI_TEST.gdb\\HASIL_OBJECT_DETECTION_16_1,R,-1,-1", match_option="INTERSECT", search_radius="", distance_field_name="")
    arcpy.Buffer_analysis(in_features=shpsj, out_feature_class=finalresult,
                          buffer_distance_or_field="R", line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field=[], method="PLANAR")

print("Proses Deteksi Selesai Yeyyyyyy Senangnyaaaaa!!!!!!!!!!!!!!!!!!!!!")