# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from lxml import etree
import requests
import re
import os
import json


COMPLETED_FILE_NAME = 'completed_items'

class ThepaperSpider(object):
    def __init__(self, index_url):
        self._index_url = index_url
        self._last_time = None
        # load completed items, use redis is better
        self._completed_items = []

        if os.path.exists(COMPLETED_FILE_NAME):
            with open(COMPLETED_FILE_NAME, 'r') as f:
                self._completed_items = json.load(f)


    def start(self):
        self.parse_index()
        # write completed items
        with open(COMPLETED_FILE_NAME, 'w') as f:
            json.dump(self._completed_items, f)


    def parse_index(self):
        response = requests.get(self._index_url)
        index_content = response.content

        match_obj = re.search('var\s?g_pageidx\s?=\s?(\d);', index_content)
        self._g_pageidx = int(match_obj.group(1))

        base_url_match_obj = re.search('load_index\.jsp\?nodeids=.*?&topCids=.*?\&', index_content)
        self._ajax_base_url = base_url_match_obj.group()

        last_time_match_obj = re.search('lastTime=\"(\d{13})\"', index_content)
        self._last_time = last_time_match_obj.group(1)

        etree_obj = etree.HTML(index_content)
        item_urls = etree_obj.xpath('//div[@id="indexScroll"]/div/div/div[@class="news_tu"]/a/@data-id')
        self.get_item_detail(item_urls)

        while True:
            self._g_pageidx += 1
            has_next = self.get_ajax_items(self._ajax_base_url, self._g_pageidx, self._last_time)
            if not has_next:
                break

    def get_ajax_items(self, base_url, g_pageidx, last_time):
        ajax_url = 'https://www.thepaper.cn/' + base_url + 'pageidx=' + str(g_pageidx) + '&lastTime=' + self._last_time
        response = requests.get(ajax_url)
        has_content = len(response.content)>0
        if has_content:
            etree_obj = etree.HTML(response.content)
            item_urls = etree_obj.xpath('//div/div[@class="news_tu"]/a/@data-id')
            self.get_item_detail(item_urls)
        return has_content

    def get_item_detail(self, item_list):
        base_url = 'https://www.thepaper.cn/newsDetail_forward_'
        for i in item_list:
            # skip dulplication
            if i in self._completed_items:
                continue
            else:
                self._completed_items.append(i)
            url = base_url + i
            response = requests.get(url)
            print url
            self.parse_detail(response.content)


    def parse_detail(self, content):
        etree_obj = etree.HTML(content)
        news_title = etree_obj.xpath('//h1[@class="news_title"]/text()')
        if isinstance(news_title, list) and len(news_title):
            news_title = news_title[0]
        else:
            return
        news_body = etree_obj.xpath('//div[@class="news_txt"]')[0]
        body_str = etree.tostring(news_body, encoding='utf-8')
        with open(news_title, 'w+') as f:
            f.write(body_str)


if __name__ == '__main__':
    '''
        Usage: python spider.py https://www.thepaper.cn/channel_25951
    '''
    import sys
    if sys.argv < 2:
        print('must input index url')

    index_url = sys.argv[1]
    spider = ThepaperSpider(index_url)
    spider.start()
    # spider.get_item_detail(['2581985'])

