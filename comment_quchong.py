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

def sql_fetch(table_name, md5):
    select_sql = """
    SELECT * FROM %s WHERE name_content_md5 = '%s'
    """ % (table_name, md5)
    cursor.execute(select_sql)
    return cursor.fetchone()

def sql_insert(table_name, item):
    ROWkey = ''
    ROWstr = ''
    for key in item.keys():
        ROWkey = (ROWkey + '%s' + ',') % key
        ROWstr = (ROWstr + "'%s'" + ',') % (item[key])
    insert_sql = """
    INSERT INTO %s (%s) VALUES (%s)
    """ % (table_name, ROWkey[:-1], ROWstr[:-1])
    # print(insert_sql)
    cursor.execute(insert_sql)
    connection.commit()

def get_pagenum(url):
    html = requests.get(url, cookies=cookie, verify=False).content
    # print(html)
    selector = etree.HTML(html)
    pagenum = int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
    print('Total page number is', pagenum)
    return pagenum

def get_item(url):
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
        item = {
            'name':name,
            'content': content,
            'name_content_md5': name_content_md5.hexdigest(),
            'time_device': time_device,
            'up_num': up_num
        }
        print(item)
        if sql_fetch(url[25:34], item['name_content_md5']):
            print('Already exist, skip.')
            continue
        else:
            sql_insert(url[25:34], item)
            print('Item inserted.')


if __name__ == '__main__':
    url = 'https://weibo.cn/comment/HqwcJ2TzB?uid=1618051664&rl=0&gid=10001'
    # get_pagenum(url)
    # init_table(url)
    get_item(url)

    connection.close()
