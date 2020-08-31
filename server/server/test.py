import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")  # 이곳은 보통 똑같음 IP add

mydb = myclient["lucete"]
mycol2 = mydb["userID"]

lat = 0
lng = 0
dic = {
    '_id': 0,
    'City_id': 0,
    'Power': 0,
    'Mode': 0,
    'State': 0.0,
    'Lx': 0.0,
    'Lx_flag': 0,
    'Lx_mode': 0,
    'Temp': 0.0,
    'time_period': 3,
    'time': 0,
    'flag': 0
}

mycol2.insert_one(dic)

