import re
import json
import requests
import time

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
            is_login = True
            return True
        elif '登 录' in result.text:
            return "[-] Username Or Password Error"
        else:
            print(result.text)
            if count % 100 == 0:
                print('[-] ' + str(count) + ' : Failed')


def choiceLesson(id, Name, num):
    if is_login:
        choice_url = url + '/student/courseSelect/planCourse/waitingfor?dealType=2'
        info = getInfo(id, Name, num)
        if info == 0:
            print('[-] 未查询到结果，请检查课程号是否正确')
            return False
        para = {
            'fajhh': getMajorNum(),
            'kcIds': info['kcIds'],
            'kcms': info['kcms'],
            'sj': '0_0',
            'tokenValue': getToken(getMajorNum())
        }
        cookie = {
            'JSESSIONID': getCurrentCookie()['JSESSIONID'],
            'selectionBar': '1293218'
        }
        session.post(choice_url, cookies=cookie, data=para)
        time.sleep(0.1)
        if checkResult(id, num):
            print('[+] [' + Name + '] 选课成功！')
            return True
        else:
            print('[-] [' + Name + '] 好像没选上...')
            return False

    else:
        print("[-] Not login")
        return False


# 课程号，课程名，课序号
def getInfo(id, Name, num):
    if is_login:
        req_url = url + '/student/courseSelect/freeCourse/courseList'
        para = {
            'jc': '0',
            'kyl': '1',
            'searchtj': id,
            'xq': '0'
        }
        cookie = {
            'JSESSIONID': getCurrentCookie()['JSESSIONID'],
            'selectionBar': '1293218'
        }
        data = session.post(req_url, cookies=cookie, data=para)
        r = json.loads(data.json()['rwRxkZlList'])
        ret = {
            'kcIds': '',
            'kcms': ''
        }
        if len(r) == 0:
            return 0
        for i in r:
            if i['kkxqh'] == num:
                ret['kcIds'] = i['kch'] + '_' + i['kkxqh'] + '_' + i['zxjxjhh']
                ret['kcms'] = i['kcm'] + '_' + i['kkxqh']
                return ret
    else:
        print("[-] Not login")
        return


def checkResult(id, num):
    if is_login:
        req_url = url + '/student/courseSelect/thisSemesterCurriculum/callback'
        cookie = {
            'JSESSIONID': getCurrentCookie()['JSESSIONID'],
            'selectionBar': '1293219'
        }
        r = session.post(req_url, cookies=cookie)
        if id in str(r.text) and num in str(r.text):
            return True
        else:
            return False
    else:
        print('[-] not login')
        return False


def getScore(lesson_name):
    req_url = url + '/student/integratedQuery/scoreQuery/allPassingScores/index'
    cookie = {
        'JSESSIONID': getCurrentCookie()['JSESSIONID'],
        'selectionBar': '1379870'
    }
    pass


def autoChoice(u, p, id, name, num):
    count = 0
    while True:
        if login(u, p):
            if choiceLesson(id, name, num):
                return True
            else:
                print("[-] 第" + str(count) + "次选课失败")
        else:
            if count == 100:
                print("[-] 第" + str(count) + "次登录失败")
        count = count + 1


username = '**********'
password = '**********'
# 登陆
login(username, password)
# 120120230 唐诗意境与人生情怀(A模块)
# 需要提供课程号和课序号，课程名无所谓，为了方便表示（好看）
choiceLesson('140450470', '无线通信与网络', '01')
choiceLesson('140451380', '网络安全技术', '01')
choiceLesson('140451390', '物联网技术', '01')
choiceLesson('140451400', '网络工程', '01')
