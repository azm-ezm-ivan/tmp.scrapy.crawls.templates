import scrapy
import re
import requests
import logging
import json
from scrapy import signals
from scrapy import Spider
from scrapy.utils.trackref import NoneType


class VDPVehicleInfo(scrapy.Item):
    domain = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
    make = scrapy.Field()
    model = scrapy.Field()
    trim = scrapy.Field()
    stock_no = scrapy.Field()
    vin = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()


class VehicleInfo(scrapy.Item):
    domain = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
    make = scrapy.Field()
    model = scrapy.Field()
    trim = scrapy.Field()
    ext_color = scrapy.Field()
    int_color = scrapy.Field()
    stock_no = scrapy.Field()
    miles = scrapy.Field()
    vin = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field()
    veh_state = scrapy.Field()
    image = scrapy.Field()
    engine = scrapy.Field()
    transmission = scrapy.Field()
    drivetrain = scrapy.Field()
    body_style = scrapy.Field()
    carfax = scrapy.Field()
    fuel_type = scrapy.Field()
    fuel_combined = scrapy.Field()
    fuel_highway = scrapy.Field()
    fuel_city = scrapy.Field()
    doors = scrapy.Field()
    induction = scrapy.Field()
    displacement = scrapy.Field()
    cylinder = scrapy.Field()
    price_type = scrapy.Field()
    body_type = scrapy.Field()
    description = scrapy.Field()


class gordonchevy_com(scrapy.Spider):
    name = 'gordonchevy_com'
    domain = 'gordonchevy.com'
    allowed_domains = ['gordonchevy.com']
    start_urls = ['https://www.gordonchevy.com/new']

    '''custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT': 10,
        'LOG_LEVEL': 'ERROR',
        'DOWNLOAD_FAIL_ON_DATALOSS': 'false',
        'DEFAULT_REQUEST_HEADERS': {
            'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'ACCEPT_ENCODING': 'gzip, deflate, br',
            'ACCEPT_LANGUAGE': 'en-US,en;q=0.9',
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
            'CONNECTION': 'keep-alive',
        }
    }

    i = 0'''

    def parse(self, response):
        urls = response.css('div.veh-title-bar.group > h2 > a::attr(href)').extract()
        jsonData_content = response.xpath('//script[@type="application/ld+json"]//text()').extract()    #43
        for ld_json in (jsonData_content[:-1]):
            jsonData = json.loads(ld_json)

            data = {
                "title": jsonData["name"],
                "year": jsonData["vehicleModelDate"],
                "make": jsonData["manufacturer"],
                "model": jsonData["model"],
                "ext_color": jsonData["color"],
                "trim": jsonData["mileageFromOdometer"],
                "vin": jsonData["vehicleIdentificationNumber"],
                "url": jsonData["url"],
                "veh_state": re.findall('(\w+)[C]', jsonData["itemCondition"])[0],
                "price": jsonData["offers"]["price"],
            }

            url = jsonData["url"]
            yield scrapy.Request(url=url, callback=self.parse_details, meta=data)

        selected_page = int(response.xpath('//*[@id="pagination-html"]/div/li[@class="item active"]/a/text()').extract_first())
        next_page = response.xpath('//*[@id="pagination-html"]/div/a[@data-page=' + str(selected_page + 1) + ']/@href').extract_first()
        follow_url = response.urljoin(next_page)
        print(follow_url)
        yield response.follow(follow_url, self.parse)

    def parse_details(self, response):
        listing = response
        vehicle = VehicleInfo()
        vehicle['domain'] = self.domain
        vehicle['vin'] = response.meta["vin"]
        vehicle['title'] = response.meta["title"]
        vehicle['veh_state'] = response.meta["veh_state"]
        vehicle['url'] = response.meta["url"]
        vehicle['trim'] = str(response.meta["trim"])
        vehicle['ext_color'] = response.meta["ext_color"]
        vehicle['model'] = response.meta["model"]
        vehicle['make'] = response.meta["make"]
        vehicle['year'] = str(response.meta["year"])
        vehicle['price'] = str(response.meta["price"])


        yield vehicle
