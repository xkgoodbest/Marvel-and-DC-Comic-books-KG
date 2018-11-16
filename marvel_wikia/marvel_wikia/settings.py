# -*- coding: utf-8 -*-

# Scrapy settings for marvel_wikia project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'marvel_wikia'

SPIDER_MODULES = ['marvel_wikia.spiders']
NEWSPIDER_MODULE = 'marvel_wikia.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# 300 ms of delay
DOWNLOAD_DELAY = 0.5