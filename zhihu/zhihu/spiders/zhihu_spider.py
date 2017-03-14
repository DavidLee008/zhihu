# -*- coding: utf-8 -*-
import scrapy
#from bs4 import BeautifulSoup
from zhihu.items import ZhihuItem
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.spider import BaseSpider
import urlparse
from scrapy import log
from scrapy_splash import SplashRequest
from scrapy_splash import SplashMiddleware

class ZhihuSpider(BaseSpider):
    name = "zhihu_spider"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        'https://www.zhihu.com/topic/19562832/hot'
    ]

    rules = (
        Rule(LinkExtractor(allow = ('/question/\d+')), process_request='request_question'),
    )


    headers_zhihu = {
           'Host':'www.zhihu.com ',
           'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding':'gzip,deflate,sdch',
           'Referer':'https://www.zhihu.com ',
           'If-None-Match':"FpeHbcRb4rpt_GuDL6-34nrLgGKd.gz",
           'Cache-Control':'max-age=0',
           'Connection':'keep-alive'
          # 'cookie':cookie


    }


    def start_requests(self):
        return [SplashRequest("https://www.zhihu.com/login/phone_num",meta={'cookiejar':1},headers = self.headers_zhihu,callback=self.post_login)]

    def post_login(self,response):
        self.log("preparing login...")
        xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]  #不见【0】输出错误

        self.log(xsrf)
        #print 'xsrf'+xsrf

        return [FormRequest('https://www.zhihu.com/login/phone_num',
                method='POST',
                meta = {
                    'cookiejar': response.meta['cookiejar'],
                    '_xsrf':xsrf

                },

                headers = self.headers_zhihu,

                formdata = {
                    'phone_num':'18575607945',  #这里的参数值不能去掉''
                    'password':'82883613',
                     '_xsrf':xsrf
                },
                callback = self.after_login,
                #dont_filter = True

        )]
    #def after_login(self,response):
    #    print 'after_login'
    #    print response.body    # 返回msg
    #    for url in self.start_urls:
    #        print 'url...................'+url
    #        yield self.make_requests_from_url(url,response)
    def after_login(self,response):
        for url in self.start_urls:
            yield SplashRequest(url,self.parse,args={'wait':'0.5'},meta={'cookiejar':1},headers = self.headers_zhihu)

    def request_question(self,request):
        return SplashRequest(request.url,meta={'cookiejar':1},headers = self.headers_zhihu,callback=self.parse)


    #def make_requests_from_url(self, url,response):
    #    return Request(url,dont_filter=True, meta = {
    #             'cookiejar':response.meta['cookiejar'],
    #              'dont_redirect': True,
    #              'handle_httpstatus_list': [301,302]
    #        },
    #             #      callback=self.parse
    #                   )


    def parse(self, response):
        #items = []

        problem = Selector(response)

        item = ZhihuItem()

        title = problem.xpath('//h2/a[@class="question_link"]/text()').extract()
        #print title
        item['title'] = title
        #item['title'] = [n.encode('utf-8') for n in title]

        urls = problem.xpath('//h2/a[@class="question_link"]/@href').extract()
        #print urls
        item['urls'] = urls
        yield item

        #print 'response ............url '+response.url
        #item['url'] = response.url
        #print item['url']


        #items.append(item)
        #yield item                                                     #返回item
        #for url in urls:
            #print url

            #yield scrapy.Request(urlparse.urljoin('https://www.zhihu.com', url),dont_filter=True,   #直接使用url会报错
            #     meta = {
            #     'cookiejar':response.meta['cookiejar'],               #设置cookiejar
            #      'dont_redirect': True,                               #防止重定向
            #      'handle_httpstatus_list': [301,302]
            #},
            #           callback=self.parse
            #           )
