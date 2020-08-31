from django.shortcuts import render
import socket
from _thread import *
import threading
import pymongo
from scipy.spatial import distance
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus
import urllib
from time import sleep

HOST = '127.0.0.1'
PORT = 8080
Lock1 = threading.Lock()
# 접속한 클라이언트마다 새로운 쓰레드가 생성되어 통신을 하게 됩니다.
myclient = pymongo.MongoClient("mongodb://localhost:27017/")  # 이곳은 보통 똑같음 IP add
mydb = myclient["lucete"]
user_col = mydb["userID"]
mycol1 = mydb["KR_city"]
mycol2 = mydb["KR_weather"]
weather_col = mydb["KR_weather"]
connect_col = mydb["connectID"]
user_Alarm = mydb["user_Alarm"]
# def get_weather(lat, lng):

# 연결되어 있는 디바이스
connect_device = []
time_now = datetime.datetime.now()
global server_flag
server_flag = True

url2 = 'http://api.openweathermap.org/data/2.5/weather'

# 올리고 내리고 메제시 전송
def move_message(_id, value, mode):
    print(_id)
    # connect 되어 있는지 확인
    check = False
    for item2 in connect_device:
        print(item2)
        if item2['_id'] == _id:
            device_info = item2['socket']
            check = True

    # define 되어 있는 값들
    if check:
        if mode:
            if value:
                message = "SERVER RECEIVE:CONTINUOUS UP ~"
            else:
                message = "SERVER RECEIVE:CONTINUOUS DOWN ~"
            device_info.send(message.encode('utf-8'))
        else:
            if value:
                message = "SERVER RECEIVE:ONCE UP ~"
            else:
                message = "SERVER RECEIVE:ONCE DOWN ~"
            device_info.send(message.encode('utf-8'))
    # else:
    #     device_info.send("Disconnected HW".encode('utf-8'))


# 절전 모드 메세지 전송
def power_message(_id, power, client):
    print(_id)
    # connect 되어 있는지 확인
    check = False
    for item2 in connect_device:
        print(item2)
        if item2['_id'] == _id:
            device_info = item2['socket']
            check = True

    # define 되어 있는 값들
    print(check)
    if check:
        if power:
            message = "SERVER RECEIVE:POWER ON ~"
        else:
            message = "SERVER RECEIVE:POWER OFF ~"
        device_info.send(message.encode('utf-8'))
    else:
        client.send("Disconnected HW".encode('utf-8'))


# 방범 모드 메세지 전송
def protection_message(_id, period):
    print(_id)
    # connect 되어 있는지 확인
    check = False
    for item2 in connect_device:
        print(item2)
        if item2['_id'] == _id:
            device_info = item2['socket']
            check = True

    # define 되어 있는 값들
    print(check)
    if check:
        if 30 < period:
            message = "SERVER RECEIVE:PROTECTION " + str(period) + " ~"
        else:
            message = "SERVER RECEIVE:PROTECTION OFF"
        device_info.send(message.encode('utf-8'))
    else:
        device_info.send("Disconnected HW".encode('utf-8'))


# 현재시간과 알람시간을 비교하여 알려줌
def check_time(_id):
    print("check_time :", repr(time_now))
    item = user_Alarm.find_one({'_id': _id})
    now_minute = time_now.hour*60 + time_now.minute
    # 00시에 알람 초기화 그 후에 알람 시간을 체크해서 메세지 전송
    if item['power'] == 0:
        # 알람 시간 체크
        if 0 < item['time'] - now_minute:
            # 올림
            move_message(_id, True, False)
            user_Alarm.update_one({'_id': _id}, {
                '$set': {
                    'power': 1
                }
            })
        # 알람 시간이 아닐 때
        else:
            # 에너지 모드 자동 실행
            energy_mode(_id)
    else:
        # 혹시모를 시간에 10분까지 체크 후 power 초기화
        if 10 < now_minute:
            user_Alarm.update_one({'_id': _id}, {
                '$set': {
                    'power': 0
                }
            })
        # 에너지 모드 자동 실행
        energy_mode(_id)


