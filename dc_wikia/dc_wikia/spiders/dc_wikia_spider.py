'''
    Author: Basel Shbita
    Date created: 11/07/2018
    This scrapy-spider-crawler crawls http://dc.wikia.com/ and yields an output file
'''

# json utilities
import json
# to maintain ordered-dictionaries
from collections import OrderedDict
# time
import datetime
# regular expressions
import re
# SCRAPY crawler libraries
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

# DCWIKIA-Spider class
class DCWIKIASpider(scrapy.Spider):
    name = "dc_wikia"
    allowed_domains = ['dc.wikia.com']
    wfilename = 'dc_wikia_chars__%s.filtered.jl' % str(datetime.datetime.now()).split(' ')[0]
    wfile_handle = open(wfilename, "w")
    # incremental unique identifier counter (maps to 'doc_id' in output file)
    uniq_id = 0
    # REGEX for issue-pages filtering
    reg_ptrn = re.compile("http?:\/\/dc\.wikia\.com\/wiki\/.*(\(Earth-One\)|\(New_Earth\)|Category:Earth-One_Characters).*")

    # URL seed initiate list
    def start_requests(self):
        urls = ['http://dc.wikia.com/wiki/Category:Earth-One_Characters']
        for url in urls:
            # return an iterable of Requests
            yield scrapy.Request(url=url, callback=self.parse)

    # a method that will be called to handle the response downloaded for each of the requests made
    def parse(self, response):
        page_url = response.url
        # check if the page is according to defined REGEX
        if self.reg_ptrn.match(page_url) and 5 == len(page_url.split('/')):
            # generate timestamp field
            timestamp_str = str(datetime.datetime.now())
            # debug print (in INFO logging mode)
            self.logger.info('[%05d][%s]: %s' % (self.uniq_id, timestamp_str, page_url))
            # output to file
            temp_dict_out = OrderedDict()
            temp_dict_out['doc_id'] = self.uniq_id
            temp_dict_out['url'] = page_url
            temp_dict_out['raw_content'] = response.body.decode('utf-8')
            temp_dict_out['timestamp_crawl'] = timestamp_str
            # serialize constructed dictionary to an output JSON-line
            temp_string = json.dumps(temp_dict_out)
            self.wfile_handle.write(temp_string + '\n')
            # increase the unique identifier
            self.uniq_id += 1
        # extract follow-up urls from response
        for url in response.xpath('//a/@href').extract():
            # make sure to get full-path and not relative-path
            next_page = response.urljoin(url)
            if self.reg_ptrn.match(next_page):
                yield scrapy.Request(next_page, callback=self.parse)
