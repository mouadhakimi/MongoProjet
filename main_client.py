import geocoder
import pymongo

#g = geocoder.ip('me')


myclient = pymongo.MongoClient("mongodb+srv://hakimimouad:admin@cluster0.mobs5qu.mongodb.net/test")
mydb = myclient["vls"]
mycol = mydb["stations"]

x = 50.634940
y = 3.046680

#x = g.lat
#y = g.lng


mycolcursor = mydb.stations.find({},{ "_id": 1, "name": 1, "geometry.coordinates": 1 })

mycolcursor_2 = mydb.datas.find({},{"_id":0,"station_id":1, "bike_availbale":1,"stand_availbale":1})


for i,j in zip(mycolcursor,mycolcursor_2):
    z = i.get("geometry")
    w = z.get("coordinates")
    if(w[0]<y+0.003 and w[0]>y-0.003):
        if(w[1]<x+0.003 and w[1]>x-0.003):
            if(i.get("_id") == j.get("station_id")):
                velo = j.get("bike_availbale")
                stand = j.get("stand_availbale")
                print("Une des stations les plus proches est: "+i.get("name")+ " avec "+str(velo)+" velos disponibles et "+str(stand)+" places disponibles")
                

