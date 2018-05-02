# -*- coding: utf-8 -*-
import scrapy


class VoteSpider(scrapy.Spider):
    name = 'vote'
    allowed_domains = ['vote.com']
    start_urls = ['http://vote.com/']

    def parse(self, response):
        pass
