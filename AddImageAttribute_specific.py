import arcpy
import os
from PIL import Image,ImageFile
import traceback
import shutil

# return a list of all the path + name of the jpg files(C:/.../smthg.jpg) in a directory and it's sub directories
def getAllPhotosFullPaths( path ):
    paths = []
    for root, dirs, filenames in os.walk(path):
        filenames = filter(lambda f: f.endswith(".jpg"), filenames)
        for filename in filenames:
            paths.append(os.path.join(root, filename))
    return paths

def deleteFieldOfAll( featureClasses,fieldName ):
    for fc in featureClasses:
        if  any(field.name == fieldName for field in iter(arcpy.ListFields(fc))):
            arcpy.DeleteField_management( fc,fieldName )

def filterClassesWithImgField(featureClasses):
    hasImgField = lambda fc : fc != "Trail" and any(field.name == "Image" for field in iter(arcpy.ListFields(fc)))
    return filter(hasImgField, featureClasses)


def getFullPhotoPath(allPhotoPaths, photoName):
# def getFullPhotoPath(allPhotoPaths, photoName, municipality):
    if len(photoName.strip()) == 0:
        return None
    # municipalityFirst = municipality.split(" ")[0]
    for photoPath in allPhotoPaths:
        # if photoPath.endswith(photoName) and municipalityFirst.lower() in photoPath.lower():
        if photoPath.endswith(photoName):
            return photoPath
    return None

# returns a dictionary of key: photoname and value: absolute photo path for a given featurelayer
# if two photos or more have same name they are discarded.
def filterPhotoPathsForLayer(allPhotosFullPaths, layer):
    photoPathNamePairs = {} 
    duplicatePhotoNames = []
    # with arcpy.da.SearchCursor(layer, ["Photo","Municipality"]) as cursor:
    with arcpy.da.SearchCursor(layer, ["Photo"]) as cursor:
        for row in cursor:
            photoName = row[0]
            if photoName in photoPathNamePairs.keys():
                duplicatePhotoNames.append( photoName )
                continue
            # path = getFullPhotoPath(allPhotosFullPaths, photoName, row[1])
            path = getFullPhotoPath(allPhotosFullPaths, photoName)
            if path is not None:
                photoPathNamePairs[photoName] = path
    # deleting duplicate photonames
    for key in duplicatePhotoNames:
        photoPathNamePairs.pop( key )
    return photoPathNamePairs


def resizeAndSavePhoto(fullPhotoPath, photoName, destination, resizeFactor):
    img = Image.open(fullPhotoPath)
    newSize = tuple([dim / resizeFactor for dim in img.size])
    img.resize(newSize, Image.ANTIALIAS).save(
        os.path.join(destination, photoName))


def makeRasterCatalog(featureClass, rc_name, in_GDB, imageFolderPath):
    rasterCatolog = rc_name
    arcpy.CreateRasterCatalog_management(in_GDB, rasterCatolog)
    arcpy.WorkspaceToRasterCatalog_management(
        imageFolderPath, os.path.join(in_GDB, rasterCatolog)
    )

# def fixFieldInfo(fieldInfo,rasterCatalog):
#     fieldInfo.setFieldName( fieldInfo.findFieldByName( rasterCatalog+".Raster" ),rasterCatalog+".Image" )
#     # remove unnecessary fields
#     fieldNames = [ "OBJECTID","Name","Shape_Length","Shape_Area" ]
#     fullFieldNames = map( lambda name: rasterCatalog+"."+name, fieldNames )
#     for name in fullFieldNames:
#         fieldInfo.removeField( fieldInfo.findFieldByName(name) )
#     return fieldInfo

# def joinWithCatalogAndSave( fc_workspace,featureClass,rc_workspace,rasterCatalog,outWorkspace ):
#     featureLayer = 'feature_layer'
#     arcpy.MakeFeatureLayer_management( os.path.join(fc_workspace,featureClass),featureLayer )
#     arcpy.AddJoin_management( featureLayer,"Photo", os.path.join(rc_workspace,rasterCatalog),"Name" )
#     fieldInfo = fixFieldInfo( arcpy.Describe( featureLayer ).fieldInfo,rasterCatalog )
#     arcpy.MakeFeatureLayer_management( featureLayer,'fieldCorrectedLayer',field_info=fieldInfo)
#     arcpy.CopyFeatures_management( 'fieldCorrectedLayer',os.path.join( outWorkspace,featureClass+"withPhotos") )

