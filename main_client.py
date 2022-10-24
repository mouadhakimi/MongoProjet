import geocoder
import pymongo

g = geocoder.ip('me')
print(g.latlng)


myclient = pymongo.MongoClient("mongodb+srv://hakimimouad:admin@cluster0.mobs5qu.mongodb.net/test")
mydb = myclient["vls"]
mycol = mydb["stations"]

x = 50.634178
y = 3.048710


mycolcursor = mydb.stations.find({},{ "_id": 0, "name": 1, "geometry.coordinates": 1 })

for i in mycolcursor:
  z = i.get("geometry")
  w = z.get("coordinates")
  if(w[0]<y+0.003 and w[0]>y-0.003):
      if(w[1]<x+0.003 and w[1]>x-0.003):
          print(i)

