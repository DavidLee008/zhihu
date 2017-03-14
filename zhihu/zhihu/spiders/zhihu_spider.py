# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from zhihu.items import ZhihuItem
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spider import BaseSpider
import urlparse
from scrapy import log

class ZhihuSpider(BaseSpider):
    name = "zhihu_spider"
    #allowed_domains = ["zhihu.com"]
    start_urls = (
        'https://www.zhihu.com/',
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
        return [Request("https://www.zhihu.com/login/phone_num",meta={'cookiejar':1},headers = self.headers_zhihu,callback=self.post_login)]

    def post_login(self,response):
        print 'post_login'
        xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]  #不见【0】输出错误

        print 'xsrf'+xsrf

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

    def after_login(self,response):
        print 'after_login'
        print response.body    # 返回msg
        for url in self.start_urls:
            print 'url...................'+url
            yield self.make_requests_from_url(url,response)


    def make_requests_from_url(self, url,response):
        return Request(url,dont_filter=True, meta = {
                 'cookiejar':response.meta['cookiejar'],
                  'dont_redirect': True,
                  'handle_httpstatus_list': [301,302]
            },
                 #      callback=self.parse
                       )


    def parse(self, response):
        items = []

        problem = Selector(response)

        item = ZhihuItem()
        name = problem.xpath('//span[@class="name"]/text()').extract()
        print name
        item['name'] = name
        urls = problem.xpath('//a[@class="question_link"]/@href').extract()

        print urls
        item['urls'] = urls
        print 'response ............url '+response.url
        item['url'] = response.url
        print item['url']


        items.append(item)
        yield item                                                     #返回item
        for url in urls:
            print url

            yield scrapy.Request(urlparse.urljoin('https://www.zhihu.com', url),dont_filter=True,   #直接使用url会报错
                 meta = {
                 'cookiejar':response.meta['cookiejar'],               #设置cookiejar
                  'dont_redirect': True,                               #防止重定向
                  'handle_httpstatus_list': [301,302]
            },
                       callback=self.parse
                       )
