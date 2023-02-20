# import requests
# import re
# import time
# import datetime
# import locale
# locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
#
#
# res = []
# param = { 'drwNo':[i for i in range(1, 1055)] for i in range(1, 1055)}
# print(param)
# print(param.keys())
# print(param.values())
# param_values = list(param.values())   # 딕셔너리의 값을 리스트로 만들기
# print(param_values[0][0])
# param_values = param_values[0]
# print(param_values)  # [ [1, 2, 3, 4 ....] ]
# print(param_values[0])  # [1, 2, 3, 4, ....]
#
#
# for i in range(len(param_values)):
#     param = {'drwNo' : param_values[i]}
#     res.insert(i, requests.post(
#         'https://www.dhlottery.co.kr/gameResult.do?method=byWin', params=param))  # params는 위에서 만든 param을 넣어주기
#     text = res[i].text
#     # print(text)
#
#     p = re.compile('ball_645 lrg ball\d">(\d+)<')
#     win_num = p.findall(text)
#     print(win_num)
#
#     sidx = text.find('"desc">')
#     eidx = text.find('추첨)<', sidx)
#     # print(eidx)
#     result2 = text[sidx:eidx]
#
#     p2 = re.compile('([0-9]{4}[가-힣]{1}\s*[0-9]{2}[가-힣]{1}\s*[0-9]{2}[가-힣]{1})')
#     # drawdate = str(p2.findall(result2))
#     drawdate = "".join(map(str, p2.findall(result2)))
#     drawdate = datetime.datetime.strptime(drawdate, '%Y년 %m월 %d일')
#     # print(drawdate)


line_counter = 0
data_header = []
investigate_list = []

with open('C:/Users/erbaf/KEPCO/jupyter-notebook/jupyter-notebook-----/csv 파일 만들기.csv', 'rt', encoding='cp949') as file:
    while 1:
        data = file.readline()  # 줄바꿈 문자까지(한줄만) 내용 읽음
        if not data: break
        if line_counter == 0:
            data_header = data.split(",")
        else:
            investigate_list.append(data.split(","))
        line_counter += 1
print("Header : ", data_header)
for i in range(0, 10):
    print("data", i, ":", investigate_list[i])
