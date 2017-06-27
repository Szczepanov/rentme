import uuid

import scrapy
import time


class HomeGateSpider(scrapy.Spider):
    name = "homegate"
    allowed_domains = ["homegate.ch"]
    start_urls = [
        "https://www.homegate.ch/rent/real-estate/matching-list?tab=list&ab=4000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000G00040C000G202G00000000000A",
        "https://www.homegate.ch/rent/apartment/matching-list?tab=list&ab=4000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000G00040C000G202G00000000000A",
        "https://www.homegate.ch/rent/house/matching-list?tab=list&ab=4000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000G00040C000G202G00000000000A",
        "https://www.homegate.ch/rent/furnished-dwelling/matching-list?tab=list&ab=4000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000G00040C000G202G00000000000A"]

    def parse(self, response):
        offers = response.xpath('//article[@class="box-row-wrapper"]/a[@class="detail-page-link box-row--link"]')
        for offer in offers:
            try:
                price = (''.join(offer.xpath('.//div[@class="item-content-label"]/span/text()').extract()).replace(",", "").replace(".\u2013", "")).strip()
            except Exception:
                price = None
            try:
                source_id = (''.join(offer.xpath("./@href").extract_first()).replace("/rent/", "")).strip()
            except Exception:
                source_id = None
            try:
                city = offer.xpath(".//p[@class='item-description']/span[@class='display--block']/text()").extract_first().strip()
            except Exception:
                city = None
            try:
                street = offer.xpath(".//div[@class='item-content item-content--tooltip']/p[@class='item-title item-title--street']/text()").extract_first().strip()
            except Exception:
                street = None
            try:
                url = 'https://www.homegate.ch' + offer.xpath("./@href").extract_first().strip()
            except Exception:
                url = None
            attributes = offer.xpath(".//div[@class='item-content']/ul//node()")
            attributes_dict = {}
            for attribute in attributes:
                attr_key = ''.join(attribute.xpath("./span[@class='key']/text()").extract()).strip()
                attr_value = ''.join(attribute.xpath("./span[@class='value']/text()").extract()).strip()
                if attr_key:
                    attributes_dict.update({attr_key: attr_value})
            yield {
                'offer_id': uuid.uuid1().int,
                'source_id': source_id,
                'city': city,
                'street': street,
                'price': price,
                'currency': 'CHF',
                'url': url,
                'scrape_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'attributes':  attributes_dict
            }

            next_page_url = response.xpath("//li[@class='next']/a[@rel='next']/@href").extract_first()
            if next_page_url is not None:
                yield scrapy.Request(response.urljoin(next_page_url))
