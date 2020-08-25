import json
import pymongo
import datetime
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus
import urllib
from time import sleep

myclient = pymongo.MongoClient("mongodb://localhost:27017/")  # 이곳은 보통 똑같음 IP add
mydb = myclient["lucete"]
mycol1 = mydb['KR_city']
mycol2 = mydb["KR_weather"]

url2 = 'http://api.openweathermap.org/data/2.5/weather'

# url = 'http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList'
# queryParams = '?ServiceKey=vlwAV7Pgf8uaV0N8PdxeIK6z3%2Bw1JSj4Qr6x5qM1Yh1Fk5FfTUFwdPuyQcTSw%2FID3Pd7WKX8DSV8JCk9r8g0QQ%3D%3D&' + \
#               urlencode({
#                          quote_plus('pageNo'): '1', quote_plus('numOfRows'): '10',
#                          quote_plus('dataType'): 'JSON', quote_plus('dataCd'): 'ASOS',
#                          quote_plus('dateCd'): 'HR', quote_plus('startDt'): '20100101',
#                          quote_plus('startHh'): '01', quote_plus('endDt'): '20100601',
#                          quote_plus('endHh'): '01', quote_plus('stnIds'): '131',
#                          quote_plus('schListCnt'): '10'
#               })
# request = urllib.request.Request(url + queryParams)
# request.get_method = lambda: 'GET'
# response_body = urlopen(request).read()

# 1분에 60번 이상 검색 하지 못하게 함
count = 0
cityID_list = []
myquery = [
    {"$sort": {"_id": 1}}
]
for item in mycol1.aggregate(myquery):
    cityID_list.append(item['_id'])

myquery2 = [
    {"$match": {"country": "KR"}}
]

city_list = []
for item in cityID_list:
    try:
        print(item)
        queryParams2 = '?' + urlencode({
            quote_plus('id'): item, quote_plus('appid'): '008f6aadc0e813803c68f1a1e5dedf12'
        })
        request = urllib.request.Request(url2 + queryParams2)
        request.get_method = lambda: 'GET'
        response_body = urllib.request.urlopen(request).read()
        # response_body = response_body.replace("'", "\"")
        response_body = json.loads(response_body)
        data = {
            'temp': round(response_body['main']['temp'] - 273, 2),
            'date': datetime.datetime.fromtimestamp(response_body['dt']),
            'sunset': datetime.datetime.fromtimestamp(response_body['sys']['sunset']),
            'sunrise': datetime.datetime.fromtimestamp(response_body['sys']['sunrise']),
            'weather': response_body['weather'],
            'cloud': response_body['clouds']['all']
        }
        dic = {
            '_id': item,
            'name': response_body['name'],
            'location':  response_body['coord'],
            'data': data
        }
        # city_list.append(dic)
        mycol2.replace_one({'_id': item}, {"name": response_body['name'],
                                           'location':  response_body['coord'], 'data': data})
        count = count + 1
        if count == 20:
            count = 0
            #break
            sleep(60)

    except Exception as ex:
        print(ex)
        queryParams2 = '?' + urlencode({
            quote_plus('id'): item, quote_plus('appid'): '008f6aadc0e813803c68f1a1e5dedf12'
        })
        request = urllib.request.Request(url2 + queryParams2)
        request.get_method = lambda: 'GET'
        response_body = urllib.request.urlopen(request).read()
        # response_body = response_body.replace("'", "\"")
        response_body = json.loads(response_body)
        data = {
            'temp': round(response_body['main']['temp'] - 273, 2),
            'date': datetime.datetime.fromtimestamp(response_body['dt']),
            'sunset': datetime.datetime.fromtimestamp(response_body['sys']['sunset']),
            'sunrise': datetime.datetime.fromtimestamp(response_body['sys']['sunrise']),
            'weather': response_body['weather'],
            'cloud': response_body['clouds']['all']
        }
        dic = {
            '_id': item,
            'name': response_body['name'],
            'location': response_body['coord'],
            'data': data
        }
        # city_list.append(dic)
        mycol2.replace_one({'_id': item}, {"name": response_body['name'],
                                           'location': response_body['coord'], 'data': data})
        count = count + 1
        if count == 50:
            count = 0
            sleep(60)


