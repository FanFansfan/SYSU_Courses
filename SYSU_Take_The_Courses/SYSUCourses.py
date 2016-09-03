import random
import os
import re
import time
import sys
import requests
import json
import subprocess
import urllib
import hashlib
import threading

j_code = ""
_eventId = "submit"
gateway = "true"	
lt = ""
password = ""
username = ""
sid = ''
cookies = {}
urls = {}
session = requests.session()
headers = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    'Accept-Encoding' : 'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection':'keep-alive',
    'Host':'uems.sysu.edu.cn',
    'Referer':'http://uems.sysu.edu.cn/elect/',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0 Firefox/47.0',
}
ImgPath = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'Check_code.jpg'
datas = []
class_names = []
choices = []
teachers = []
num = int(0)

def GET_code():
    global headers, j_code
    url = 'http://uems.sysu.edu.cn/elect/login/code'
    response = session.get(url)
    with open(ImgPath, 'wb') as f:
        f.write(response.content)
    if sys.platform.find('darwin') >= 0:
        subprocess.call(['open', ImgPath])
    elif sys.platform.find('linux') >= 0:
        subprocess.call(['xdg-open', ImgPath])
    else:
        os.startfile(ImgPath)
    time.sleep(1)
    j_code = input("请输入图中验证码：")
 
def login():
    global j_code, _eventId, gateway, lt, password, username, sid, cookies, urls
    username = input("请输入您的学号：")
    password = input("请输入您的密码：")
    m = hashlib.md5()
    m.update(str.encode(password))
    password = m.hexdigest().upper()
    params = {
        'j_code' : j_code,
        '_eventId' : _eventId,
        'gateway' : gateway,	
        'lt' : lt,
        'password' : password,
        'username' : username,
    }
    url = 'http://uems.sysu.edu.cn/elect/' 
    r = session.get(url)
    cookies = r.cookies
    url = 'http://uems.sysu.edu.cn/elect/login'
    h = headers
    response = session.post(url, headers = h, data = params, cookies = cookies)
    if str(response.status_code) == '200':
        print("登录成功！")
        data = response.content.decode('utf-8')
        regx = r'sid=(\S*?)">'
        pm = re.findall(regx, data)
        sid = pm[0]
        regx = r'''courses\?kclb=\d+?&xnd=\S+?&xq=\d+?&fromSearch=false&sid=\S+?\"'''
        pm = re.findall(regx, data)
        tmp = 'http://uems.sysu.edu.cn/elect/s/'
        urls['公选'] = tmp + pm[1].replace('\"', '')
        urls['专选'] = tmp + pm[3].replace('\"', '')
        return True
    else :
        print("登录失败！")
        return False
    
def consult():
    global cookies, num, datas, class_names, choices, teachers
    cookie = ''
    data = ''
    class_name = ''
    choice = ''
    teacher = ''
    url = ''
    num = input('请输入需选课程数：')
    num = int(num)
    for i in range(num):
        while True:
            kind = input('''    1、公选 
    2、专选
请输入第%s门选课类型：''' % (i + 1))
            kind = int(kind)
            if kind == 1:
                url = urls['公选']
                break
            elif kind == 2:
                url = urls['专选']
                break
            else:
                print('请输入一个合法数字进行选择：')
                continue
        response = session.get(url, headers = headers, cookies = cookies)
        data = response.content.decode("utf-8")
        class_name = ''
        teacher = ''
        choice = ''
        while True:
            class_name = input('请输入课程名称：')
            teacher = input('请输入教师名称：')
            regx = r'''<td><a href="javascript:void\(0\)" onclick="courseDet\(\'\d+?\'\)">%s</a></td>\s+?<td>([\s\S]{20,35})</td>\s+?<td class='c w'>%s</td>''' % (class_name, teacher)
            pm = re.findall(regx, data)
            if len(pm) == 0:
                print('查无符合课程，请重新输入！')
                continue
            elif len(pm) > 1:
                time = []
                i = int(1)
                for temp in pm:
                    time.append(temp)
                    print('    ' + str(i) + '、'+ temp)
                    i += 1
                i = int(1)
                while True:
                    tmp = input('请选择一个时间段：')
                    tmp = int(tmp)
                    if tmp < len(time):
                        choice = time[tmp]
                        break
                    else:
                        print('无效选择！')
                        continue
                break
            else:
                choice = pm[0]
                break
        print()
        datas.append(data)
        teachers.append(teacher)
        class_names.append(class_name)
        choices.append(choice)
        #print(choice)

def select(data, class_name, choice, teacher):
    regx = r'''<td><a href="javascript:void\(0\)" onclick="courseDet\(\'(\d+?)\'\)">%s</a></td>\s+?<td>%s</td>\s+?<td class='c w'>%s</td>''' % (class_name, choice, teacher)
    jxbh = re.findall(regx, data)
    #print(data)
    #print(jxbh)
    print('正在监视 %s 的选课状况, 请不要关闭程序，如果选课成功会有提示！' % class_name)
    while True:
        url = 'http://uems.sysu.edu.cn/elect/s/elect'
        params = {
            'jxbh' : jxbh[0],
            'sid' : sid,
        }
        response = session.post(url, headers = headers, data = params, cookies = cookies)
        data = response.content.decode('utf-8')
        regx = r'code&#034;:(\d+?),'
        err = re.findall(regx, data)
        if err[0] == '0':
            print('Congradulation: %s 选课成功！' % class_name)
            break
        elif err[0] == '9':
            print('Error: 选课失败，%s 已选，不能重复选择！' % class_name)
            break
        elif err[0] == '12' or err[0] == '17':
            regx_ = r'caurse&#034;:&#034;([\s\S]+?)&'
            msg = re.findall(regx_, data)
            print('Error: ' + msg[0])
            break
        elif err[0] == '18':
             pass
        #    print('Error: 选课失败，该课程人数已满！') #如果有人退选就可以乘虚而入
        else :
            print('Error: 选课失败！')
            break
        
def main():
    GET_code()
    if login() == False:
        return False
    os.remove(ImgPath)
    consult()
    threads = []
    for i in range(num):
        threads.append(threading.Thread(target=select, args=(datas[i], class_names[i], choices[i], teachers[i],)))
    for t in threads:
        #t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
        
if __name__ == "__main__":
    main()