# 온도에 따른 에너지 효율
def energy_mode(_id):
    print("energy_mode :", repr(_id))
    # 냉방 18-20도 난방 24-26도 default
    user = user_col.find_one({'_id': _id})
    weather = weather_col.find_one(({'_id': user['City_id']}))
    if weather['data']['temp'] >= 18:
        # 여름일 경우
        if 9 > time_now.month > 5:
            print('여름')
            # 내림
            move_message(_id, False, False)
        # 에너지 절약을 위한 실내 실외 온도 비교
        if weather['data']['temp'] > user['Temp']:
            if weather['data']['temp'] - user['Temp'] > 3:
                print(' 내림 ')
                # 내림
                move_message(_id, False, False)
        else:
            if user['Temp'] - weather['data']['temp'] > 3:
                # 올림
                print(' 올림 ')
                move_message(_id, True, False)
    elif weather['data']['temp'] < 18:
        if time_now.month < 3 or time_now.month > 11:
            # 올림
            print('겨울')
            move_message(_id, True, False)
        # 에너지 절약을 위한 실내 실외 온도 비교
        if weather['data']['temp'] > user['Temp']:
            if weather['data']['temp'] - user['Temp'] > 3:
                print(' 내림 ')
                # 내림
                move_message(_id, False, False)
        else:
            if user['Temp'] - weather['data']['temp'] > 3:
                # 올림
                print(' 올림 ')
                move_message(_id, True, False)


# 조도에 따른 값
def landscape_mode(_id):
    user = user_col.find_one({'_id': _id})
    print("landscape_mode ")
    # 빛에 민감할 경우
    if user['Lx_mode'] == 1:
        print('Lx_mode 1')
        # lux 값이 0 ~ 500 사이
        maximum = 500
        if user['Lx'] > maximum:
            # 계속 상태가 지속되었음
            if user['Lx_flag'] == 1:
                # 내림
                move_message(_id, False, False)

            # 그렇지 않으면 플래그를 세워줌
            else:
                user_col.update_one({'_id': _id}, {
                    '$set': {
                        'Lx_flag': 1
                    }
                })
                # 조경모드 조건 완성 -> 커튼 쳐야함
        else:
            if user['Lx_flag'] == 4:
                # 올림
                move_message(_id, True, False)
            # 그렇지 않으면 플래그를 세워줌
            else:
                user_col.update_one({'_id': _id}, {
                    '$set': {
                        'Lx_flag': 4
                    }
                })

    # 보통의 경우
    elif user['Lx_mode'] == 2:
        print('Lx_mode 2')
        # lux 값이 0 ~ 5000 사이
        maximum = 5000
        # 범위 초과시
        if user['Lx'] > maximum:
            # 계속 상태가 지속되었음
            if user['Lx_flag'] == 2:
                # 내림
                move_message(_id, False, False)
            # 그렇지 않으면 플래그를 세워줌
            else:
                user_col.update_one({'_id': _id}, {
                    '$set': {
                        'Lx_flag': 2
                    }
                })
        # 조경모드 조건 완성 -> 커튼 쳐야함
        else:
            if user['Lx_flag'] == 4:
                # 올림
                move_message(_id, True, False)
            # 그렇지 않으면 플래그를 세워줌
            else:
                user_col.update_one({'_id': _id}, {
                    '$set': {
                        'Lx_flag': 4
                    }
                })

    # 빛에 둔감할 경우
    elif user['Lx_mode'] == 3:
        print('Lx_mode 3')
        # lux 값이 0 ~ 20000 사이
        maximum = 20000
        if user['Lx'] > maximum:
            # 계속 상태가 지속되었음
            if user['Lx_flag'] == 3:
                # 내림
                move_message(_id, False, False)

            # 그렇지 않으면 플래그를 세워줌
            else:
                user_col.update_one({'_id': _id}, {
                    '$set': {
                        'Lx_flag': 3
                    }
                })
        # 조경모드 조건 완성 -> 커튼 쳐야함
        else:
            if user['Lx_flag'] == 4:
                # 올림
                move_message(_id, True, False)
            # 그렇지 않으면 플래그를 세워줌
            else:
                user_col.update_one({'_id': _id}, {
                    '$set': {
                        'Lx_flag': 4
                    }
                })


