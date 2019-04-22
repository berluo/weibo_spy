from bs4 import BeautifulSoup
import requests
from lxml import etree
import re
import urllib3
import pymysql
import hashlib

connection = pymysql.connect(host='',
                             user='',
                             password='',
                             db='dbtest',
                             charset='utf8mb4')
cursor = connection.cursor()

cookie = {"Cookie": "your_cookies"}
urllib3.disable_warnings()

def init_table(url):
    table_name = url[25:34]
    cursor.execute('DROP TABLE IF EXISTS %s' % table_name)
    create_sql = """
    CREATE TABLE %s (
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
    print('Table name is', table_name)

def sql_insert(sql):
    cursor.execute(sql)
    connection.commit()

def get_pagenum(url):
    html = requests.get(url, cookies=cookie, verify=False).content
    # print(html)
    selector = etree.HTML(html)
    pagenum = int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
    print('Total page number is', pagenum)
    return pagenum

def get_item(url):
    table_name = url[25:34]
    pagehtml = requests.get(url, cookies=cookie, verify=False).content
    soup = BeautifulSoup(pagehtml, 'lxml')
    creg = re.compile('C_\d{16}')
    content = soup.find_all(attrs={'id': creg})
    for con in content:
        name = con.a.string
        content = con.find_all(attrs={'class': 'ctt'})[0].get_text().replace("'", "''")
        name_content_md5 = hashlib.md5((name + content).encode("utf-8"))
        time_device = con.find_all(attrs={'class': 'ct'})[0].get_text().replace(u'\xa0', u' ')
        if re.findall("\d+", con.find_all(attrs={'class': 'cc'})[0].a.string):
            up_num = int(re.findall("\d+", con.find_all(attrs={'class': 'cc'})[0].a.string)[0])
        else:
            up_num = int(re.findall("\d+", con.find_all(attrs={'class': "cmt"})[0].string)[0])
        sql = """
        INSERT INTO %s (name, content, name_content_md5, time_device, up_num) VALUES ('%s', '%s', '%s', '%s', %d);
        """ % (table_name, name, content, name_content_md5.hexdigest(), time_device, up_num)
        with open('pengpai.sql', 'a', encoding='utf-8') as f:
            f.write(sql)

if __name__ == '__main__':
    url = 'https://weibo.cn/comment/HqnSPwuvS?'
    page_num = get_pagenum(url)
    for i in range(1, page_num+1):
        pageurl = url + '&page=' + str(i)
        get_item(pageurl)
        print("page %d/%d completed" % (i, page_num))


