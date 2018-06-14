import re
import json
import requests

url = 'http://jwxt.imu.edu.cn'
session = requests.session()
is_login = False


def getNewCookie():
    u = url + '/login'
    session.get(u)
    cookie = requests.utils.dict_from_cookiejar(session.cookies)
    while cookie['JSESSIONID'] == '':
        session.get(u)
        cookie = requests.utils.dict_from_cookiejar(session.cookies)
    return cookie


def getCurrentCookie():
    return requests.utils.dict_from_cookiejar(session.cookies)


def getToken(major_num):
    if is_login:
        sel_url = url + '/student/courseSelect/planCourse/index?fajhh=' + major_num
        sel_cookie = {
            'JSESSIONID': getCurrentCookie(),
            'selectionBar': '1293218'
        }
        r = session.get(sel_url, cookies=sel_cookie)
        temp = re.findall('value="[0-9a-z]{32}', r.text)
        while temp.__len__() == 0:
            r = session.get(sel_url, cookies=sel_cookie)
            temp = re.findall('value="[0-9a-z]{32}', r.text)
        return temp[0][7:]


def getMajorNum():
    # 16软工 : 32937
    # 15网工 :
    pass


def login(u, p):
    req = url + '/j_spring_security_check'
    print(req)
    data = {
        'j_username': u,
        'j_password': p,
        'j_captcha1': 'error'
    }
    count = 0
    while True:
        count = count + 1
        cookie = getNewCookie()
        result = session.post(req, data=data, cookies=cookie)
        if '欢迎您' in result.text:
            print("[-] Success Login")
            is_login = True
            return getCurrentCookie()
        elif '登 录' in result.text:
            return
        else:
            print(result.text)
            if count % 100 == 0:
                print('[+] ' + str(count) + ' : Failed')


def choiceLesson(Id, Name):
    if is_login:
        choice_url = url + '/student/courseSelect/planCourse/waitingfor?dealType=2'
        para = {
            'fajhh': getMajorNum(),
            'kcIds': Id + '_01_2018-2019-1-2',
            'kcms': Name + '_01',
            'sj': '0_0',
            'tokenValue': getToken()
        }
        choice = session.post(choice_url, cookies=getCurrentCookie(), data=para)


def checkResult(u):
    if is_login:
        # 查询结果
        check_url = url + '/student/courseSelect/selectResult/query'
        resu_data = {
            'kcNum': '1',
            'redisKey': u
        }
        for i in 10:
            check = session.post(check_url, cookies=getCurrentCookie(), data=resu_data)
            response = json.loads(check.content)
            print('[-] ' + response)
            if response['isFinish'] and response['result']:
                if "选课成功！" in response['result']:
                    print("[-] 选课成功！")
                    return
                else:
                    print('[-] ' + response['result'])
                    return
            else:
                print('[-] 选课失败!')
        print('[-] 排队人数较多')


username = '0151122244'
password = '**********'
# 登陆
login(username, password)
# 120120230 唐诗意境与人生情怀(A模块)
choiceLesson('120120230', '唐诗意境与人生情怀(A模块)')
checkResult(username)