# 모드에 따라 나뉘어줌
def check_mode(_id):
    # 아직 sunset sunrise 포함하지 못했음
    user = user_col.find_one({'_id': _id})
    # weather = weather_col.find_one(({'_id': user['City_id']}))
    if user == 0:
        print("user not exist")
    else:
        print(user['Mode'])
        # 에너지 절약 모드
        if user['Mode'] == 1:
            energy_mode(_id)
        # 조경 모드
        elif user['Mode'] == 2:
            landscape_mode(_id)
            # print(datetime.datetime.now().isoformat(timespec='seconds'))
        # 방범 모드 - 주기 전송
        elif user['Mode'] == 3:
            protection_message(_id, user['time_period'])
        # 알람모드 - 선 알람 후 에너지 절약 모드
        elif user['Mode'] == 4:
            check_time(_id)
            print("Mode 4")


# 소켓에 들어갈 함수
def threaded(client_socket, addr):
    print('Connected by :', addr[0], ':', addr[1])

    # 클라이언트가 접속을 끊을 때 까지 반복.
    while True:
        try:
            # 데이터가 수신되면 클라이언트에 다시 전송합니다.(에코)
            data = client_socket.recv(1024)
            if not data:
                print('Disconnected by ' + addr[0], ':', addr[1])
                break
            # print('Received from ' + addr[0], ':', addr[1], data.decode())
            # 새로운 클라이언트의 접속
            device = {
                '_id': '',
                'socket': client_socket,
                'ip': addr[0],
                'port': addr[1]
            }
            data_list = data.decode().split(' ')
            # 하드웨어와 통신 시작
            try:
                if data_list[0] == "HW":
                    # MKID 일 때 실행 코드
                    check = False
                    if data_list[1] == "MKID":

                        # Dead Lock 방지
                        Lock1.acquire()
                        # 이곳에서 디비에 추가
                        not_overlap = True
                        data_list[2] = int(data_list[2])
                        # 연결되어 있는 HW 중에 중복이 되어 있는지 확인
                        for check_overlap in connect_device:
                            if check_overlap['_id'] == data_list[2]:
                                client_socket.send("user_id overlap".encode('utf-8'))
                                not_overlap = False
                                break
                        if not_overlap:
                            # 현재 위치
                            location = (float(data_list[3]), float(data_list[4]))
                            dst = -1
                            # 위도와 경도를 내 디비에 있는 도시들과 비교하여 가장 가까운 도시를 집어 넣음
                            for item2 in weather_col.find():
                                loc = (float(item2['location']['lat']), float(item2['location']['lon']))
                                # 위도 경도 최소값 구함
                                if dst < 0:
                                    dst = distance.euclidean(loc, location)
                                elif dst > distance.euclidean(loc, location):
                                    dst = distance.euclidean(loc, location)
                                    city_id = item2['_id']
                            device['_id'] = data_list[2]
                            dic = {
                                '_id': data_list[2],
                                'City_id': city_id,
                                'Power': 1,
                                'Mode': 0,
                                'State': data_list[5],
                                'Lx': 0.0,
                                'Temp': 0.0,
                                'time_period': 60,
                                'time': 0
                            }
                            user_col.insert_one(dic)
                            connect_device.append(device)
                            # print(connect_device)
                            # connect_col.insert_one(device)
                            client_socket.send("MK_ID Success".encode('utf-8'))
                        # Dead Lock 방지 해제
                        Lock1.release()
                    # 기존의 클라이언트 유저가 정보를 보내옴
                    elif data_list[1] == "SET":
                        # print(connect_device)
                        Lock1.acquire()
                        data_list[2] = int(data_list[2])
                        for item in connect_device:
                            if item['_id'] == data_list[2]:
                                check = True
                                break
                        if check:
                            print("SET VALUE")
                            location = (float(data_list[3]), float(data_list[4]))
                            dst = -1
                            # 위도와 경도를 내 디비에 있는 도시들과 비교하여 가장 가까운 도시를 집어 넣음
                            for item2 in weather_col.find():
                                loc = (float(item2['location']['lat']), float(item2['location']['lon']))
                                # 위도 경도 최소값 구함
                                if dst < 0:
                                    dst = distance.euclidean(loc, location)
                                elif dst > distance.euclidean(loc, location):
                                    dst = distance.euclidean(loc, location)
                                    city_id = item2['_id']
                            user_col.update_one({'_id': data_list[2]}, {
                                "$set": {
                                    "City_id": city_id,
                                    "State": float(data_list[5])
                                }})
                            client_socket.send("SET Success".encode('utf-8'))
                        else:
                            location = (float(data_list[3]), float(data_list[4]))
                            dst = -1
                            # 위도와 경도를 내 디비에 있는 도시들과 비교하여 가장 가까운 도시를 집어 넣음
                            for item2 in weather_col.find():
                                loc = (float(item2['location']['lat']), float(item2['location']['lon']))
                                # 위도 경도 최소값 구함
                                if dst < 0:
                                    dst = distance.euclidean(loc, location)
                                elif dst > distance.euclidean(loc, location):
                                    dst = distance.euclidean(loc, location)
                                    city_id = item2['_id']

                            dic = {
                                '_id': data_list[2],
                                'City_id': city_id,
                                'Power': 1,
                                'Mode': 0,
                                'State': float(data_list[5]),
                                'Lx': 0.0,
                                'Temp': 0.0,
                                'time_period': 3,
                                'time': 0
                            }
                            user_col.insert_one(dic)
                            connect_device.append(device)
                            client_socket.send("SET MK_ID Success".encode('utf-8'))
                            # connect_col.insert_one(device)
                        Lock1.release()
                    # 현재 아두이노에서 가지고 있는 값을 갱신해주기 위ㅡ하여 보내주는 값 CR
                    elif data_list[1] == "CR":
                        # 연결되어 있는 디바이스 확인
                        data_list[2] = int(data_list[2])
                        for item in connect_device:
                            if item['_id'] == data_list[2]:
                                check = True
                                break
                        # 디바이스에 있으면 업데이트 해줌
                        if check:
                            user_col.update_one({'_id': data_list[2]}, {
                                "$set": {
                                    "State": float(data_list[3]),
                                    "Lx": float(data_list[4]),
                                    "Temp": float(data_list[5]),
                                    "Power": int(data_list[6])
                                }})
                        # 에너지 절절모드 OR 조경모드일때 메세지 보내야 함
                        client_socket.send("CR Success".encode('utf-8'))
                    else:
                        client_socket.send("HW error : code 8".encode('utf-8'))

                # 앱하고 통신
                elif data_list[0] == "APP":
                    print("APP _id :", data_list[1])
                    data_list[1] = int(data_list[1])
                    user_data = user_col.find_one({'_id': data_list[1]})
                    if user_data == 0:
                        client_socket.send("_id value is Not valuable".encode('utf-8'))
                    else:
                        # 전원이 꺼져있는 것
                        print("APP Connect")
                        data_list[2] = int(data_list[2])
                        data_list[3] = int(data_list[3])
                        if data_list[2] != user_data['Power']:
                            # 메세지 전송
                            if data_list[2] == 0:
                                power_message(data_list[1], False, client_socket)
                            # 전원을 킴
                            elif data_list[2] == 1:
                                power_message(data_list[1], True, client_socket)
                        # 알람 모드
                        if data_list[3] == 3:
                            time = data_list[4].split(':')
                            hour = int(time[0])
                            minute = int(time[1])
                            user_col.update_one({'_id': data_list[1]}, {
                                                '$set': {
                                                    'Power': data_list[2],
                                                    'Mode': data_list[3],
                                                    'time_period': hour*60 + minute
                                                    }
                                                }, upsert=True
                                                )
                        # 방범 모드
                        elif data_list[3] == 4:
                            # 주기를 계산
                            time = data_list[4].split(':')
                            hour = int(time[0])
                            minute = int(time[1])
                            # 디비에 업로드
                            user_col.update_one({'_id': data_list[1]}, {
                                                '$set': {
                                                    'Power': data_list[2],
                                                    'Mode': data_list[3],
                                                    'time': hour*60 + minute
                                                    }
                                                }, upsert=True
                                                )
                            # 디비에 알람시간을 저장한 후에 더 빠르게 검색 후 메시지 전송
                            user_Alarm.update_one({'_id': data_list[1]}, {
                                '$set': {
                                    '_id': data_list[1],
                                    'time': hour*60 + minute,
                                    'power': 0
                                }
                            }, upsert=True)

                        # 사용자 설정 모드
                        elif data_list[3] == 5:
                            if data_list[4] == 1:
                                move_message(data_list[1], True, True)
                            else:
                                move_message(data_list[1], False, True)

                        # 조경 모드
                        elif data_list[3] == 2:
                            user_col.update_one({'_id': data_list[1]}, {
                                '$set': {
                                    'Power': data_list[2],
                                    'Mode': data_list[3],
                                    'Lx_mode': data_list[4],
                                }
                            }, upsert=True
                                                )
                        # 초기 모드, 에너지 효율 모드
                        else:
                            user_col.update_one({'_id': data_list[1]}, {
                                                '$set': {
                                                    'Power': data_list[2],
                                                    'Mode': data_list[3],
                                                    }
                                                }, upsert=True
                                                )
                            # 후에 데이터를 아두이노에 보내는 함수 필요
                        # 모드 체크 함수 호출
                        check_mode(data_list[1])
                        print("3")
                        # for item in connect_device:
                        #     if item['_id'] == int(data_list[1]):
                        #         item['socket'].send(" socket message ".encode('utf-8'))
                elif data_list[0] == "test":
                    check_time(data_list[1])
                else:
                    client_socket.send("APP error : code 8".encode('utf-8'))
            except ConnectionResetError as e:
                print('Error :' + addr[0], ':', addr[1], ' :', e)
                client_socket.send("Error :".encode('utf-8'))
        except ConnectionResetError as e:
            print('Disconnected by ' + addr[0], ':', addr[1], ' :', e)
            # 연결 끊겼을 때 connect_device 에서 remove

            break
    client_socket.close()

