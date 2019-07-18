from bs4 import BeautifulSoup
import requests
import re
import urllib3
import hashlib
import time

urllib3.disable_warnings()
headers = {
    "Cookie": "your_cookies",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0"
}
def create_table(table_name):
    create_sql = """CREATE TABLE %s_weibo (
    `id` INT NOT NULL AUTO_INCREMENT,
    `serial_num` VARCHAR(45) NULL,
    `author` VARCHAR(100) NULL,
    `origin_author` VARCHAR(100) NULL,
    `origin_weibo` LONGTEXT NULL,
    `content` LONGTEXT NULL,
    `publish_time` VARCHAR(45) NULL,
    `now_time` VARCHAR(45) NULL,
    PRIMARY KEY (`id`))
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb4;\n""" % table_name
    return create_sql

def get_pagenum(url):
    html = requests.get(url, headers=headers, verify=False).content
    soup = BeautifulSoup(html, 'lxml')
    page_num = int(soup.find(attrs={'id': 'pagelist'}).find(attrs={'type': 'hidden'})['value'])
    print('Total page number is', page_num)
    return page_num

def get_content(url):
    pattern = re.compile('\/(\w+)$')
    table_name = re.findall(pattern, url)[0]
    # print(create_table(table_name))

if __name__ == '__main__':
    # url = 'https://weibo.cn/sickipedia'
    # get_content(url)
    weibo_pattern = re.compile('M_\w+')
    with open('user.html', 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    weibo_List = soup.find_all(attrs={'id': weibo_pattern})
    author = soup.find(attrs={'class': 'ctt'}).get_text().split('\n')[1].strip()
    for each in weibo_List:
        # repost_flag
        if each.find(attrs={'class': 'cmt'}):
            repost_flag = True;
        else:
            repost_flag = False
        # origin_author & origin_weibo
        if repost_flag == True:
            origin_author = each.find(attrs={'class': 'cmt'}).a.string.strip()
            origin_weibo = each.find(attrs={'class': 'ctt'}).get_text().strip()
            content = each.div.next_sibling.next_sibling.next_sibling.next_sibling.get_text()
        else:
            origin_author = ''
            origin_weibo = ''
            content = each.find(attrs={'class': 'ctt'}).get_text().strip()

        # serial num
        serial_num = each.find(attrs={'class': 'cc'})['href']
        serial_pattern = re.compile('\/(\w+)\?')
        serial_num = re.findall(serial_pattern, serial_num)[0]
        # content

        # print
        print('repost_flag: %s' % repost_flag)
        print('origin_author: %s' % origin_author)
        print('origin_weibo: %s' % origin_weibo)
        print('serial_num: %s' % serial_num)
        print('author: %s' % author)
        print('content: %s' % content)
        print('********************')
