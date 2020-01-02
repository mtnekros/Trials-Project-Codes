import arcpy
print 'imports done'

wards = []

# caching wards
def cache_wards():
    ward_layer = r'C:\Users\PATHWAY\Desktop\Mugu Trails\OSM Diwas Edited\OSMappingBlank_1.gdb\Admin\Ward'
    with arcpy.da.SearchCursor( ward_layer, ['NEW_WARD_N', 'SHAPE@']) as cursor:
        for row in cursor:
            wards.append( ( row[0],row[1] ) )

cache_wards()
print 'caching done!'

def get_ward( geometry ):
    for wardNo, wardGeom in iter(wards):
        if geometry.within( wardGeom ):
            return wardNo
    return None
        
# update wards in shapefiles
workspace = input( "Enter the dataset url(String):" )
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

featureClasses = arcpy.ListFeatureClasses()
featureClasses = filter( lambda fc: fc not in ["Trail","Trail_Junction","Obstacle_Natural_Hazard"], featureClasses)

for layer in iter(featureClasses):
    print "Updating Layer", layer
    with arcpy.da.UpdateCursor( layer,['SHAPE@','Ward'] ) as cursor:
        for row in cursor:
            wardNo = get_ward( row[0] )
            row[1] = wardNo
        
            cursor.updateRow( row )
    print "Layer", layer, "Done!"

print "\nAll Done"
