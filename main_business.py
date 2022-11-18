import requests
import json
from pprint import pprint
from pymongo import MongoClient, DESCENDING
import dateutil.parser
import re

client = MongoClient(
    'mongodb+srv://hakimimouad:admin@cluster0.mobs5qu.mongodb.net/test')
db = client["vls"] 
collection_vlilles = db["vlilles"]
collection_stations = db["stations"]

# find a station from a partial name


def find_station(name_partial: str):
    requete = {"name": re.compile(
        name_partial, re.IGNORECASE), "city": re.compile("Lille", re.IGNORECASE)}
    cursor = collection_stations.find(requete)
    print("{} stations match".format(
        collection_stations.count_documents(requete)))
    l: list = []
    for i in cursor:
        l.append(i)
    return l


# loop over asking for a value bewteen range
def input_range(min: int = 1, max: int = 5) -> int:
    while True:
        try:
            choix = input("choice [{},{}]:".format(min, max))
            choix = int(choix)
            if min <= choix <= max:
                return choix
        except:
            pass

# choose an item from a list


def input_list(liste: list) -> int:
    if len(liste) == 0:
        return -1
    if len(liste) == 1:
        input()
        return 0
    return input_range(0, len(liste)-1)


print("""
Choose one:
    1. find station with name (with some letters)
    2. update a stations
    3. delete a station and datas
    4. deactivate all station in an area
    5. give all stations with a ratio bike/total_stand under 20'%' between 18h and 19h00 (monday to friday)
""")

# Testing the input of the user
choix: int = input_range()

# choosing the options
if 1 <= choix <= 3:

    for x in collection_stations.find():
        print(x)
    station_name = input("station name :")
    list_stations = find_station(station_name)
    for station in list_stations:
        pprint(station)
    if 2 <= choix <= 3:
        # choose a station to edit or delete
        print("\n\nchoose a station")
        [print("    " + str(indice) + " : " + value["name"])
         for indice, value in enumerate(list_stations)]
        station_to_edit: int = input_list(list_stations)
        if station_to_edit == -1:
            exit("no station found")
        station_to_edit: dict = list_stations[station_to_edit]
        
        if choix == 2 :
            print("\n\nGo for editing station {}".format(station_to_edit))
            pprint(station_to_edit)
            # Choose the field to edit
            [print("    " + str(key) + " : " + value + " : " + str(station_to_edit[value]))
            for key, value in enumerate(list(station_to_edit.keys())[1:])]
            print("\nfield to edit :")
            field_to_edit: int = input_list(list(station_to_edit.keys())[
                                            1:])  # 1: to avoid editing _id
            field_to_edit: str = list(station_to_edit.keys())[1:][field_to_edit]
            print("\n\nGo for editing field {}".format(field_to_edit))
            # edit the field and update the db
            value = input("new value of the field :")
            # DB update
            collection_stations.update_one({"_id": station_to_edit["_id"]}, {
                                        "$set": {field_to_edit: value}})

        if choix == 3 :
            # Deleting the station
            # First clean data
            collection_vlilles.delete_many({"name": station_to_edit["name"]})

            # Clean station
            collection_stations.delete_one(station_to_edit)

elif choix == 4:

    print("deavtivate")
    

if choix == 5:
    # give all stations with a ratio bike/total_stand under 20% between 18h and 19h00 (between two aribtrary dates)
    liste_staion = collection_vlilles.aggregate([
        {"$match":{"status": True}},  # only look for the working stations
        {"$sort": {"record_timestamp": DESCENDING}}, # sort by date 
        {"$match":{    # time window to match 
            "$or": [  # hardcoded time of two days because the worker did not work for ever
                { "$and" : [ { "record_timestamp" : { "$lte" : dateutil.parser.parse("2020-10-12 17:05:16.683Z")}} ,
                        { "record_timestamp" : { "$gte" : dateutil.parser.parse("2020-10-12 17:02:16.263Z")}} ]
                },{
                "$and" : [ { "record_timestamp" : { "$lte" : dateutil.parser.parse("2020-10-12 17:01:16.683Z")}} ,
                        { "record_timestamp" : { "$gte" : dateutil.parser.parse("2020-10-12 16:56:00.263Z")}} ]
                }
                ]
        }},
        {"$project":  # Calculate the total of places can be done with an index I think but meh where is the fun
            {"_id":"$_id",
            "name": "$name",
                "total":{ "$add": ["$vlilles_dispo", "$places_dispo"]} , 
                "places_dispo" : "$places_dispo",
                "vlilles_dispo" : "$vlilles_dispo",
                "record_timestamp" : "$record_timestamp"
    }},
    {"$match":{"total": {"$gt": 0} }} , # avoid to get station with no total (cause blackhole later in the code /0)  
    {"$project": # calculate the percentage of bickes
            {"_id": "$_id", 
                "name": "$name", 
                "total": "$total", 
                "places_dispo" : "$places_dispo",
                "vlilles_dispo" : "$vlilles_dispo",  
                "percent" : {"$divide": [ "$vlilles_dispo" , "$total" ]},
                "record_timestamp" : "$record_timestamp"
    }},
    {"$match":{"percent": {"$lte": 0.2} }}, # Look for the 20%
    {"$group":  # we groupe by station name in order to extract it and the time where it was at 20%
            {"_id":"$name",
            "entries" : {"$push" : {
                "percent": "$percent",
                "places_dispo" : "$places_dispo",
                "vlilles_dispo" : "$vlilles_dispo",
                "record_timestamp" : "$record_timestamp"}
    }}},
    {"$project": # only get the _id because it's the station name that match all the previous
        { "_id":1 }},
    ])
    for station in liste_staion:
        print(station["_id"])
else:
    pass
