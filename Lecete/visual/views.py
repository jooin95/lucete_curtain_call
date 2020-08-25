from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import pymongo
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus
import urllib

myclient = pymongo.MongoClient("mongodb://localhost:27017/")  # 이곳은 보통 똑같음 IP add
mydb = myclient["lucete"]
mycol2 = mydb["KR_city"]

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


def index(request):
    return render(request, "vis/beta.html")


def index2(request):
    queryParams2 = '?' + urlencode({
        quote_plus('id'): 1846355, quote_plus('appid'): '008f6aadc0e813803c68f1a1e5dedf12'
    })
    request2 = urllib.request.Request(url2 + queryParams2)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request2).read()
    print(response_body)
    return render(request, "vis/main_page.html")


def index3(request):
    return render(request, "vis/explain_detail.html")


def index4(request):
    return render(request, "vis/beta.html")

@csrf_exempt
def data_insert(request):
    data_list = []
    return JsonResponse({"data_list": data_list})