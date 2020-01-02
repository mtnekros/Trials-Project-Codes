import arcpy
print "Import Done!\n"

def cache_wards( ward_layer ):
    wards = []
    arcpy.MakeFeatureLayer_management( ward_layer,'ward_layer')
    with arcpy.da.SearchCursor( 'ward_layer', ['NEW_WARD_N','GaPa_NaPa','Type_GN', 'SHAPE@']) as cursor:
        for row in cursor:
            wards.append({
                "NEW_WARD_N": row[0],
                "GaPa_NaPa": row[1],
                "Type_GN": row[2],
                "Geometry": row[3]
            })
    return wards

def GetMuniAndWard(ptGeom, wards):
    for ward in wards:
        if ward["Geometry"].contains( ptGeom ):
            municipality = ward["GaPa_NaPa"] # +" " + ward["Type_GN"]
            wardNo = ward["NEW_WARD_N"]
            return municipality, wardNo 


if __name__ == "__main__":
    ward_layer = r"C:\Users\Diwas\Desktop\Mugu Trails\WorkingGDB\Working.gdb\Admin\Ward"
    arcpy.env.workspace = r"C:\Users\Diwas\Desktop\Mugu Trails\WorkingGDB\Working.gdb\osmapping"
    
    wards = cache_wards( ward_layer )
    featureClasses = ["Community_Space"]
    
    for fc in featureClasses:
        with arcpy.da.UpdateCursor( fc, ["Municipality","SHAPE@"] ) as cursor:
            for row in cursor:
                municipality,wardNo = GetMuniAndWard( row[1], wards )
                row[0] = municipality
                cursor.updateRow( row )
        print "{}'s Municipality Updated!".format( fc )
    
    print "\nAll Done!!"