def joinWithCatalogAndSave( fc_workspace,featureClass,rc_workspace,rasterCatalog,outWorkspace ):
    featureLayer = 'feature_layer'
    arcpy.MakeFeatureLayer_management( os.path.join(fc_workspace,featureClass),featureLayer )
    arcpy.AddJoin_management( featureLayer,"Photo", os.path.join(rc_workspace,rasterCatalog),"Name" )
    outLayer = os.path.join( outWorkspace,featureClass+"withPhotos" )
    arcpy.CopyFeatures_management( featureLayer,outLayer )
    #  Delete unnecessary fields and rename field names to appropriate names
    extra_fields = [ "{}_{}".format(rasterCatalog,name) for name in ["OBJECTID","Name","Shape_Length","Shape_Area"] ]
    for field in extra_fields:
        arcpy.DeleteField_management( outLayer,field )
    fieldsToRename = filter( lambda name: featureClass in name, (f.name for f in arcpy.ListFields( outLayer ) ) )
    for fieldName in fieldsToRename:
        if "Raster" in fieldName:
            # arcpy.AlterField_management( outLayer,fieldName,"Image" )
            continue
        else:
            newFieldName = fieldName[ len(featureClass)+1: ]
            arcpy.AlterField_management( outLayer,fieldName,newFieldName )

if __name__ == "__main__":
    # ************** ! main variables to change ************** #
    rootImageFolderPath = r"C:\Users\Diwas\Desktop\Mugu Trails\all_photos"
    featureClasses = ["Obstacle_Natural_Hazard_Mixed"] 
    # featureClasses = [Financial_Institution",] 
    fc_workspace = r"C:\Users\Diwas\Desktop\Mugu Trails\OSM Low Rez Photos GDB\OSMappingBlank_1.gdb" # workspace of the input feature classes
    # rc_workspace = (fc_workspace).replace( r'osmapping', '').strip("\\").strip("/")
    rc_workspace = arcpy.env.scratchGDB
    outWorkspace = r"C:\Users\Diwas\Desktop\Mugu Trails\OSM Low Rez Photos GDB\OSMappingBlank_1.gdb" # workspace to save the output file # must be a gdb or can't alter
    imageFieldName = "Obstacle_Natural_Hazard_photos_Raster"
    imgResizeFactor = 5
    # ******************************************************** #

    allPhotosFullPaths = getAllPhotosFullPaths( rootImageFolderPath )
    # setting environment vars
    arcpy.env.workspace = fc_workspace
    arcpy.env.overwriteOutput = True
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    # arcpy.env.qualifiedFieldNames = False
    # * deleting the ImageField because joined tables can't be exported if both tables have Raster Field
    deleteFieldOfAll( featureClasses,imageFieldName ) 
    imgSaveRoot = r"C:\Users\Diwas\Desktop\TempFolderForImages"     
    if not os.path.isdir( imgSaveRoot ):
        os.mkdir( imgSaveRoot )
    # looping through all fcs
    try:
        for fc in featureClasses:
            # getting dict with key of photoname and value of path
            srcPhotoPathDict = filterPhotoPathsForLayer(allPhotosFullPaths, fc)
            imageDirectory = os.path.join(imgSaveRoot, fc)
            if not os.path.isdir( imageDirectory ):
                os.mkdir(imageDirectory)
            for name, fullpath in srcPhotoPathDict.iteritems():
                resizeAndSavePhoto(fullpath, name, imageDirectory, imgResizeFactor)
            print fc, "photos saved in folder!"

            # creating raster catalog
            rasterCatalog = fc + "_RC"
            makeRasterCatalog(fc,rasterCatalog, rc_workspace, imageDirectory)
            print "Raster Catalog for",fc,"Saved!"
            # join and save the joined layer
            joinWithCatalogAndSave( fc_workspace, fc, rc_workspace, rasterCatalog, outWorkspace)
            print fc, "Joined layer exported!"
            print "======================================================"
    except Exception as e:
        traceback.print_exc()
        print "Process wasn't successful"
    else:
        print "\nAll Done!!!"
    finally:
        shutil.rmtree( imgSaveRoot )
        arcpy.env.workspace = arcpy.env.scratchGDB
        [ arcpy.Delete_management( table ) for table in arcpy.ListTables() ]
        
