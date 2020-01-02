import arcpy

print("Imports Done!!\n")
way_points = r"C:\Users\PATHWAY\Desktop\Mugu Trails\all_waypoints\{AddNameFileNameHere}.shp"
arcpy.MakeFeatureLayer_management(way_points, 'waypts_layer')

# category wise keywords to include at 0 index and to exclude at 1 index
category_keywords = {
    "Education Infrastructure"  : [["school","library","boarding","campus","pra vi"],["jane bato","way to","jaane"]],
    "Obstacles/ Natural Hazards": [["paheero","risk","pohiro","pairo","slide", "land slade", "obstacle","erosion","pahiro","risky","no bridge","danger","damage", "danjar","no trail","rock fall"],["damage tap"]],
    "Geographic Features"       : [["bagar","stream","forest","river","khola"],["way to", "bridge","dhunga","pul"]],
    "Health Amenity"            : [["health","swasthye sakha","helth post","hospital","pharmacy","birth","medical"],[]],
    "Trail"                     : [["trail","steps","road","footway","motorway"," way","bato","secondary","tertiary"],["paheero","pairo","slide", "land slade", "obstacle","erosion","pahiro","risk","no bridge","danger","damage", "danjar","no trail","rock fall"]],
    "Business Centers"          : [["bazar", "bazaar","bazzar"],[]],
    "Settlements"               : [["village","vlage","gauu","gaau","house","gaun"],["way to","trail","near ","birth","palika","jaane"]],
    "River Crossings"           : [["bridge","kathe pul","wooden strips","dhunga ko pul"],["no bridge"]],
    "Utility Infrastructure"    : [["dharo","post box","pani ghatta","ghatta", "mill","reservoir","tower","tank","hotal","chorten","chhorten","gumpa","stupa","gumba","phone","restaurant","water","cinema","shop","temple","tample","worship","hotel"],["jaane bato"]],
    "Financial Institution"     : [["bank","finance"],[]],
    "Public Buildings"          : [["police","surveillance","jail","armi post","barak","army","office","court","sansthan","red cross","samiti"],["health"]],
    "Trail Junction"            : [["dobato",],["school"]],
    "Community Space"           : [["bus stop","chautara","allotment","shelter","cemetery","park","camp site","hostel","monument","farm","oppen space","open space","ground"],[]]
    }


def KeywordIsInDescription( keywords,description ):
    return any( keyword in description for keyword in keywords )

def GetCategory( description ):
    description = description.lower()
    for category in category_keywords.keys():
        kw_to_include = category_keywords[category][0]
        kw_to_exclude = category_keywords[category][1]
        if KeywordIsInDescription( kw_to_include,description ) and not KeywordIsInDescription( kw_to_exclude,description ):
            print (category,description)
            return category
    return ""
    
count = {}
with arcpy.da.UpdateCursor( 'waypts_layer',["desc_","category"] ) as cursor:
    for row in cursor:
        # getting description and assgining and counting category
        category = GetCategory( row[0] )
        count[ category ] = count.get( category,0 ) + 1
        #updating row
        row[1] = category
        cursor.updateRow( row )
        
for key in count:
    print key,":", count[key]

print "Categories Assigned To", sum( count.values() ) - count[""], "records"

