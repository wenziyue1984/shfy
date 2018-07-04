# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ShfyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()  ##标题
    link = scrapy.Field()  ##连接
    date = scrapy.Field()  ##结案日期
    text = scrapy.Field()  ###内容
    casenum = scrapy.Field()  ###案号
    querydate = scrapy.Field()  ###查询日期
    doctype = scrapy.Field()  ###判决书类型
    court = scrapy.Field()  ##法院
    judge = scrapy.Field()  ###审判长
    plaintiff = scrapy.Field()  ##原告
    defendant = scrapy.Field()  ##被告
