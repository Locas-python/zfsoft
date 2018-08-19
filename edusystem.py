import requests
from lxml import etree
import os, re
from urllib.parse import quote
from getpass import getpass

'''
* 登录教务系统
* 爬取所有课表
* 保存为 html 文件

----

教务系统版本：1999-2012 正方软件股份有限公司
'''


print('支持系统 -> 1999-2012 正方软件股份有限公司')
print('链接格式 -> http://jwxt.example.com/')
edusystem_url = input('教务系统链接：') # 教务系统首页
login_url = f'{edusystem_url}Default2.aspx' # 登录（post）请求的链接
code_url = f'{edusystem_url}CheckCode.aspx' # 看不起，重新获取验证码的链接


web = requests.Session()
web.get(edusystem_url)  # 登录页面：获取验证码


# 获取验证码
def get_code(session):
    page = session.get(code_url)
    with open('code.gif', 'wb') as file:
        file.write(page.content)
    os.system('start code.gif') # 打开图片
    code = input('验证码(保存到当前目录下的code.gif)：')
    return code

def login(session, username, password, code):
    login_data = f'__VIEWSTATE=dDwyODE2NTM0OTg7Oz4%3D&txtUserName={username}&TextBox2={password}&txtSecretCode={code}&RadioButtonList1=%D1%A7%C9%FA&Button1=&lbLanguage=&hidPdrs=&hidsc='
    # 因为post数据要进行gb2312编码，所以使用编码后的字符串直接发生（而不是字典）
    # 所以还有手动在头部加上post信息
    headers= {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    # 登录教务系统
    res = session.post(login_url, data=login_data, headers=headers)
    if res.url == login_url: # 登录失败
        tree = etree.HTML(res.text)
        alert = tree.xpath('//script[@defer]/text()')[0]
        print(re.search(r'\((.*?)\)', alert).group(1)) # 正则表达式提取 alert() 括号里面的内容
        print('-.' * (79 // 3))
        return alert 
    else:
        print('登录成功：', res.url)
        return res


username = input('用户名：')
password = getpass('密码（输入的密码不会显示）：')

while True:
    code = get_code(web)
    res = login(web, username, password, code)

    if '验证码' in res:
        continue
    elif '密码' in res:
        password = getpass('请重新输入密码：')
    elif '用户名' in res:
        username = input('用户名：')
    else:
        break
    

# 获取课表的（相对）链接
tree = etree.HTML(res.text)
schedule_url = tree.xpath('//a[contains(text(), "课表")]/@href')[0]

# 提取链接的学名，并进行 gb2321 编码
xm = re.search(r'xm=(.*?)&', schedule_url).group(1) # 提取学名
xm = quote(xm, encoding='gb2312') # gb2312 编码
schedule_url = re.sub(r'xm=(.*?)&', 'xm='+xm+'&', schedule_url) # 替换编码后的结果
schedule_url = edusystem_url + schedule_url # 拼接成完整链接

# get/post 请求课表都要带上 referer
# get 当前正在执行的课表
# post 根据学年、学期获取课表
headers = {
    'Referer': res.url
}

# 用get请求课程表（当前正在执行的课程）
res = web.get(schedule_url, headers=headers)

# 提取 学年 xn, 学期 xq
tree = etree.HTML(res.text)
xn = tree.xpath('//select[@name="xnd"]/option/@value')
xq = tree.xpath('//select[@name="xqd"]/option/@value')
print(xn)
print(xq)
#

# 遍历学年/学期 提取所有课表
for n in xn:
    for q in xq:
        schedule_data= f'__EVENTTARGET=xqd&__EVENTARGUMENT=&__VIEWSTATE=dDwzOTI4ODU2MjU7dDw7bDxpPDE%2BOz47bDx0PDtsPGk8MT47aTwyPjtpPDQ%2BO2k8Nz47aTw5PjtpPDExPjtpPDEzPjtpPDE1PjtpPDI0PjtpPDI2PjtpPDI4PjtpPDMwPjtpPDMyPjtpPDM0Pjs%2BO2w8dDxwPHA8bDxUZXh0Oz47bDxcZTs%2BPjs%2BOzs%2BO3Q8dDxwPHA8bDxEYXRhVGV4dEZpZWxkO0RhdGFWYWx1ZUZpZWxkOz47bDx4bjt4bjs%2BPjs%2BO3Q8aTwzPjtAPDIwMTctMjAxODsyMDE2LTIwMTc7MjAxNS0yMDE2Oz47QDwyMDE3LTIwMTg7MjAxNi0yMDE3OzIwMTUtMjAxNjs%2BPjtsPGk8MT47Pj47Oz47dDx0PDs7bDxpPDE%2BOz4%2BOzs%2BO3Q8cDxwPGw8VGV4dDs%2BO2w85a2m5Y%2B377yaMTUwODAyMDEzNjs%2BPjs%2BOzs%2BO3Q8cDxwPGw8VGV4dDs%2BO2w85aeT5ZCN77ya5buW5a2Q5Y2aOz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlrabpmaLvvJrorqHnrpfmnLrnp5HlrabkuI7mioDmnK%2Fns7s7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOS4k%2BS4mu%2B8mue9kee7nOW3peeoizs%2BPjs%2BOzs%2BO3Q8cDxwPGw8VGV4dDs%2BO2w86KGM5pS%2F54%2Bt77yaMTXnvZHnu5zlt6XnqIvnj607Pj47Pjs7Pjt0PDtsPGk8MT47PjtsPHQ8QDA8Ozs7Ozs7Ozs7Oz47Oz47Pj47dDxwPGw8VmlzaWJsZTs%2BO2w8bzxmPjs%2BPjtsPGk8MT47PjtsPHQ8QDA8Ozs7Ozs7Ozs7Oz47Oz47Pj47dDxAMDxwPHA8bDxQYWdlQ291bnQ7XyFJdGVtQ291bnQ7XyFEYXRhU291cmNlSXRlbUNvdW50O0RhdGFLZXlzOz47bDxpPDE%2BO2k8Mz47aTwzPjtsPD47Pj47Pjs7Ozs7Ozs7Ozs%2BO2w8aTwwPjs%2BO2w8dDw7bDxpPDE%2BO2k8Mj47aTwzPjs%2BO2w8dDw7bDxpPDA%2BO2k8MT47aTwyPjtpPDM%2BO2k8ND47aTw1PjtpPDY%2BO2k8Nz47PjtsPHQ8cDxwPGw8VGV4dDs%2BO2w8MDgwMTM5Oz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDwwODAxMzk7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOiwgzAxNzg7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCgyMDE2LTIwMTctMiktMDgwODkyLTA4MDEzOS0xQTs%2BPjs%2BOzs%2BO3Q8cDxwPGw8VGV4dDs%2BO2w8572R57uc5pON5L2c57O757ufOz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkag156ysMeiKgui%2Fnue7rTLoioJ756ysMTMtMTPlkah9L%2BS4gOagizUwMuWupC%2FotbXlv5fkv4o7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWRqDTnrKw56IqC6L%2Be57utMuiKgnvnrKwxNS0xNeWRqOWNleWRqH0vQ2lzY2%2FnvZHnu5zlrp7pqozlrqQv6LW15b%2BX5L%2BKOz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDE3LTA1LTIzLTE3LTI5Oz4%2BOz47Oz47Pj47dDw7bDxpPDA%2BO2k8MT47aTwyPjtpPDM%2BO2k8ND47aTw1PjtpPDY%2BO2k8Nz47PjtsPHQ8cDxwPGw8VGV4dDs%2BO2w8MDUxMDcwOz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDwwNjEwNjk7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOaNojAwMDM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCgyMDE2LTIwMTctMiktMDUyMzlGLTA1MTA3MC0yOz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlpKflraboi7Hor63vvIjpnZ7oibrkvZPvvIkoNCk7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWRqDHnrKwz6IqC6L%2Be57utMuiKgnvnrKwzLTEw5ZGofS%2FkuInmoIs2MDPlrqQv5byg6ZuqOz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkagx56ysM%2BiKgui%2Fnue7rTLoioJ756ysMy0xMOWRqH0v5LiJ5qCLNjAz5a6kL%2BiCluiJs%2BiKszs%2BPjs%2BOzs%2BO3Q8cDxwPGw8VGV4dDs%2BO2w8MjAxNy0wMy0xNS0wOC0xNjs%2BPjs%2BOzs%2BOz4%2BO3Q8O2w8aTwwPjtpPDE%2BO2k8Mj47aTwzPjtpPDQ%2BO2k8NT47aTw2PjtpPDc%2BOz47bDx0PHA8cDxsPFRleHQ7PjtsPDA1MTA3MDs%2BPjs%2BOzs%2BO3Q8cDxwPGw8VGV4dDs%2BO2w8MDYxMDY5Oz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDzmjaIwMDA1Oz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDwoMjAxNi0yMDE3LTIpLTA1MjM5Ri0wNTEwNzAtMjs%2BPjs%2BOzs%2BO3Q8cDxwPGw8VGV4dDs%2BO2w85aSn5a2m6Iux6K%2Bt77yI6Z2e6Im65L2T77yJKDQpOz4%2BOz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkagz56ysMeiKgui%2Fnue7rTLoioJ756ysMy0xMOWRqH0v5LiJ5qCLNjA05a6kL%2BW8oOmbqjs%2BPjs%2BOzs%2BO3Q8cDxwPGw8VGV4dDs%2BO2w85ZGoM%2BesrDHoioLov57nu60y6IqCe%2BesrDMtMTDlkah9L%2BS4ieagizYwNOWupC%2FogpboibPoirM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIwMTctMDMtMTUtMDgtMTg7Pj47Pjs7Pjs%2BPjs%2BPjs%2BPjt0PEAwPHA8cDxsPFBhZ2VDb3VudDtfIUl0ZW1Db3VudDtfIURhdGFTb3VyY2VJdGVtQ291bnQ7RGF0YUtleXM7PjtsPGk8MT47aTwwPjtpPDA%2BO2w8Pjs%2BPjs%2BOzs7Ozs7Ozs7Oz47Oz47dDxAMDxwPHA8bDxQYWdlQ291bnQ7XyFJdGVtQ291bnQ7XyFEYXRhU291cmNlSXRlbUNvdW50O0RhdGFLZXlzOz47bDxpPDE%2BO2k8MD47aTwwPjtsPD47Pj47Pjs7Ozs7Ozs7Ozs%2BOzs%2BO3Q8QDA8cDxwPGw8UGFnZUNvdW50O18hSXRlbUNvdW50O18hRGF0YVNvdXJjZUl0ZW1Db3VudDtEYXRhS2V5czs%2BO2w8aTwxPjtpPDA%2BO2k8MD47bDw%2BOz4%2BOz47Ozs7Ozs7Ozs7Pjs7Pjs%2BPjs%2BPjs%2B&xnd={n}&xqd={q}'
        res = web.get(schedule_url, data=schedule_data, headers=headers)
        tree = etree.HTML(res.text)
        schedule = etree.tounicode(tree.xpath('//table')[1])
        
        filename = f'{n}--{q}.html'
        with open(filename, 'w', encoding='utf-8') as file:
            print('正在写入：', filename)
            file.write(schedule)
        