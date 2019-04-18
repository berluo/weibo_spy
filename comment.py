from bs4 import BeautifulSoup
import requests
from lxml import etree
import re
from pymongo import MongoClient
import urllib3

cookie = {"Cookie": "_T_WM=7e017ab76d7fb79d228c67b4cd33e763; SUB=_2A25xsg5BDeRhGeVM6VER-SrJyjyIHXVTXJIJrDV6PUJbkdAKLUynkW1NTNRuCWg95Xq-PzGF6hrAPEQ3Vy4wJGFN; SUHB=0laF121NwHJqjw; SCF=AnHZACb_a-BqpR8ukjakYivCbygCl2HXw4X-zSJ6zhuJARj8JvB3hUfRlo2p-SqLb1gkSMGpyibtdUK5YlAyiuw.; SSOLoginState=1555463697"}
urllib3.disable_warnings()
client = MongoClient()
db = client['weibo']
collection = db['test_comment']

def get_weibo_comment(url):

    html = requests.get(url, cookies=cookie, verify=False).content
    selector = etree.HTML(html)
    pagenum = int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
    # print(pagenum)
    for i in range(1, pagenum+1):
        pageurl = url + "&page=" + str(i)
        pagehtml = requests.get(pageurl, cookies=cookie, verify=False).content
        soup = BeautifulSoup(pagehtml, 'lxml')
        creg = re.compile('C_\d{16}')
        content = soup.find_all(attrs={'id': creg})
        # print(content)
        for con in content:
            weibo_item = {
                'name': con.a.string,# 发布人微博ID
                'content': con.find_all(attrs={'class': 'ctt'})[0].get_text(),# 微博内容
                'time&device': con.find_all(attrs={'class': 'ct'})[0].get_text()# 发布时间及设备
            }
            print(weibo_item)
            if collection.insert_one(weibo_item):
                print('Saved to Mongo')

if __name__ == '__main__':
    url = 'https://weibo.cn/comment/Hq9XChOaA?uid=1910848371&rl=0&oid=4362012576184521'
    get_weibo_comment(url)
