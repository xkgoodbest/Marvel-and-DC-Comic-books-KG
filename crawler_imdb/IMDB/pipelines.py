# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json

class ImdbPipeline(object):
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
    def open_spider(self, spider):
        self.file = open('imdb_marvel.jl', 'w')

    def close_spider(self, spider):
        self.file.close()
