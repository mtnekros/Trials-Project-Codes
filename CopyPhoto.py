import os
import arcpy
import shutil
print "imports done"

# extracting photo names from
all_photos_folder_path = r"C:\Users\PATHWAY\Desktop\Mugu Trails\all_photos"

all_photos_names = []
for root, dirs, filenames in os.walk(all_photos_folder_path):
    filenames = filter(lambda f: f.endswith('.jpg'), filenames)
    for filename in filenames:
        all_photos_names.append(os.path.join(root, filename))
print "filenames done,", len(all_photos_names), "Total!"

# setting workspace & getting feature classes
workspace = input("Enter the dataset's path: ")
arcpy.env.workspace = workspace


# making feature layer
layer_name = input("Enter the layer's complete path: ")
arcpy.MakeFeatureLayer_management(layer_name, 'layer')
print "making feature layer done"


def get_complete_photo_path(photo_name):
    if len(photo_name.strip()) == 0:
        return None
    for complete_photo_name in iter(all_photos_names):
        if complete_photo_name.endswith(photo_name):
            return complete_photo_name
    return None


count_of_photos = {}

# counting and copying photos for the layer to destination
destination = r"C:\Users\PATHWAY\Desktop\Mugu Trails\Categorized Photos\Settlement Photos"
print "counting copying started"
with arcpy.da.SearchCursor('layer', ['Photo']) as cursor:
    for row in cursor:
        photo_name = row[0].strip()
        complete_photo_path = get_complete_photo_path(photo_name)
        if complete_photo_path is not None:
            shutil.copyfile(complete_photo_path,
                            os.path.join(destination, photo_name))
        # for counting purposes only
        count_of_photos[photo_name] = count_of_photos.get(photo_name, 0) + 1
print "couting copying completed\n"

print "Photos with multiple counts are: "
for photo, count in count_of_photos.items():
    if count > 1:
        print "Name:", photo, "Count:", count
print ""
