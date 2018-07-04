# -*- coding: utf-8 -*-
import random

import binascii
import urllib

import execjs
from scrapy.spiders import Spider
import datetime, time
from scrapy import FormRequest

import shfy.ConnectMiddleware as connect
import json, re, requests
from scrapy import Request
import os
# import PyV8

import sys

from shfy.items import ShfyItem

reload(sys)
sys.setdefaultencoding('utf-8')


class ShfySpider(Spider):
	name = 'shfy'
	domain = "court.gov.cn"
	start_urls = ['http://wenshu.court.gov.cn/Index']
	# start_urls = ['http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=bd135174-5ee7-4ab5-ab5d-a72000aea26a']
	# start_urls = ['http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=c8b19260-b353-49ce-8d3f-f9dbc0d87e43']

	# 日志文件夹
	if not os.path.exists(connect.UsedThing.log_path + time.strftime("%Y%m%d", time.localtime()) + "/"):
		os.makedirs(connect.UsedThing.log_path + time.strftime("%Y%m%d", time.localtime()) + "/")

	def __init__(self, date=None):
		if date:
			# 自定义模式
			Spider.date = date
			d = re.findall('\d{4}-\d{2}-\d{2}', date)
			if len(d) == 2:
				self.start_date = d[0]
				self.stop_date = d[1]
				Spider.s_date = self.start_date
			else:
				pass
		else:
			# 常规模式
			# 读文件找到开始日期
			Spider.date = None
			date_file = open('date_recode.txt', 'a')
			date_file.close()
			date_file = open('date_recode.txt', 'r')
			date_recode = date_file.read().replace('\n', '')
			date_file.close()
			# 修改文件中的日期
			recode_today = time.strftime("%Y-%m-%d", time.localtime())
			date_file = open('date_recode.txt', 'wb')
			date_file.write(recode_today)
			date_file.close()
			# 设定开始日期与结束日期
			date_txt = re.findall('\d{4}-\d{2}-\d{2}', date_recode)  # 找到文件中所有日期
			if date_txt:
				self.start_date = date_txt[0]
				Spider.s_date = date_txt[0]
			else:
				pass
			self.stop_date = str(datetime.date.today() + datetime.timedelta(-1))
			print self.start_date, self.stop_date

		self.court_list = connect.UsedThing.court_list

	def start_requests(self):
		# start_time = datetime.datetime.strptime('2018-03-07', '%Y-%m-%d')
		# stop_time = datetime.datetime.strptime('2018-03-07', '%Y-%m-%d')
		start_time = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
		stop_time = datetime.datetime.strptime(self.stop_date, '%Y-%m-%d')
		# 遍历查询范围内的每一天
		for i in range((stop_time - start_time).days + 1):
			check_time_str = (start_time + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
			for court_name in self.court_list:
				# court_name = u"上海市徐汇区人民法院"  # 测试
				print court_name, check_time_str
				# 1.获取number
				guid = self.get_guid()
				post_url = 'http://wenshu.court.gov.cn/ValiCode/GetCode'
				yield FormRequest(post_url, formdata={'guid': guid, }, callback=self.get_number,
								  meta={'guid': guid, 'court': court_name, 'date': check_time_str, }, dont_filter=True, )

	def get_number(self, response):
		# print response.body
		# 向list/list发请求，获取cookie里的vjkl5
		court_name = response.meta['court']
		check_time_str = response.meta['date']
		number = response.body
		guid = response.meta['guid']
		get_url = 'http://wenshu.court.gov.cn/list/list/?sorttype=1&&number='+number+'&guid='+guid+'conditions=searchWord+' + court_name + '+SLFY++法院名称:' + court_name + '&conditions=searchWord++CPRQ++裁判日期:' + check_time_str + '%20TO%20' + check_time_str
		yield Request(get_url, callback=self.get_vl5x, dont_filter=True,
							 meta={'guid': guid, 'court': court_name, 'date': check_time_str, 'number': number},)

	def get_vl5x(self, response):

		court_name = response.meta['court']
		check_time_str = response.meta['date']
		number = response.meta['number']
		guid = response.meta['guid']
		# 提取vjkl5,转为vl5x，发送请求
		cookie = response.headers.getlist('Set-Cookie')
		if len(cookie) == 1:
			vjkl5 = re.findall('vjkl5=(.*?);', cookie[0])
			if len(vjkl5) == 1:
				vjkl5 = vjkl5[0]
				# print vjkl5, number
				jsstr = self.get_js()
				ctx = execjs.compile(jsstr)
				vl5x = ctx.call('getKey', vjkl5)
				data = {
					"Param": '法院名称:' + court_name + ',裁判日期:' + check_time_str + '  TO ' + check_time_str,
					"Index": "1", "Page": "5", "Order": "法院层级", "Direction": "asc",
					"vl5x": vl5x, "number": number, "guid": guid, }
				post_url = 'http://wenshu.court.gov.cn/List/ListContent'
				header = {
					'Cookie': ['vjkl5='+vjkl5,],
				}
				yield FormRequest(post_url, formdata=data, callback=self.get_total_old, dont_filter=True, headers=header,
										 meta={'vl5x': vl5x , 'court': court_name, 'date': check_time_str, 'guid': guid ,
											   'number': number , 'vjkl5': vjkl5})

	def get_total_old(self, response):
		print response.body
		court_name = response.meta['court']
		check_time_str = response.meta['date']
		number = response.meta['number']
		guid = response.meta['guid']
		vl5x = response.meta['vl5x']
		vjkl5 = response.meta['vjkl5']
		body_text = response.body.replace("\\", "")
		try:
			dict_text = json.loads(body_text[1:-1])
		except:
			dict_text = ""
		if dict_text:
			try:
				full_num = int(dict_text[0]["Count"])
				if full_num % 20 == 0:
					loop_time = full_num // 20
				else:
					loop_time = full_num // 20 + 1
				for page_index in range(1, loop_time + 1):
					if page_index <= 100:
						data = {
							"Param": '法院名称:' + court_name + ',裁判日期:' + check_time_str + '  TO ' + check_time_str,
							"Index": str(page_index), "Page": "20", "Order": "法院层级", "Direction": "asc",
							"vl5x": vl5x, "number": number, "guid": guid,
						}
						header = {
							'Cookie': ['vjkl5=' + vjkl5],
						}
						post_url = 'http://wenshu.court.gov.cn/List/ListContent'
						yield FormRequest(post_url, formdata=data, callback=self.get_DocID, dont_filter=True, headers=header,
												 meta={'vjkl5': vjkl5})
			except:
				pass

	def get_DocID(self, response):
		print 'get_DocID:', response.body
		body_text = response.body.replace("\\", "")
		# print body_text
		# print type(body_text)
		try:
			dict_text = json.loads(body_text[1:-1])
		except:
			dict_text = ""
		if dict_text:
			id_num = len(dict_text)
			for id_index in range(1, id_num):
				book_id = dict_text[id_index][u'文书ID']
				case_num = dict_text[id_index][u'案号']
				date_text = dict_text[id_index][u'裁判日期']
				title = dict_text[id_index][u'案件名称']
				doc_type = dict_text[id_index][u"案件类型"]
				court = dict_text[id_index][u"法院名称"]
				url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=" + book_id
				yield Request(url,
							  meta={"date_text": date_text, "title": title, "case_num": case_num,
									"doc_type": doc_type, "court": court,},
							  callback=self.parse, dont_filter=True,)

	def parse(self, response):
		temp = response.xpath("/html/body/div//text()").extract()
		if not temp:
			req = response.request
			req.meta["change_proxy"] = True
			return req
		else:
			# try:
			type_list = {"1": u"刑事", "2": u"民事", "3": u"行政", "4": u"赔偿"}
			date_text = response.meta['date_text']
			title = response.meta['title']
			case_num = response.meta['case_num']
			doc_type = response.meta['doc_type']
			court = response.meta['court']

			news = ShfyItem()
			news['date'] = date_text
			news['title'] = title.replace(u"xa0", " ").replace(u"\u3000", " ")
			news["link"] = response.url
			# 案号
			news['casenum'] = case_num.strip()
			# 查询日期
			news['querydate'] = time.strftime('%Y-%m-%d', time.localtime())
			if doc_type in type_list:
				news['doctype'] = type_list[doc_type]
			else:
				news['doctype'] = ""
			temp = response.xpath("/html/body/div//text()").extract()
			content = ''
			if temp:
				for te in temp:
					content += " " + te.replace('"', '').replace('\\', '').replace('	', '').strip()
				news['text'] = content.strip().replace('\r\n', '').replace('"', '').replace(' ', '').replace('\\',
																											 '').replace(
					'\n', '').replace(u"xa0", " ").replace(u"\u3000", " ").strip()
			else:
				news['text'] = ''

			news['court'] = court.replace(u"xa0", " ").replace(u"\u3000", " ").strip()
			# 审判员
			temp = response.xpath("/html/body/div")
			judge = ""
			for tr_index in range(len(temp) - 1, -1, -1):
				tr_text = temp[tr_index].xpath(".//text()").extract()
				judge_text = "".join(tr_text).replace(u"\xa0", "").replace("\r\n", "").replace("\n", "").replace("\t",
																												 "").replace(
					" ", "").strip()
				judge = re.findall(u"审判长.+", judge_text)
				if judge:
					judge = judge[0]
					break
			if judge:
				news['judge'] = judge
			else:
				judge2 = ""
				for tr_index in range(len(temp) - 1, -1, -1):
					tr_text = temp[tr_index].xpath(".//text()").extract()
					judge2_text = "".join(tr_text).replace(u"\xa0", "").replace("\r\n", "").replace("\n", "").replace(
						"\t", "").replace(" ", "").strip()
					judge2 = re.findall(u"审判员.+", judge2_text)
					if judge2:
						judge2 = judge2[0]
						break
				if judge2:
					news['judge'] = judge2
				else:
					judge3 = ""
					for tr_index in range(len(temp) - 1, -1, -1):
						tr_text = temp[tr_index].xpath(".//text()").extract()
						judge3_text = "".join(tr_text).replace(u"\xa0", "").replace("\r\n", "").replace("\n",
																										"").replace(" ",
																													"").replace(
							"\t",
							"").strip()
						judge3 = re.findall(u"代理审判员.+", judge3_text)
						if judge3:
							judge3 = judge3[0]
							break
					if judge3:
						news['judge'] = judge3
					else:
						news['judge'] = ""
			news['judge'] = news['judge'].replace(u"xa0", " ").replace(u"\u3000", " ")
			# 原告
			plaintiffset = set()
			rel_plaintiffset = set()
			up_check = ""
			app_check = ""
			if temp:
				plaintiff_content = content.replace('\n', '').replace("\r\n", "").replace("\t", "").replace(u"\xa0",
																											"").replace(
					u' ', '').replace(case_num, u'。').replace(u'，', '\n').replace(u'。', '\n').replace(u',',
																									  '\n').replace(
					u'\.', '\n').replace(u"：", ":")

				plaintiff_info = re.findall(u"\\n原告人:(.+)", plaintiff_content)
				if not plaintiff_info:
					plaintiff_info = re.findall(u"\\n原告人(.+)", plaintiff_content)
				if not plaintiff_info:
					plaintiff_info = re.findall(u"\\n原告:(.+)", plaintiff_content)
				if not plaintiff_info:
					plaintiff_info = re.findall(u"\\n原告(.+)", plaintiff_content)

				if re.findall(u"号原告(.+)", plaintiff_content):
					for n in re.findall(u"号原告(.+)", plaintiff_content):
						plaintiff_info.append(n)
				if re.findall(u"号原告人(.+)", plaintiff_content):
					for n in re.findall(u"号原告人(.+)", plaintiff_content):
						plaintiff_info.append(n)
				# 上述人
				if re.findall(u"\\n上诉人（.*?）(.+)", plaintiff_content):
					up_check = "1"
					for n in re.findall(u"\\n上诉人（.*?）(.+)", plaintiff_content):
						plaintiff_info.append(n)
				elif re.findall(u"\\n上诉人(.+)", plaintiff_content):
					up_check = "1"
					for n in re.findall(u"\\n上诉人(.+)", plaintiff_content):
						plaintiff_info.append(n)
				# 申请执行人，申请人
				if re.findall(u"\\n[一 二 三 四 再 终]{0,1}[审]{0,1}申请人（.*?）(.+)", plaintiff_content):
					app_check = "1"
					for n in re.findall(u"\\n[一 二 三 四 再 终]{0,1}[审]{0,1}申请人（.*?）(.+)", plaintiff_content):
						plaintiff_info.append(n)
				elif re.findall(u"\\n[一 二 三 四 再 终]{0,1}[审]{0,1}申请人(.+)", plaintiff_content):
					app_check = "1"
					for n in re.findall(u"\\n[一 二 三 四 再 终]{0,1}[审]{0,1}申请.*人(.+)", plaintiff_content):
						plaintiff_info.append(n)
				for plaintiff in plaintiff_info:
					plaint_long = re.findall(
						plaintiff.replace("(", "\(").replace(")", "\)").replace("*", "\*").replace(".",
																								   "\.").replace(
							"^", "\^"), plaintiff_content)
					if len(plaint_long) >= 1:
						plaintiffset.add(plaintiff)
						rel_plaintiffset.add(plaintiff)
			for i in plaintiffset:
				for j in plaintiffset:
					if j == i:
						pass
					else:
						if len(re.findall(
								j.replace(u"（", "").replace(u"）", "").replace(u"：", "").replace("(", "").replace(")",
																												 "").replace(
									":", ""), i)) > 0:
							if i in rel_plaintiffset:
								rel_plaintiffset.remove(i)
			if not plaintiffset:
				rel_plaintiffset.add('')
			plaintiffs = ''
			for name in rel_plaintiffset:
				# print name
				plaintiffs = plaintiffs + name.replace(u"（", "").replace(u"）", "").replace(u"：", "").replace("(",
																											 "").replace(
					")", "").replace(":", "").replace(u"xa0", " ").replace(u"\u3000", " ") + ","
			news['plaintiff'] = plaintiffs[:-1]
			# 被告，被上诉人，被执行人，被申请人
			defendantset = set()
			rel_defendantset = set()
			if temp:
				defendant_info = []
				defendant_content = content.replace('\n', '').replace("\r\n", "").replace("\t", "").replace(u"\xa0",
																											"").replace(
					u' ', '').replace(case_num, u'。').replace(u'，', '\n').replace(u'。', '\n').replace(u',',
																									  '\n').replace(
					u'\.', '\n').replace(u"：", ":")
				if re.findall(u"\\n罪犯(.+)", defendant_content):
					for n in re.findall(u"\\n罪犯(.+)", defendant_content):
						defendant_info.append(n)
				elif up_check:
					# 被上述人
					if re.findall(u"被上诉人（.*?）(.+)", defendant_content):
						for n in re.findall(u"被上诉人（.*?）(.+)", defendant_content):
							defendant_info.append(n)
					elif re.findall(u"被上诉人(.+)", defendant_content):
						for n in re.findall(u"被上诉人(.+)", defendant_content):
							defendant_info.append(n)
				elif app_check:
					if re.findall(u"\\n被申请人（.*?）(.+)", defendant_content):
						defendant_info.append(re.findall(u"\\n被申请人（.*?）(.+)", defendant_content)[0])
					elif re.findall(u"\\n被申请人(.+)", defendant_content):
						defendant_info.append(re.findall(u"\\n被申请人(.+)", defendant_content)[0])
				else:
					defendant_info = re.findall(u"\\n被告人:(.+)", defendant_content)
					if not defendant_info:
						defendant_info = re.findall(u"\\n被告人(.+)", defendant_content)
					if not defendant_info:
						defendant_info = re.findall(u"\\n被告:(.+)", defendant_content)
					if not defendant_info:
						defendant_info = re.findall(u"\\n被告(.+)", defendant_content)
					# 被执行人
					if re.findall(u"被执行人(.+)", defendant_content):
						for n in re.findall(u"被执行人(.+)", defendant_content):
							defendant_info.append(n)

				for defendant in defendant_info:
					if len(re.findall(
							defendant.replace("(", "\(").replace(")", "\)").replace("*", "\*").replace(".",
																									   "\.").replace(
								"^", "\^"), defendant_content)) > 1:
						defendantset.add(defendant)
						rel_defendantset.add(defendant)
						# if re.findall(u"被申请人(.+)", defendant_content):
						#     rel_defendantset.add(re.findall(u"被申请人(.+)", defendant_content)[0])
			for i in defendantset:
				for j in defendantset:
					if j == i:
						pass
					else:
						defendant_long = re.findall(j.replace(":", ""), i)
						if len(defendant_long) > 0:
							if i in rel_defendantset:
								rel_defendantset.remove(i)
							else:
								pass
			if not defendantset:
				rel_defendantset.add('')
			# log.msg(': '.join([response.url, news['title']]), level=log.INFO)
			defendant_final = ""
			for name in defendantset:
				defendant_final += name.replace(u"（", "").replace(u"）", "").replace(u"：", "").replace("(", "").replace(
					")", "").replace(":", "").replace(u"xa0", " ").replace(u"\u3000", " ") + ","
			news['defendant'] = defendant_final[:-1]
			# print news
			return news

	# def pyv8_js(self, cookie):
	#     ctxt = PyV8.JSContext()
	#     ctxt.enter()
	#     with open(r'/home/skyon/Spider_completed/shfy/shfy/decode-result.js') as f:
	#         jsdata = f.read()
	#         ctxt.eval(jsdata)
	#         get_key = ctxt.locals.getKey
	#         vl5x = get_key(cookie)
	#         return vl5x

	def get_js(self):
		# f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
		f = open(connect.UsedThing.js_path, 'r')
		line = f.readline()
		htmlstr = ''
		while line:
			htmlstr = htmlstr + line
			line = f.readline()
		return htmlstr

	def get_guid(self):
		return self.guid() + self.guid() + "-" + self.guid() + "-" + self.guid() + self.guid() + "-" + self.guid() + self.guid() + self.guid()

	def guid(self):
		return hex(int((random.random() + 1) * 0x10000))[3:]

	def str_16(self, cstr):
		str_tmp = binascii.b2a_hex(cstr).upper()
		str_add = ''
		index = 0
		while index < len(str_tmp):
			str_add += '%' + str_tmp[index: index + 2]
			index += 2
		return str_add
