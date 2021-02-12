import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import RcbatItem

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'

class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.rcb.at/en/certificates/news']

    def parse(self, response):
        links = response.xpath('//a[@class="news-item-link"]/@href').getall()
        end_page = response.xpath('//em[@class="rcb-angle-right"]').get()
        if end_page:
            for link in links:
                yield response.follow(link, self.parse_article)

            next_page = response.xpath('(//a[@class="pager-link icon"]/@href)[last()]').get()
            if next_page:
                yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(RcbatItem())
        item.default_output_processor = TakeFirst()

        date = response.xpath('//time/@datetime').get()
        title = response.xpath('//h1//text()').get().strip()
        subtitle = response.xpath('//div[@class="content-block editor-output margin--bottom-sm"]/h2//text()').get()

        if subtitle:
            subtitle = subtitle.strip()
        else:
            subtitle = ''

        content = ''.join(response.xpath('//div[@itemprop="articleBody"][1]//text()').getall())
        content = re.sub(pattern, "", content)

        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('subtitle', subtitle)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()