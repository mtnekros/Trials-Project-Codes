import arcpy

arcpy.env.workspace = r"C:\Users\Diwas\Desktop\Mugu Trails\WorkingGDB\Working.gdb\osmapping"
# featureClasses = filter( lambda fc: fc!="Trail",arcpy.ListFeatureClasses() )
featureClasses = []
print list(featureClasses)

def fillNAWhereAppropriate( row,nFields ):
    for i in xrange(nFields):
        rowValue = row[i] if row[i] is None else row[i].strip().lower()
        if rowValue in (None,"","photo"):
            row[i] = "N/A"

for fc in featureClasses:
    fields = filter( lambda f: f.type=="String" and not f.name.endswith("loc"), arcpy.ListFields( fc ) )
    fieldNames = list( f.name for f in fields )
    print "*********************",fc,"*********************"
    print " ".join(fieldNames)
    with arcpy.da.UpdateCursor( fc,fieldNames ) as cursor:
        for row in cursor:
            fillNAWhereAppropriate( row,len(fieldNames) )
            cursor.updateRow( row )
    print "----------------------------------------------------------\n"