# -*- coding: utf-8 -*-
# Version: 1.2.0

from selenium import webdriver
from bs4 import BeautifulSoup
import json
import os.path, errno

#param_map = {
#             "厂商指导价":"official_price", 
#             "经销商参考价":"real_price",
#             "厂商":"manufacturer",
#             "级别":"class",
#             "能源类型":"power",
#             "上市时间":"launch_date",
#             "纯电续航里程":"battery_life",
#             "电池充电时间":"charging_time",
#             "最大功率(kW)":"max_kW",
#             "最大扭矩(N·m)":"max_Nm",
#             "发动机":"engine",
#             "变速箱":"transmission",
#             "长*宽*高(mm)":"l_w_h",
#             "车身结构":"structure",
#             "最高车速(km/h)":"max_speed",
#             "官方0-100km/h加速(s)":"0_to_100",
#             "整车质保":"warranty"
#         }
urls = [
        "https://car.autohome.com.cn/config/spec/26916.html",
        "https://car.autohome.com.cn/config/series/692.html",
        "https://car.autohome.com.cn/config/series/66.html",
        "https://car.autohome.com.cn/config/series/3823.html",
        "https://car.autohome.com.cn/config/series/703.html",
        "https://car.autohome.com.cn/config/series/4045.html",
        "https://car.autohome.com.cn/config/series/110.html",
        "https://car.autohome.com.cn/config/series/364.html",
        "https://car.autohome.com.cn/config/series/209.html",
        "https://car.autohome.com.cn/config/series/872.html",
        "https://car.autohome.com.cn/config/series/669.html",
        "https://car.autohome.com.cn/config/series/4307.html",
        "https://car.autohome.com.cn/config/series/2476.html",
        "https://car.autohome.com.cn/config/series/255.html",
        "https://car.autohome.com.cn/config/series/3097.html",
        "https://car.autohome.com.cn/config/series/201.html",
        "https://car.autohome.com.cn/config/series/2988.html",
        "https://car.autohome.com.cn/config/series/382.html",
        "https://car.autohome.com.cn/config/series/2664-8052.html"
        ]

driver = webdriver.Chrome()
driver.implicitly_wait(10)

driver.get("https://car.autohome.com.cn/config/spec/26916.html")
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

dictionary = {} #偽類對應文字
car_list = []

#Recursive處理目標內容文字，包含解析偽類元素
def process_content(contents): 
    result = ''
    for content in contents:
        #判斷是否為html格式
        if ('</' in str(content)):
            if('ul' in str(content)):
                #ul element: for color
                for li in content.findAll('li'):
                    if(result is not ''):
                        result += (',' + li.contents[0]['title'])
                    else:
                        result += li.contents[0]['title']
            elif('span' in str(content)):
                #若是span元素，以contents數量判斷是否為偽類
                if len(content.contents) > 0:
                    #非偽類處理
                    result += process_content(content.contents)
                else: 
                    #偽類處理
                    cValue = content['class'][0]
                    if cValue in dictionary:
                        result += dictionary[cValue]
                    else:
                        #執行JavaScript，獲取偽類對應文字
                        script = "return window.getComputedStyle(document.getElementsByClassName('%s')[0],'before').getPropertyValue('content')" %(content['class'][0])
                        x = driver.execute_script(script).strip('\"')
                        dictionary[cValue] = x
                        result += x    
            else:
                #其它html元素處理
                result += process_content(content.contents)
        else:
            #純文字
            result += content                        
    return result   


def find_title(soup):
    div = soup.find("div", {"class":"subnav-title-name"})
    return process_content(div.contents)

#Car name
def find_car_name(soup):
    for item in soup.findAll("div", {"class":"carbox"}):
        for ana in item.findAll("a"):
            if ana.parent.name == "div" and len(ana.contents) > 0:
                car = {}
                car["name"] = process_content(ana.contents)
                car_list.append(car)

#Car parameter table
def find_car_parameter(soup):
    for table in soup.findAll("table", {"class":"tbcs"}):
        for tr in table.findAll("tr"):
            if ('style' in tr.attrs) and (tr.attrs['style'] == 'display:none'):
                continue
            else:
                origin_param = ""
                div = None
                th = tr.find("th")
                if th is not None:
                    div = th.find("div")
#                key_param = ""
                if div is not None:
                    origin_param = process_content(div.contents)
#                    if origin_param in param_map:
#                        key_param = param_map[origin_param]
                if origin_param is not "":
                    index = 0
                    for td in tr.findAll("td"):
                        car = car_list[index]
                        index += 1
                        div = td.find("div")
                        car[origin_param] = process_content(div.contents)
             
#main process
for url in urls:
    car_list = []
    dictionary = {}
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    filename = find_title(soup).strip('\n')
    find_car_name(soup)
    find_car_parameter(soup)
    #Output               
    save_path = os.path.join(os.getcwd(), 'result')
    if not os.path.exists(save_path):
        try:
            os.makedirs(save_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    complete_name = os.path.join(save_path, filename)  
    file = open(complete_name, 'w', encoding = 'UTF-8')
    file.write(json.dumps(car_list, ensure_ascii=False))  
    file.close()

driver.quit
    
    