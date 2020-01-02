import arcpy
print "Import Done\n"
print "----------------------------------------------------"

def IntersectAndGetCount( featureClass,municipality_layer,municipality,summary ):
    feature_layer = 'feature_layer'
    # make feature layers ready for selection
    arcpy.MakeFeatureLayer_management( featureClass,feature_layer )
    # selecting required municipality
    arcpy.SelectLayerByAttribute_management( 
        municipality_layer,
        "NEW_SELECTION",
        " GaPa_NaPa = '{}' ".format(municipality) 
    )
    # selecting the feature layer that intersects with the selected municipality
    arcpy.SelectLayerByLocation_management(
        feature_layer,
        'INTERSECT',
        municipality_layer
    )
    return arcpy.GetCount_management( feature_layer )[0]
    
if __name__ == "__main__":
    arcpy.env.workspace = r"C:\Users\Diwas\Desktop\Mugu Trails\WorkingGDB\Working.gdb\osmapping"
    arcpy.env.overwriteOutput = True
    featureClasses = arcpy.ListFeatureClasses()
    municipality_fc = r"C:\Users\Diwas\Desktop\Mugu Trails\WorkingGDB\OldGDBLowRez.gdb\Admin\Municipality"
    municipality_layer = arcpy.MakeFeatureLayer_management( municipality_fc,'municipality_layer' )
    
    municipalityList = ["Mugum Karmarong","Khatyad","Chhayanath Rara","Soru"]
    summary = [ "Feature, {}\n".format( ", ".join(municipalityList) ) ]
    for fc in featureClasses:
        record = fc
        for municipality in iter( municipalityList ):
            count = IntersectAndGetCount( fc,municipality_layer,municipality,summary )
            record += ", " + str( count )
            print "{} has {} {}".format( municipality,count,fc )
        print "----------------------------------------------------"
        record += "\n"
        summary.append( record )

    with open("Summary.csv","w") as outFile:
        outFile.writelines( summary )