#-*- codeing = utf-8 -*-
#@Time: 2020/7/12 11:07
#@Author:shan
#@File:Spider.py

from bs4 import BeautifulSoup  #网页解析，获取数据
import re   #正则表达式，进行文字匹配
import  urllib.request,urllib.error #指定url,获取网页数据
import xlwt #进行Excel操作
import sqlite3 #进行数据库操作

def main():
    baseurl = "https://movie.douban.com/top250?start="
    #1.爬取网页
    dataList = get_data(baseurl)
    savePath = "豆瓣电影Top250.xls"
    save_data(dataList,savePath)


#影片详情链接规则
findLink = re.compile(r'<a href="(.*?)">')
#影片海报链接规则
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)
#影片名称规则
findTitle = re.compile(r'<span class="title">(.*?)</span>')
#影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#影片概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
#影片信息
findBD = re.compile(r'<p class="">(.*?)</p>',re.S)


#爬取网页
def get_data(baseurl):
    dataList = []
    for i in range(0,10):       #调用获取页面信息的函数10次
        url = baseurl + str(i*25)
        html = ask_url(url)     #保存获取到的网页源码
        #逐一解析数据
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all("div",class_="item"): #查找符合要求的字符串，形成列表
            #print(item) #测试：查看电影item全部信息
            data = []
            item = str(item)

            # re库通过正则表达式查找指定的字符串
            link = re.findall(findLink,item)[0]         #获取影片详情链接
            data.append(link)
            imgSrc = re.findall(findImgSrc,item)[0]     #获取影片海报链接
            data.append(imgSrc)

            title = re.findall(findTitle,item)          #获取影片名称(可能有英文名和中文名）
            if len(title) ==2:
                ctitle = title[0]                       #添加中文名
                data.append(ctitle)
                otitle = title[1].replace("/","")       #添加英文名
                data.append(otitle)
            else:
                data.append(title[0])
                data.append(' ')                        #外国名留空

            rating = re.findall(findRating,item)[0]        #获取影片评分
            data.append(rating)
            judge = re.findall(findJudge,item)[0]          #获取影片评价人数
            data.append(judge)
            inq = re.findall(findInq,item)                 #获取影片概述
            if len(inq)!=0:
                #inq = inq.replace("。"," ")
                data.append(inq)
            else:
                data.append(" ")
            bd = re.findall(findBD,item)[0]                #获取影片信息
            bd = re.sub('<br(\s+)?/>(\s+)'," ",bd)          #去掉<br/>
            bd = re.sub('/'," ",bd)
            data.append(bd.strip())                         #去掉空格
            dataList.append(data)                           #把处理好的一部电影放入dataList
    return dataList

#获取指定url的网页内容
def ask_url(url):
    head = {    #模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/79.0.3945.88 Safar/537.36"
    }   #用户代理，表示告诉豆瓣服务器，我们是什么类型的机器，浏览器。本质是告诉浏览器，我们可以接收什么水平的数据
    request  = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


#保存数据
def save_data(dataList,savePath):
    workbook = xlwt.Workbook(encoding="utf-8",style_compression=0)  # 创建workbook对象
    worksheet = workbook.add_sheet('豆瓣电影TOP250',cell_overwrite_ok=True)  # 创建工作表
    col = ("电影详情链接","电影海报链接","电影中文名","电影外文名","评分","评价人数","概况","电影信息")
    for i in range(0,8):
        worksheet.write(0,i,col[i])
    for i in range(0,250):
        print("存入第{0}条".format(i+1))
        data = dataList[i]
        for j in range(0, 8):
            worksheet.write(i+1,j,data[j])
    workbook.save(savePath)

if __name__ == "__main__":
    main()
    print("爬取结束")