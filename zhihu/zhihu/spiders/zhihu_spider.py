# -*- coding: utf-8 -*-
import scrapy
#from bs4 import BeautifulSoup
from zhihu.items import ZhihuItem
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.spider import BaseSpider
import urlparse
from scrapy import log
from PIL import Image
from StringIO import StringIO
import json


class ZhihuSpider(BaseSpider):
    name = "zhihu_spider"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        'https://www.zhihu.com/#signin'
    ]

    rules = (
        Rule(LinkExtractor(allow = ('/question/\d+')), callback='parse_qusetion'),
    )


    headers_zhihu = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36",
        "Referer": "http://www.zhihu.com"
        # 'cookie':cookie


    }


    def start_requests(self):
        return [Request("https://www.zhihu.com/login/phone_num",headers = self.headers_zhihu,meta={'cookiejar':1},#callback=self.post_login
                        callback=self.init)]

    def init(self,response):
        self.xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]  #不见【0】输出错误
        return Request('https://www.zhihu.com/captcha.gif?r=1490793697630&type=login', callback=self.login)

    def getcapid(self,response):
        Image.open(StringIO(response.body)).show()
        return raw_input('输入验证码：')

    def login(self,response):

        return FormRequest('https://www.zhihu.com/login/phone_num',
                           headers = self.headers_zhihu,
                           formdata = {
                               '_xsrf':self.xsrf,
                               'phone_num':'18575607945',  #这里的参数值不能去掉''
                               'password':'82883613',
                               'remember_me':'true',
                               'captcha':self.getcapid(response)
                           },
                           callback = self.after_login,
                           #dont_filter = True
                           )


#    def post_login(self,response):
#        self.log("preparing login...")
#        xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]  #不见【0】输出错误
#
#        self.log(xsrf)
#        #print 'xsrf'+xsrf

#        return [FormRequest('https://www.zhihu.com/login/phone_num',
#                meta={'cookiejar':response.meta['cookiejar']},
#                headers = self.headers_zhihu,
#                formdata = {
#                    '_xsrf':xsrf,
#                    'phone_num':'18575607945',  #这里的参数值不能去掉''
#                    'password':'82883613',
#                    'remember_me':'true',
#                },
#                callback = self.after_login,
                #dont_filter = True

#        )]
    #def after_login(self,response):
    #    print 'after_login'
    #    print response.body    # 返回msg
    #    for url in self.start_urls:
    #        print 'url...................'+url
    #        yield self.make_requests_from_url(url,response)
    def after_login(self,response):
        #print response.body
        for url in self.start_urls:
        #if json.loads(response.body)['r'] == 0:
            yield Request(url,headers = self.headers_zhihu,callback=self.parse_question,dont_filter = True
                            )

    #def request_question(self,request):
        #return Request(request.url,meta={'cookiejar':1},headers = self.headers_zhihu,callback=self.parse_question,
                         #)


    #def make_requests_from_url(self, url,response):
    #    return Request(url,dont_filter=True, meta = {
    #             'cookiejar':response.meta['cookiejar'],
    #              'dont_redirect': True,
    #              'handle_httpstatus_list': [301,302]
    #        },
    #             #      callback=self.parse
    #                   )


    def parse_question(self, response):
        #items = []
        print 'xsrf'+self.xsrf
        print response.body
        problem = Selector(response)

        item = ZhihuItem()

        title = problem.xpath('//h2/a[@class="question_link"]/text()').extract()
        #print title
        item['title'] = title
        #item['title'] = [n.encode('utf-8') for n in title]

        urls = problem.xpath('//h2/a[@class="question_link"]/@href').extract()
        print urls
        item['urls'] = urls
        yield item


        request = Request(url='https://www.zhihu.com/', dont_filter=True)
        request.meta['PhantomJS'] = True

        #print 'response ............url '+response.url
        #item['url'] = response.url
        #print item['url']


        #items.append(item)
        #yield item                                                     #返回item
        #for url in urls:
            #print url

        #yield scrapy.Request(urlparse.urljoin('https://www.zhihu.com', url),dont_filter=True,   #直接使用url会报错
                 #meta = {
                 #'cookiejar':response.meta['cookiejar'],               #设置cookiejar
                  #'dont_redirect': True,                               #防止重定向
                  #'handle_httpstatus_list': [301,302]
            #},
                       #callback=self.parse
                       #)
