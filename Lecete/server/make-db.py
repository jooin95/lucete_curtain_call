import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")  # 이곳은 보통 똑같음 IP add

mydb = myclient["lucete"]
mycol2 = mydb["user_Alarm"]

dic = {
    '_id': 0,
    'time': 0,
    'power': 0
}

mycol2.insert_one(dic)
