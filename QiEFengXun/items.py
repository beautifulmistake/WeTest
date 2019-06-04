# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QiefengxunItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 一级分类
    maintypename = scrapy.Field()
    # 二级分类
    pName = scrapy.Field()
    # 三级分类
    type_name = scrapy.Field()
    # APP名称
    app_name = scrapy.Field()
    # APP详情页链接
    app_detail = scrapy.Field()
