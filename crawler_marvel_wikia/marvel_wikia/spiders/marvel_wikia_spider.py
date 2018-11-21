'''
    Author: Basel Shbita
    Date created: 11/06/2018
    This scrapy-spider-crawler crawls http://marvel.wikia.com/ and yields an output file
'''

import string
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

NUM_OF_REQ_BS_IN_URL = 5
NUM_OF_REQ_QM_IN_URL = 1

# MARVELWIKIA-Spider class
class MARVELWIKIASpider(scrapy.Spider):
    name = "marvel_wikia"
    allowed_domains = ['marvel.wikia.com']
    wfilename = 'marvel_wikia_chars__%s.filtered.jl' % str(datetime.datetime.now()).split(' ')[0]
    wfile_handle = open(wfilename, "w")
    # incremental unique identifier counter (maps to 'doc_id' in output file)
    uniq_id = 0
    # REGEX for issue-pages filtering
    reg_ptrn = re.compile("http?:\/\/marvel\.wikia\.com\/.*(\(Earth-616\)|Category\:Earth\-616\_Characters).*")

    # URL seed initiate list
    def start_requests(self):
        urls = ['http://marvel.wikia.com/wiki/Category:Earth-616_Characters', \
                'http://marvel.wikia.com/index.php?title=Category:Earth-616_Characters&from=0']
        url_base = 'http://marvel.wikia.com/index.php?title=Category:Earth-616_Characters&from='
        for i in range(ord('A'), ord('Z')+1):
            urls.append(url_base + chr(i))
        for url in urls:
            # return an iterable of Requests
            yield scrapy.Request(url=url, callback=self.parse)

    # a method that will be called to handle the response downloaded for each of the requests made
    def parse(self, response):
        page_url = response.url
        # if webpage is not required, skip
        num_of_bs_in_url = len(page_url.split('/'))
        num_of_qm_in_url = len(page_url.split('?'))
        # check if the page is according to defined REGEX
        if self.reg_ptrn.match(page_url) and not(NUM_OF_REQ_BS_IN_URL != num_of_bs_in_url or \
                                                 NUM_OF_REQ_QM_IN_URL != num_of_qm_in_url or \
                                                 'File:' in page_url):
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
