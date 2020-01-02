import arcpy
import os

print "Import Done!"

def GetFieldNames( featureLayer ):
    return list( field.name for field in arcpy.ListFields( featureLayer ) )

def DeleteAllRowsOf( in_workspace,featureClass ):
    assert( "OSM Low Rez Photos GDB" in in_workspace )

    layer = os.path.join( in_workspace,featureClass )
    with arcpy.da.UpdateCursor( layer,GetFieldNames( layer ) ) as cursor:
        for row in cursor:
            cursor.deleteRow() 

def CopyAttributesFromTo( srcDataset,destDataset,featureClass ):
    srcLayer = os.path.join( srcDataset,featureClass )
    destLayer = os.path.join( destDataset,featureClass )
    assert( "OSM Low Rez Photos GDB" in destLayer )

    fields = filter( lambda f : f not in ["Image","OBJECTID","FID"], GetFieldNames( srcLayer ) ) # cursor don't support image field
    destCursor = arcpy.da.InsertCursor( destLayer,fields )
    with arcpy.da.SearchCursor( srcLayer,fields ) as cursor:
        for row in cursor:
            destCursor.insertRow( row )
    del destCursor


if __name__ == '__main__':
    srcWorkspace = r""
    destWorkspace = r""
    
    arcpy.env.workspace = srcWorkspace
    featureClasses = filter( lambda fc : fc != "Trail", arcpy.ListFeatureClasses() )

    for fc in featureClasses:
        # print "****Deleted Destination",fc,"Started****"
        # DeleteAllRowsOf( destWorkspace,fc )
        # print "****Deleted Destination",fc,"Completed****"
        print "---------------------------------------------------"
        print "****Copying",fc,"Started****"
        CopyAttributesFromTo( srcWorkspace,destWorkspace,fc )
        print "****Copying",fc,"Completed****"
        print "---------------------------------------------------\n"

    