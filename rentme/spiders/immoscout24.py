import re
import uuid

import scrapy
import time


class ImmoScout24Spider(scrapy.Spider):
    name = "immoscout24"
    allowed_domains = ["immoscout24.ch"]
    start_urls = [
        "http://www.immoscout24.ch/en/search/rent-flat-zuerich-grossraum?s=2&t=1&l=135&se=1&pn=1&ps=120"]

    def parse(self, response):
        # DEBUGGING PURPOSES
        # filename = "immoscout24.html"
        # with open(filename,'wb+') as f:
        #     f.write(response.body)
        # self.log("Saved "+filename)

        offers = response.xpath('//li[contains(@class,"item")]')

        for offer in offers:
            try:
                price = (''.join(offer.xpath('.//div[@class="item-props labeled-props"]/strong[@class="prop-value"]/text()').extract())).replace("CHF ", "").replace(".—", "").replace(",", "").strip()
            except Exception:
                price = None
            try:
                source_id = re.search('(\/)(\d+)(\?)', (''.join(offer.xpath('.//a[@class="item-title"]/@href').extract_first())).strip()).group(2)
            except Exception:
                source_id = None
            try:
                city = offer.xpath(".//div[@class='item-prop-column']/div[@class='item-props']/text()").extract()[1].strip()
            except Exception:
                city = None
            try:
                street = offer.xpath(".//div[@class='item-prop-column']/div[@class='item-props']/text()").extract_first().strip()
            except Exception:
                street = None
            try:
                url = 'http://www.immoscout24.ch' + re.search('(\S+\d+)(\?)', (''.join(offer.xpath('.//a[@class="item-title"]/@href').extract_first())).strip()).group(1)
            except Exception:
                url = None
            attributes = offer.xpath(".//div[@class='item-prop-column labeled-prop-column']/div[@class='item-props labeled-props']")
            attributes_dict = {}
            if attributes:
                for attribute in attributes:
                    try:
                        keys = attribute.xpath("./span[@class='prop-label']/text()").extract()
                    except Exception:
                        keys = None
                    if keys:
                        i = 0
                        for _ in keys:
                            try:
                                attr_key = attribute.xpath("./span[@class='prop-label']/text()").extract()[i]
                                attr_value = attribute.xpath("./span[@class='prop-value']/text()").extract()[i]
                                i += 1
                                if attr_key:
                                    attributes_dict.update({attr_key: attr_value})
                            except IndexError:
                                pass
                    # if attr_key:
                    #     attributes_dict.update({attr_key: attr_value})
            if source_id:
                yield {
                    'offer_id': str(uuid.uuid1().int),
                    'source_id': source_id,
                    'city': city,
                    'street': street,
                    'price': int(price),
                    'currency': 'CHF',
                    'url': url,
                    'scrape_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'attributes': attributes_dict
                }

            # next_page_url = response.xpath("//li[@class='next']/a[@rel='next']/@href").extract_first()
            # if next_page_url is not None:
            #     yield scrapy.Request(response.urljoin(next_page_url))
