import requests
import re
import json

username = '0161121574'
password = '582565'
# 软工 : 32937
major_num = '32937'
id = '120120230'
name = '唐诗意境与人生情怀(A模块)'
# kcIds = 课程号_课序号_上课时间
# 上课时间：秋季：2018-2019-1-2
# kcms = 完整课程名_课序号

url = 'http://jwxt.imu.edu.cn/j_spring_security_check'
data = {
    'j_username': username,
    'j_password': password,
    'j_captcha1': 'error'
}
cookie = {
    'JSESSIONID': 'abcoQsXmzZp0j8Ls3g3pw'
}
count = 0
session = requests.session()
while True:
    result = session.post(url, data=data, cookies=cookie)
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    count = count + 1
    if 'Internal Server Error' in result.text:
        if '502' in result.text:
            if count % 100 == 0:
                print(count)
    else:
        print("Success:")
        # 获取token
        sel_url = 'http://jwxt.imu.edu.cn/student/courseSelect/planCourse/index?fajhh=' + major_num
        sel_cookie = {
            'JSESSIONID': 'abcoQsXmzZp0j8Ls3g3pw',
            'selectionBar': '1293218'
        }
        r = session.get(sel_url, cookies=sel_cookie)
        token = re.findall('value="[0-9a-z]{32}', r.text)[0][7:]

        # 选课
        choice_url = 'http://jwxt.imu.edu.cn/student/courseSelect/planCourse/waitingfor?dealType=2'
        para = {
            'fajhh': '32937',
            'kcIds': id + '_01_2018-2019-1-2',
            'kcms': name + '_01',
            'sj': '0_0',
            'tokenValue': token
        }
        choice = session.post(choice_url, cookies=sel_cookie, data=para)
        # 查询结果
        check_url = 'http://jwxt.imu.edu.cn/student/courseSelect/selectResult/query'
        resu_data = {
            'kcNum': '1',
            'redisKey': username
        }
        check = session.post(check_url, cookies=sel_cookie, data=resu_data)
        response = json.loads(check.content)
        print(response)
        if response['isFinish']:
            if "选课成功！" in response['result']:
                print("选课成功！")
            else:
                print(response['result'])
        else:
            print('选课失败!')
        break
