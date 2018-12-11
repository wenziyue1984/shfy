# -*- coding: utf-8 -*-
import binascii
import random
import re
import sys
import urllib

import requests

reload(sys)
sys.setdefaultencoding('utf-8')


# def str_16(cstr):
#     str_tmp = binascii.b2a_hex(cstr).upper()
#     str_add = ''
#     index = 0
#     while index < len(str_tmp):
#         str_add += '%' + str_tmp[index: index + 2]
#         index += 2
#     return str_add
#
# cn1 = u'\u5b9d\u5c71\u533a\u4eba\u6c11\u6cd5\u9662'
# cn2 = u"上海市高级人民法院"
# cn3 = "上海市高级人民法院"
# print cn1.encode('utf-8')
# print str_16(cn1.encode('utf-8'))
# print str_16(cn2)
# print str_16(cn3)
#
# dic = {'derek': '编码'}
# print urllib.urlencode(dic)
#
# url = 'http://wenshu.court.gov.cn/list/list/?sorttype=1&number=5HU4HY3K&guid=f64e6561-b002-bb59cc41-03cd7303af23&conditions=searchWord+上海市高级人民法院+SLFY++法院名称:上海市高级人民法院&conditions=searchWord++CPRQ++裁判日期:2018-05-01 TO 2018-05-02'
# dt = '2018-05-01'
# dic2 = {'sorttype': '1', 'conditions': 'searchWord+'+cn1.encode('utf-8')+'+SLFY++法院名称:'+cn1.encode('utf-8'),}
# dic3 = {'conditions':'searchWord++CPRQ++裁判日期:'+dt+' TO '+dt}
# print urllib.urlencode(dic2)+'&'+urllib.urlencode(dic3)
# 'http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+上海市高级人民法院+SLFY++法院名称:上海市高级人民法院&conditions=searchWord++CPRQ++裁判日期:2018-05-01 TO 2018-05-02'
# '''
# conditions=searchWord%2B%E4%B8%8A%E6%B5%B7%E5%B8%82%E9%AB%98%E7%BA%A7%E4%BA%BA%E6%B0%91%E6%B3%95%E9%99%A2%2BSLFY%2B%2B%E6%B3%95%E9%99%A2%E5%90%8D%E7%A7%B0%3A%E5%AE%9D%E5%B1%B1%E5%8C%BA%E4%BA%BA%E6%B0%91%E6%B3%95%E9%99%A2&sorttype=1&conditions=searchWord%2B%2BCPRQ%2B%2B%E8%A3%81%E5%88%A4%E6%97%A5%E6%9C%9F%3A2018-05-01+TO+2018-05-01
# '''
# '''
# http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+%E4%B8%8A%E6%B5%B7%E5%B8%82%E9%AB%98%E7%BA%A7%E4%BA%BA%E6%B0%91%E6%B3%95%E9%99%A2+SLFY++%E6%B3%95%E9%99%A2%E5%90%8D%E7%A7%B0:%E4%B8%8A%E6%B5%B7%E5%B8%82%E9%AB%98%E7%BA%A7%E4%BA%BA%E6%B0%91%E6%B3%95%E9%99%A2&conditions=searchWord++CPRQ++%E8%A3%81%E5%88%A4%E6%97%A5%E6%9C%9F:2018-05-01%20TO%202018-05-01
# '''
#
# headers = {
#         "Accept": "*/*",
#         "Accept-Encoding": "gzip, deflate",
#         "Accept-Language": "zh-CN,zh;q=0.9",
#         "Connection": "keep-alive",
#         "Content-Length": "240",
#         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
#         "Host": "wenshu.court.gov.cn",
#         "Origin": "http://wenshu.court.gov.cn",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36",
#         "X-Requested-With": "XMLHttpRequest",
#     }
#
# def get_guid():
#     return guid() + guid() + "-" + guid() + "-" + guid() + guid() + "-" + guid() + guid() + guid()
#
# def guid():
#     return hex(int((random.random() + 1) * 0x10000))[3:]
# guid_1 = get_guid()
# data = {"guid": guid_1, }
# session = requests.session()
# post_url = 'http://wenshu.court.gov.cn/list/list/?'+urllib.urlencode(dic2)+'&'+urllib.urlencode(dic3)
# print post_url
# list_list_result = session.post(url=post_url, data=data, headers=headers,)
# cookies = requests.utils.dict_from_cookiejar(list_list_result.cookies)
# print cookies

# import Queue
#
# test_q = Queue.Queue(maxsize=0)
# test_q.put(1)
# test_q.put(2)
# test_q.put(3)
# print test_q.get()
# if not test_q.empty():
# 	print 'not empty'
# 	while not test_q.empty():
# 		print test_q.get()

# import codecs, os
#
# if not os.path.exists("C:\\file\\skyon\\bad_req\\"):
# 	os.makedirs("C:\\file\\skyon\\bad_req\\")
# file = codecs.open("C:\\file\\skyon\\bad_req\\test.txt", 'wb', encoding='utf-8')
# file.close()

import json
a = json.loads('[]')