@csrf_exempt
def start_server(request):
    global server_flag
    server_flag = True
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print('server start', request)

    # 클라이언트가 접속하면 accept 함수에서 새로운 소켓을 리턴.

    # 새로운 쓰레드에서 해당 소켓을 사용하여 통신.
    while server_flag:
        print('wait')

        client_socket, addr = server_socket.accept()
        start_new_thread(threaded, (client_socket, addr))
    server_socket.close()
    data = "server destroy"
    return JsonResponse({"data": data})

@csrf_exempt
def stop_server(request):
    global server_flag
    print(server_flag)
    server_flag = False
    data = "server finish"
    return JsonResponse({"data": data})


@csrf_exempt
def weather_upload(request):
    count = 0
    cityID_list = []
    myquery = [
        {"$sort": {"_id": 1}}
    ]
    for item in mycol1.aggregate(myquery):
        cityID_list.append(item['_id'])
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
            mycol2.replace_one({'_id': item}, {"name": response_body['name'],
                                               'location': response_body['coord'], 'data': data})
            count = count + 1
            if count == 20:
                count = 0
                # break
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
            mycol2.replace_one({'_id': item}, {"name": response_body['name'],
                                               'location': response_body['coord'], 'data': data})
            count = count + 1
            if count == 50:
                count = 0
                sleep(60)
    data = "upload finish"
    return JsonResponse({"data": data})


def index(request):
    return render(request, "vis/beta.html")
