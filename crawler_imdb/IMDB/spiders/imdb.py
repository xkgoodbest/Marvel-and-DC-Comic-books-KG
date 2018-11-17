import scrapy
from scrapy.loader import ItemLoader
from IMDB.items import ImdbItem
from scrapy.exceptions import CloseSpider
import time


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    custom_settings = {'ITEM_PIPELINES': {
        'IMDB.pipelines.ImdbPipeline': 300}}

    def __init__(self):
        self.count = 0

    def start_requests(self):
        totalURL = [
            'https://www.imdb.com/search/keyword?keywords=marvel-cinematic-universe&sort=moviemeter,asc&mode=detail&page=1&ref_=kw_nxt',
            'https://www.imdb.com/list/ls020636102/']
        for i, url in enumerate(totalURL):
            yield scrapy.Request(url=url.replace('\n', ''), callback=self.parsePages)

    def parse(self, response):
        l = ItemLoader(item=ImdbItem(), response=response)
        l.add_value('url', str(response.url))
        # l.add_value('raw_content', str(response.body))
        # page_content = str(response.body)
        title = response.xpath(
            '//div[contains(@class,"title_wrapper")]/h1/text()').extract_first()
        if title:
            l.add_value('title', title.strip())

        rate = response.xpath(
            '//div[contains(@class,"ratingValue")]/strong/span/text()').extract_first()
        if rate:
            l.add_value('rate', rate.strip())

        mpr = response.xpath(
            '//div[contains(@class,"title_wrapper")]/div[contains(@class,"subtext")]/text()').extract_first()
        if mpr:
            l.add_value('motion_pic_rate', mpr.strip())

        story_line = response.xpath(
            '//div[contains(@id,"titleStoryLine")]/div/p/span/text()').extract()
        if story_line:
            l.add_value('story_line', story_line)

        genres = response.xpath('//div[h4="Genres:"]/a/text()').extract()
        if genres:
            l.add_value('genres', genres)

        key_words = response.xpath(
            '//div[h4="Plot Keywords:"]/a/span/text()').extract()
        if key_words:
            l.add_value('key_words', key_words)

        release_date = response.xpath(
            '//div[h4="Release Date:"]/text()').extract()
        if release_date:
            l.add_value('release_date', release_date)

        ch_link = response.xpath(
            '//div[contains(@class,"see-more")]/a[contains(@href,"cast")]/@href').extract()
        for page in ch_link:
            next_page = response.urljoin(page)
            request = scrapy.Request(url=next_page.replace(
                '\n', ''), callback=self.parseCharacters)
            request.meta['item'] = l
            yield request

        self.count += 1
        return l.load_item()

    def parseCharacters(self, response):
        ch_link = response.xpath(
            '//td[contains(@class,"character")]/a[contains(@href,"title")]/text()').extract()
        l = response.meta['item']
        if ch_link:
            l.add_value('characters', ch_link)
        yield l.load_item()

    def parsePages(self, response):
        movie_pages = response.xpath(
            '//h3[contains(@class,"lister-item-header")]/a/@href').extract()
        for page in movie_pages:
            next_page = response.urljoin(page)
            yield scrapy.Request(url=next_page.replace('\n', ''), callback=self.parse)

        next_page = response.xpath(
            '//div[contains(@class, "nav")]/div[contains(@class,"desc")]/a/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parsePages)
