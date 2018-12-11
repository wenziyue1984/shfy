# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import hashlib
import json
import time, os
import re

import shfy.ConnectMiddleware as connect
from pydispatch import dispatcher
from scrapy import signals


class ShfyPipeline(object):
    def __init__(self):
        self.name = "shfy_00"
        self.txt_path_01 = connect.UsedThing.txt_file_01  # txt文件存放路径(十一个字段)
        self.txt_path_02 = connect.UsedThing.txt_file_02  # txt文件存放路径(四个字段)
        day = time.strftime("%Y%m%d", time.localtime())  # 获取今天
        self.day = str(day) + '/1/'
        self.stamp = str(time.time())

    def open_spider(self, spider):
        if spider.date:
            # 自定义模式
            # 获取爬虫的开始日期
            self.start_date = spider.s_date
            # 文件路径
            self.path_01 = self.txt_path_01 + self.day + self.name + self.start_date + '_' + self.stamp
            self.path_02 = self.txt_path_02 + self.day + self.name + self.start_date + '_' + self.stamp
        else:
            # 常规模式
            self.start_date = spider.s_date
            self.path_01 = self.txt_path_01 + self.day + self.name + self.start_date
            self.path_02 = self.txt_path_02 + self.day + self.name + self.start_date

        ###用于openspider方法中，更新crawler表内爬虫文件地址字段
        self.file_path = self.path_02 + '.txt'

        ##判断是否有爬虫解析文件存放相应的文件夹，没有创建
        if not os.path.exists(self.txt_path_01 + self.day):
            os.makedirs(self.txt_path_01 + self.day)
        if not os.path.exists(self.txt_path_02 + self.day):
            os.makedirs(self.txt_path_02 + self.day)

        ##打开解析文件，格式为tmp（结束修改为txt）
        self.file_01 = codecs.open(self.path_01 + '.tmp', 'wb', encoding='utf-8')
        self.file_02 = codecs.open(self.path_02 + '.tmp', 'wb', encoding='utf-8')

        ###获取spider_closed信号
        dispatcher.connect(self.spider_closed, signals.spider_closed)

        start_time = time.strftime('%Y-%m-%d %X', time.localtime())
        ##更新爬虫状态
        # query = connect.ConnectMiddleware.dbpool.runInteraction(self.startrun, start_time)

    def process_item(self, item, spider):
        # 每天爬取的数据都写在同一文件夹之中，一天结束则新建一个文件夹
        check_day = time.strftime("%Y%m%d", time.localtime())  # 获取今天
        if self.day[:-3] != str(check_day):
            self.file_01.close()
            # 如果已经存在同名txt文件，则先删除
            if os.path.exists(self.path_01 + '.txt'):
                os.remove(self.path_01 + '.txt')
            # 将tmp改名为txt
            if os.path.exists(self.path_01 + '.tmp'):
                os.rename(self.path_01 + '.tmp', self.path_01 + '.txt')
            # 生成MD5校验码
            # 先生成一个保存校验码的文件，然后读取原文件内容（分多次读取）生成校验码，再把校验码写入文件，关闭文件
            md5_file_01 = codecs.open(self.path_01 + '.md5', 'wb', encoding='utf-8')
            md5_line_01 = self.md5sum(self.path_01 + '.txt')
            md5_file_01.write(md5_line_01.encode('utf-8'))
            md5_file_01.close()

            # 新建另一文件夹
            if not os.path.exists(self.txt_path_01 + check_day + '/1/'):
                os.makedirs(self.txt_path_01 + check_day + '/1/')

            # 修改路径，打开新文件
            if spider.date:
                # 自定义模式
                self.path_01 = self.txt_path_01 + str(check_day) + "/1/" + \
                               self.name + self.start_date + '_' + self.stamp
                self.file_01 = codecs.open(self.path_01 + '.tmp', 'wb', encoding='utf-8')
            else:
                # 常规模式
                self.path_01 = self.txt_path_01 + str(check_day) + "/1/" + self.name + self.start_date
                self.file_01 = codecs.open(self.path_01 + '.tmp', 'wb', encoding='utf-8')

            # 对file_02执行相同操作
            self.file_02.close()
            if os.path.exists(self.path_02 + '.txt'):
                os.remove(self.path_02 + '.txt')
            if os.path.exists(self.path_02 + '.tmp'):
                os.rename(self.path_02 + '.tmp', self.path_02 + '.txt')
            md5_file_02 = codecs.open(self.path_02 + '.md5', 'wb', encoding='utf-8')
            md5_line_02 = self.md5sum(self.path_02 + '.txt')
            md5_file_02.write(md5_line_02.encode('utf-8'))
            md5_file_02.close()
            if not os.path.exists(self.txt_path_02 + check_day + '/1/'):
                os.makedirs(self.txt_path_02 + check_day + '/1/')
            if spider.date:
                self.path_02 = self.txt_path_02 + str(check_day) + "/1/" + \
                               self.name + self.start_date + '_' + self.stamp
                self.file_02 = codecs.open(self.path_02 + '.tmp', 'wb', encoding='utf-8')
            else:
                self.path_02 = self.txt_path_02 + str(check_day) + "/1/" + self.name + self.start_date
                self.file_02 = codecs.open(self.path_02 + '.tmp', 'wb', encoding='utf-8')

            # 更新self.day
            self.day = str(check_day) + "/1/"

        # line_01 = json.dumps(dict(item)) + ',\n'
        # self.file_01.write(line_01.decode('unicode_escape').encode('utf-8'))
        #
        # item2 = {'title': item['title'], 'date': item['date'], 'text': item['text'], 'link': item['link']}
        # line_02 = json.dumps(dict(item2)) + ',\n'
        # self.file_02.write(line_02.decode('unicode_escape').encode('utf-8'))

        line_01 = ('' + item['title'] + '$^$' + item['link'] + '$^$' + \
                   item['date'] + '$^$' + item['casenum'] + '$^$' + \
                   item['court'] + '$^$' + item['querydate'] + '$^$' + \
                   item['doctype'] + '$^$' + item['plaintiff'] + '$^$' + \
                   item['defendant'] + '$^$' + item['judge'] + '$^$' + \
                   item['text']).strip() + '\n'
        self.file_01.write(line_01.encode('utf-8'))

        line_02 = ('' + item['title'] + '$^$' + item['date'] + '$^$' + \
                   item['link'] + '$^$' + item['text']).strip() + '\n'
        self.file_02.write(line_02.encode('utf-8'))

        return item

    def spider_closed(self,spider,reason):
        if reason == "finished":
            # query = connect.ConnectMiddleware.dbpool.runInteraction(self.finishrun)
            finish_time = time.strftime('%Y-%m-%d %X', time.localtime())

            # line = "\r"  # 写入一个回车，用于转txt文件
            # self.file_01.write(line)
            # self.file_01.close()
            # self.file_02.write(line)
            # self.file_02.close()

            self.file_01.close()
            self.file_02.close()

            if os.path.exists(self.path_01 + '.txt'):  # 是否存在同名txt文件
                os.remove(self.path_01 + '.txt')  # 删除txt文件
            if os.path.exists(self.path_01 + '.tmp'):
                os.rename(self.path_01 + '.tmp', self.path_01 + '.txt')  # 修改名字

            if os.path.exists(self.path_02 + '.txt'):  # 是否存在同名txt文件
                os.remove(self.path_02 + '.txt')  # 删除txt文件
            if os.path.exists(self.path_02 + '.tmp'):
                os.rename(self.path_02 + '.tmp', self.path_02 + '.txt')  # 修改名字

            # 生成MD5校验码
            md5_file_01 = codecs.open(self.path_01 + '.md5', 'wb', encoding='utf-8')
            md5_line_01 = self.md5sum(self.path_01 + '.txt')
            md5_file_01.write(md5_line_01.encode('utf-8'))
            md5_file_01.close()

            md5_file_02 = codecs.open(self.path_02 + '.md5', 'wb', encoding='utf-8')
            md5_line_02 = self.md5sum(self.path_02 + '.txt')
            md5_file_02.write(md5_line_02.encode('utf-8'))
            md5_file_02.close()

            file_size = os.path.getsize(self.path_01 + '.txt')
            update_time = time.strftime('%Y-%m-%d %X', time.localtime())
            # query = connect.ConnectMiddleware.dbpool.runInteraction(self.closerun, update_time, spider, finish_time,
            #                                                         file_size)
        elif reason == "shutdown":
            print "2"
            # query = connect.ConnectMiddleware.dbpool.runInteraction(self.stoprun)
        elif reason == 'cancel':
            print '2'
            # query = connect.ConnectMiddleware.dbpool.runInteraction(self.stoprun)


    #######数据库

    # def startrun(self, tx, start_time):  # 写入数据库爬虫状态和LOG
    #     # sql = "update crawler set run_status=%s where crawl_name=%s"
    #     # tx.execute(sql, ("0", name))
    #     sql = connect.UsedThing.start_sel_sql
    #     sele = tx.execute(sql, (self.name,))
    #     if sele == 1:
    #         #sql = "update crawl_log set crawl_file_name=%s,crawl_file_format=%s,crawl_file_url=%s,crawl_starttime=%s where belong_crawler=%s"
    #         sql = connect.UsedThing.start_real_sql
    #         #start_real_sql="update crawl_log set crawl_file_name=%s,crawl_file_format=%s,crawl_file_url=%s,crawl_starttime=%s where belong_crawler=%s"
    #         tx.execute(sql, (self.name + ".txt", "txt", self.file_path, start_time, self.name))
    #     else:
    #         #sql1 = "insert into crawl_log(belong_crawler,crawl_file_name,crawl_file_format,crawl_file_url,crawl_starttime)values(%s,%s,%s,%s,%s)"
    #         sql1=connect.UsedThing.start_notreal_sql
    #         tx.execute(sql1, (self.name, self.name + ".txt", "txt", self.file_path, start_time))
    #     sql = connect.UsedThing.start_crawl_log
    #     tx.execute(sql, ("0", self.name))
    #
    # def finishrun(self, tx):####finished完成
    #     sql = connect.UsedThing.finish_crawl_sql
    #     tx.execute(sql, ("1", self.name))
    #
    # def closerun(self, tx, update_time, spider, finish_time, file_size):  # 更新数据库爬虫状态和LOG的finish_time和file_size数据（完成）
    #     sql = connect.UsedThing.close_crawl_sql
    #     tx.execute(sql, (finish_time, file_size, update_time, self.name))
    #
    # def stoprun(self, tx):  # 更新数据库爬虫状态和LOG的finish_time和file_size数据（出错或者手动停止）
    #     sql = connect.UsedThing.stop_crawl_sql
    #     tx.execute(sql, ("2", self.name))

    # md5sum
    def read_chunks(self, fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else:  # 最后要将游标放回文件开头
            fh.seek(0)

    def md5sum(self, fname):
        m = hashlib.md5()
        if isinstance(fname, basestring) and os.path.exists(fname):
            with open(fname, "rb") as fh:
                for chunk in self.read_chunks(fh):
                    m.update(chunk)
        else:
            return ""
        return m.hexdigest()