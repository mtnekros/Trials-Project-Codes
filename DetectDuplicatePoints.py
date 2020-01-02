import arcpy

def getIDofNearbyGeom( suspect,geomList,tolerance ):
    for geom in iter(geomList):
        distance = suspect.distanceTo( geom[0] )
        if distance < tolerance:
            return {"ID": geom[1],"distance": distance}# return the objectid of geom and distance between the suspect and geom
    return None

if __name__ == "__main__":
    arcpy.env.workspace = r"C:\Users\Diwas\Desktop\Mugu Trails\WorkingGDB\Working.gdb\osmapping\#! Delete this and change later"
    featureClasses = filter( lambda fc: fc != "Trail", arcpy.ListFeatureClasses() )
    toleranceRadius = 35 # tolerance in meter

    for fc in featureClasses:
        if all( field.name != "Duplicate Suspect" for field in arcpy.ListFields(fc) ):
            arcpy.AddField_management( fc,"Duplicate_Suspect","TEXT" )
        geomsInFc = []
        nSuspects = 0
        with arcpy.da.UpdateCursor( fc,["Duplicate_Suspect","SHAPE@","OBJECTID"]) as cursor:
            for row in cursor:
                geometry = row[1]
                objectid = row[2]
                if row[0].strip() == "False": # in case it's already determined to not a duplicate no caculations required
                    geomsInFc.append( (geometry,objectid) )
                    continue
                result = getIDofNearbyGeom( geometry,geomsInFc,toleranceRadius )
                if result is None:
                    row[0] = "False"
                else:
                    # print "{} might be a duplicate".format(row[2])
                    row[0] = "True of ID: {} Distance: {}".format(result["ID"],result["distance"])
                    nSuspects += 1
                cursor.updateRow( row ) 
                geomsInFc.append( (geometry,objectid) )
        print "No of suspects in {} is {}".format( fc,nSuspects )