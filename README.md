# SYSU_Courses
# 中山大学抢课脚本 
**SYSUCourses** 是使用python实现的中山大学抢课程序, **支持同时选多门课程**。

目前支持的选课类型情况：
- [x] 公选
- [x] 专选
- [ ] 体育

##1 环境与依赖

此版本只能运行与 Python 3.4以上环境

使用之前需要依赖的库：

```bash
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
```
##2 代码

```python
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
    data = response.content.decode('utf-8')
    regx = r'sid=(\S*?)">'
    pm = re.findall(regx, data)
    sid = pm[0]
    regx = r'''courses\?kclb=\d+?&xnd=\S+?&xq=\d+?&fromSearch=false&sid=\S+?\"'''
    pm = re.findall(regx, data)
    tmp = 'http://uems.sysu.edu.cn/elect/s/'
    urls['公选'] = tmp + pm[1].replace('\"', '')
    urls['专选'] = tmp + pm[3].replace('\"', '')
    
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
请输入选课类型：''')
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
    login()
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

```

##3.使用说明

###3.1 运行程序
在命令行中输入 **python SYSU_Courses.py**
回车运行。

### 3.2 登录
此时，会弹出**Check_code.jpg**
同时提示输入图中验证码。
接下来输入学号密码完成登录。
![Alt text](https://github.com/JustMeDoIt/SYSU_Courses/blob/master/Image/QQ%E6%88%AA%E5%9B%BE20160903205756.png)

### 3.3 选课

- 输入所需选课程数。
- 选择课程类型
- 输入课程名称
- 输入教师名称
- 选择时间段(若有多个时间段的课程)
![Alt text](https://github.com/JustMeDoIt/SYSU_Courses/blob/master/Image/QQ%E6%88%AA%E5%9B%BE20160903204617.png)

### 3.4 等待选课结果

- 若是有空位则直接选上
- 若是有时间冲突等原因则选课失败
- 若是课程人数已满，则挂机等待有人退课，立即补上空缺。
![Alt text](https://github.com/JustMeDoIt/SYSU_Courses/blob/master/Image/QQ%E6%88%AA%E5%9B%BE20160903204652.png)
(已选哈哈！ )

### 4.作者有话说

本人小白，这个程序是我暑假在家学习python模拟登陆的一个习作，其实原理还是挺简单的。使用了多线程，支持多门课程同时监视。不过话说回来，这个抢课脚本挺鸡肋的。。。因为我们在选课前选课列表是空的，所以要等到开抢才显示出来，所以呢，等你输完各种信息别人早就选上了，哈哈莫吐槽哈！！！
**但是，它还是有用处滴。。。譬如说，有些同学可能会因为各种原因（比如时间冲突等）退课，这时我们便可以立即选上，爽！！！**
