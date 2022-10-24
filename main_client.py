import geocoder
import pymongo

g = geocoder.ip('me')
print(g.latlng)


myclient = pymongo.MongoClient("mongodb+srv://hakimimouad:admin@cluster0.mobs5qu.mongodb.net/test")
mydb = myclient["vls"]
mycol = mydb["stations"]

for x in mycol.find():
  print(x)