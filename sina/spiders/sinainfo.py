# -*- coding: utf-8 -*-
import scrapy
import sys
import os

from sina.items import SinaItem

class SinainfoSpider(scrapy.Spider):
    name = 'sinainfo'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://news.sina.com.cn/guide/']

    def parse(self, response):
        items = []
        parentTitle = response.xpath("//div[@id='tab01']/div/h3/a/text()").extract()
        parentUrls = response.xpath("//div[@id='tab01']/div/h3/a/@href").extract()

        subUrls = response.xpath('//div[@id="tab01"]/div/ul/li/a/@href').extract()
        subTitle = response.xpath('//div[@id="tab01"]/div/ul/li/a/text()').extract()

        for i in range(0,len(parentTitle)):
            parentFilename = "./Data/" + parentTitle[i]

            if (not os.path.exists(parentFilename)):
                os.makedirs(parentFilename)



            for j in range(0,len(subUrls)):
                item = SinaItem()

                item['parentTitle'] = parentTitle[i]
                item['parentUrls'] = parentUrls[i]

                if_belong = subUrls[j].startswith(item['parentUrls'])

                if (if_belong):
                    subFilename = parentFilename + '/' + subTitle[j]

                    if (not os.path.exists(subFilename)):
                        os.makedirs(subFilename)

                    item['subUrls'] = subUrls[j]
                    item['subTitle'] = subTitle[j]
                    item['subFilename'] = subFilename
                    items.append(item)

        for item in items:
            yield scrapy.Request(url=item['subUrls'],\
                                 meta={'meta_1':item},callback=self.second_parse)

    def second_parse(self,response):
        meta_1 = response.meta['meta_1']
        sonUrls = response.xpath('//a/@href').extract()

        items = []
        for i in range(0,len(sonUrls)):
            if_belong = sonUrls[i].endswith('.shtml') and sonUrls[i].startswith(\
                meta_1['parentUrls'])

            if (if_belong):
                item = SinaItem()
                item['parentTitle'] = meta_1['parentTitle']
                item['parentUrls'] = meta_1['parentUrls']
                item['subTitle'] = meta_1['subTitle']
                item['subUrls'] = meta_1['subUrls']
                item['subFilename'] = meta_1['subFilename']
                item['sonUrls'] = sonUrls[i]
                items.append(item)

        for item in items:
            yield scrapy.Request(url=item['sonUrls'], \
                                 meta={'meta_2': item}, callback=self.detail_parse)

    def detail_parse(self, response):
        item = response.meta['meta_2']
        content = ""
        head = response.xpath('//h1[@id="main_title"]/text()')
        content_list = response.xpath('//div[@id="artibody"]/p/text()').extract()
        # 将p标签里的文本内容合并到一起
        for content_one in content_list:
            content += content_one
        item['head'] = head
        item['content'] = content



