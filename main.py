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
            'JSESSIONID': getCurrentCookie()['JSESSIONID'],
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
    # 15网工 : 32871
    if not is_login:
        return '[-] Not Login!'
    req_url = url + '/student/rollManagement/rollInfo/index'
    cookie = {
        'JSESSIONID': getCurrentCookie()['JSESSIONID'],
        'selectionBar': '1183421'
    }
    major_num = re.findall('<input type="hidden" id="zx" name="zx" value="[0-9]{5}"/>',
                           session.get(req_url, cookies=cookie).text)[0][-8:-3];
    # print(major_num)
    return major_num


def login(u, p):
    req = url + '/j_spring_security_check'
    data = {
        'j_username': u,
        'j_password': p,
        'j_captcha1': 'error'
    }
    count = 0
    while True:
        count = count + 1
        cookie = {
            'JSESSIONID': getNewCookie()['JSESSIONID']
        }
        result = session.post(req, data=data, cookies=cookie)
        if '欢迎您' in result.text:
            print("[+] Success Login")
            global is_login
            is_login= True
            return getCurrentCookie()
        elif '登 录' in result.text:
            return "[-] Username Or Password Error"
        else:
            print(result.text)
            if count % 100 == 0:
                print('[-] ' + str(count) + ' : Failed')


def choiceLesson(Id, Name):
    if is_login:
        choice_url = url + '/student/courseSelect/planCourse/waitingfor?dealType=2'
        para = {
            'fajhh': getMajorNum(),
            'kcIds': Id + '_01_2018-2019-1-2',
            'kcms': Name + '_01',
            'sj': '0_0',
            'tokenValue': getToken(getMajorNum())
        }
        cookie = {
            'JSESSIONID': getNewCookie()['JSESSIONID'],
            'selectionBar': '1293218'
        }
        choice = session.post(choice_url, cookies=cookie, data=para)
    else:
        print("[-] Not login")
        return


def checkResult(u):
    if is_login:
        # 查询结果
        check_url = url + '/student/courseSelect/selectResult/query'
        resu_data = {
            'kcNum': '1',
            'redisKey': u
        }
        cookie = {
            'JSESSIONID': getNewCookie()['JSESSIONID']
        }
        print('[-] start check')
        for i in range(10):
            check = session.post(check_url, cookies=cookie, data=resu_data)
            response = json.loads(check.content)
            print('[-] ' + response)
            if response['isFinish'] and response['result']:
                if "选课成功！" in response['result']:
                    print("[+] 选课成功！")
                    return
                else:
                    print('[-] ' + response['result'])
                    return
            else:
                print('[-] 选课失败!')
        print('[-] 排队人数较多')
    else:
        print('[-] not login')


def getScore(lesson_name):
    req_url = url + '/student/integratedQuery/scoreQuery/allPassingScores/index'
    cookie = {
        'JSESSIONID': getCurrentCookie()['JSESSIONID'],
        'selectionBar': '1379870'
    }
    pass


username = '**********'
password = '**********'
# 登陆
print(login(username, password))
# 120120230 唐诗意境与人生情怀(A模块)
choiceLesson('140450470', '无线通信与网络')
choiceLesson('140451380', '网络安全技术')
choiceLesson('140451390', '物联网技术')
choiceLesson('140451400', '网络工程')


# checkResult(username)
# checkResult(username)
