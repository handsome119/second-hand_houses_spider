## V1.0 author:QT
import requests
from bs4 import BeautifulSoup
import bs4
import csv,os
from datetime import datetime
import re

##setting
TARGETCITY='北京市'
TARGETDIST='海淀区' #输入你想爬取的区 
bjdistricts ={'东城区':'dongcheng','西城区':'xicheng','朝阳区':'chaoyang','海淀区':'haidian','丰台区':'fengtai','石景山区':'shijingshan',\
              '通州区':'tongzhou','昌平区':'changping','大兴区':'daxing','亦庄开发区':'yizhuangkaifaqu','顺义区':'shunyi','房山区':'fangshan',\
              '门头沟区':'mentougou','平谷区':'pinggu','怀柔区':'huairou','密云区':'miyun','延庆区':'yanqing','燕郊':'yanjiao','香河':'xianghe'} 
#
PAGES = 50 # Based on bjdistricts[TARGETDIST], 
           # configure PAGES form `https://bj.lianjia.com/ershoufang/bjdistricts[TARGETDIST]`

#-----------------------------------------------------------------------------------------------------------------------------------------------##
def getlocation(name):#调用百度API查询位置
    bdurl = 'http://api.map.baidu.com/geocoder/v2/?address='
    output = 'json'
    ak = ''#your key 
    callback = 'showLocation'
    url = bdurl + name + '&output=t' + output + '&ak=' + ak + '&callback=' + callback
    res = requests.get(url)
    s = BeautifulSoup(res.text,'html.parser')
    lng = s.find('lng')
    lat = s.find('lat')
    if lng:
        return lng.get_text()+','+lat.get_text()
#-----------------------------------------------------------------------------------------------------------------------------------------------##
def getHTMLText(url):
    mheader = {'User-Agent': 'Baiduspider+(+http://www.baidu.com/search/spider.htm)'}
    #mheader = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}#请求头，模拟浏览器登陆
    try:
        r = requests.get(url, headers=mheader, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "None"
#-----------------------------------------------------------------------------------------------------------------------------------------------##
def fillHomeList(hlist, html):
    soup = BeautifulSoup(html, 'html.parser')
    for ele in soup.find_all('li',class_='clear'):
        houseInfoTag = ele.find('div',class_='houseInfo')
        str_houseInfo = houseInfoTag.get_text().replace(' ','')
        #print(houseInfoTag.a.get('href').split('/')[-2])
        district_number = houseInfoTag.a.get('href').split('/')[-2]
        house_code  = ele.a.get('data-housecode')
        name_houseInfo = houseInfoTag.a.string
        style_houseInfo = re.search(r'(\d室\d厅)|(\d房间\d卫)', str_houseInfo).group()
        area_houseInfo = re.search(r'/[0-9.]*平米/', str_houseInfo).group()[1:-3]
        dire_houseInfo = re.search(r'/[南北东西]+/', str_houseInfo).group()[1:-1]
        decro_houseInfo = re.search(r'(精装|简装|毛坯|其他)(/[有无]电梯)?', str_houseInfo).group()
        # print(name_houseInfo,style_houseInfo,area_houseInfo,dire_houseInfo,decro_houseInfo)

        
        app_positionInfo = ele.find('div',class_='positionInfo').get_text().split('/')
        lnglat = getlocation(TARGETCITY +' '+TARGETDIST +' '+ app_positionInfo[2] + ' ' + name_houseInfo) #add latitude/longitude from baidu API
        #district No.,housecode,houseInfo['Name','Style','Area(m2)','Direct','Docorat'],positionInfo['Floor','Time','Address'],priceInfo,location(longitude,latitude)
        totalPrice = ele.find('div',class_='priceInfo').span.string
        fol_followInfo = ele.find('div',class_='followInfo').get_text().split('/')[0][:-3]
        visit_followInfo = ele.find('div',class_='followInfo').get_text().split('/')[1].split('次')[0]
        avgPrice = round(10000*float(totalPrice)/float(area_houseInfo))
        hlist.append([district_number,house_code,name_houseInfo,style_houseInfo,area_houseInfo,dire_houseInfo,decro_houseInfo]+\
                       
                    app_positionInfo+[totalPrice,avgPrice,fol_followInfo,visit_followInfo,lnglat])
        for li in hlist: print(li)
 
#-----------------------------------------------------------------------------------------------------------------------------------------------##

def main():

    homelist = []
    CSVheaders=['小区编号','房屋编号','小区名','户型','面积(m2)','朝向','装修','楼层','年代','区位','总价(万)','均价(元/m2)','关注(人)','带看(次)','坐标']
    myroot ='./csv/'
    path = myroot + datetime.now().strftime('%Y%m%d %H:%M:%S') + '_' + bjdistricts[TARGETDIST] + '.csv'
    try:
        if not os.path.exists(myroot):
            os.mkdir(myroot)
        if not os.path.exists(path):
            with open(path,'w',encoding='utf-8',newline='') as cf:#encoding='gb18030'
                writers = csv.DictWriter(cf, CSVheaders)
                writers.writeheader()
                print("start to connect 'lianjia.com'")
                for i in range(1, PAGES+1):#1,PAGES+1
                    url = 'https://bj.lianjia.com/ershoufang/' + bjdistricts[TARGETDIST] + '/pg'+str(i)    
                    
                    html = getHTMLText(url)
                    if html == 'None': raise NameError
                    fillHomeList(homelist, html)


                    for row in homelist:
                        writers.writerow(dict(zip(CSVheaders,row)))#将dict写入到csv文件中
                    homelist=[]
                    print("{0}/{1} completed!".format(i,PAGES))
            print("Done!")
        else:
            print("Already exist.")

    except NameError:
        print('getHTMLText return empty')
    except Exception as e:
        print("Error!")

  
if __name__ == '__main__':
	main()
