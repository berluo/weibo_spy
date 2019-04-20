from bs4 import BeautifulSoup
import requests
from lxml import etree
import re
import urllib3
import pymysql
import hashlib

cookie = {"Cookie": "your_cookies"} #定义cookie
urllib3.disable_warnings()
url = 'https://weibo.cn/comment/HpzmF8bpc?uid=2145291155&rl=0' #需要爬取微博评论页地址
table_name = url[25:34]
html = requests.get(url, cookies=cookie, verify=False).content
selector = etree.HTML(html)
pagenum = int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
print("database name is ", table_name)
print('Total page number is', pagenum)
connection = pymysql.connect(host='ip_of_mysql', #mysql数据库地址
                             user='user_of_mysql', #mysql数据库用户名
                             password='pwd_of_mysql', #mysql密码
                             db='db_name', #数据库名称
                             charset='utf8mb4')
cursor = connection.cursor()
cursor.execute('DROP TABLE IF EXISTS %s;' % table_name)
create_sql = """
CREATE TABLE weibo_spider.%s (
`id` INT NOT NULL AUTO_INCREMENT,
`name` VARCHAR(45) NULL,
`content` LONGTEXT NULL,
`name_content_md5` VARCHAR(45) NULL,
`time_device` VARCHAR(45) NULL,
`up_num` INT NULL,
PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;
""" % table_name
cursor.execute(create_sql)
connection.commit()

for i in range(1, pagenum+1):
    pageurl = url + "&page=" + str(i)
    pagehtml = requests.get(pageurl, cookies=cookie, verify=False).content
    soup = BeautifulSoup(pagehtml, 'lxml')
    creg = re.compile('C_\d{16}')
    content = soup.find_all(attrs={'id': creg})

    for con in content:
        name = con.a.string
        content = con.find_all(attrs={'class': 'ctt'})[0].get_text()
        name_content_md5 = hashlib.md5((name + content).encode("utf-8"))
        time_device = con.find_all(attrs={'class': 'ct'})[0].get_text().replace(u'\xa0', u' ')
        if re.findall("\d+", con.find_all(attrs={'class': 'cc'})[0].a.string):
            up_num = int(re.findall("\d+", con.find_all(attrs={'class': 'cc'})[0].a.string)[0])
        else:
            up_num = int(re.findall("\d+", con.find_all(attrs={'class': "cmt"})[0].string)[0])
        sql = """
        INSERT INTO %s (name, content, name_content_md5, time_device, up_num) VALUES ('%s', '%s', '%s', '%s', %d);
        """ % (table_name, name, content, name_content_md5.hexdigest(), time_device, up_num)
        cursor.execute(sql)
        connection.commit()
        # print("Saved to Mysql")
        # with open('insert.sql', 'a', encoding='utf-8') as f:
        #     f.write(sql)
        # print(sql)
    print('page_num %d / %d saved to mysql ' % (i, pagenum))
connection.close()
