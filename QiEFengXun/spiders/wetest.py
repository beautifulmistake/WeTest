import json
from urllib import parse
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_redis.spiders import RedisSpider
from twisted.internet.error import TCPTimedOutError, DNSLookupError

from QiEFengXun.items import QiefengxunItem


class WeTestSpider(RedisSpider):
    # 爬虫名称
    name = 'wetest'
    # redis_key
    redis_key = "WeTestSpider:start_urls"

    def __init__(self):
        # URL 参数：typeId     platformId      page默认是0
        self.base_url = "https://fsight.qq.com/AllTypeGames?typeId={}&platformId={}&page={}"
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
        }
        self.file_path = r'F:\project\QiEFengXun\wetest.json'
        # 拼接完整的详情页链接
        self.base = "https://fsight.qq.com"
        # 全局的默认值
        self.default_value = '暂无'

    def parse_err(self, failure):
        """
        处理各种异常，将请求失败的Request自定义处理方式
        :param failure:
        :return:
        """
        if failure.check(TimeoutError, TCPTimedOutError, DNSLookupError):
            request = failure.request
            self.server.rpush(self.redis_key, request)
        if failure.check(HttpError):
            response = failure.value.response
            self.server.rpush(self.redis_key, response.url)
        return

    def start_requests(self):
        """
        生成请求
        :return:
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:1]
        for line in lines:
            line = json.loads(line, encoding='utf-8')
            # 获取信息
            maintypename = line['maintypename']
            pName = line['pName']
            platformId = line['platformId']
            type_id = line['type_id']
            type_name = line['type_name']
            yield scrapy.Request(url=self.base_url.format(type_id, platformId, 0), headers=self.headers, meta={
                'maintypename': maintypename, 'pName': pName, 'type_name': type_name, 'current_page': 0,
                'type_id': type_id, 'platformId': platformId
            }, callback=self.get_page, errback=self.parse_err, dont_filter=True)

    def get_page(self, response):
        """
        解析响应
        :param response:
        :return:
        """
        print("查看获取的响应：", response.text)
        # 获取所有的a标签，包含详情页链接和APP名称
        apps = response.xpath('//ul/li/p/a')
        if apps:
            # 创建item
            item = QiefengxunItem()
            # 获取APP信息
            maintypename = response.meta['maintypename']
            pName = response.meta['pName']
            type_name = response.meta['type_name']
            current_page = response.meta['current_page']
            type_id = response.meta['type_id']
            platformId = response.meta['platformId']
            for app in apps:
                item['app_name'] = app.xpath('./text()').extract_first() if \
                    app.xpath('./text()').extract_first() else self.default_value
                item['app_detail'] = parse.urljoin(self.base, app.xpath('./@href').extract_first()) \
                    if app.xpath('./@href').extract_first() else self.default_value
                item['maintypename'] = maintypename if maintypename else self.default_value
                item['pName'] = pName if pName else self.default_value
                item['type_name'] = type_name if type_name else self.default_value
                yield item
            next_url = self.base_url.format(type_id, platformId, current_page+1)
            yield scrapy.Request(url=next_url, headers=self.headers, meta={
                'maintypename': maintypename, 'pName': pName, 'type_name': type_name, 'current_page': current_page+1,
                'type_id': type_id, 'platformId': platformId
            }, callback=self.get_page, errback=self.parse_err, dont_filter=True)
