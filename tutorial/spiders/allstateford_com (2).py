import scrapy
import requests
import logging
import json
from scrapy import signals
from scrapy import Spider

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

    
class allstateford_com(scrapy.Spider):
    name = 'allstateford_com'
    domain = 'allstateford.com'
    allowed_domains = ['allstateford.com']
    start_urls = ['https://www.allstateford.com/new-inventory/index.htm','https://www.allstateford.com/used-inventory/index.htm']

    custom_settings = {
        'DOWNLOAD_DELAY' : 1,
        'DOWNLOAD_TIMEOUT' : 10,
        'LOG_LEVEL' : 'ERROR',
        'DOWNLOAD_FAIL_ON_DATALOSS' : 'false',
        'DEFAULT_REQUEST_HEADERS' : {
            'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'ACCEPT_ENCODING' : 'gzip, deflate, br',
            'ACCEPT_LANGUAGE' : 'en-US,en;q=0.9',
            'USER_AGENT' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
            'CONNECTION' : 'keep-alive',
        }
    }
    
    i=0

            
    def _url(self, path):
        return 'http://fbi.targetmediapartners.com' + path
        
    def get_current_ip(self):
        header_info = {'Content-Type': 'application/json'}
        r = requests.get('http://ipinfo.io', headers=header_info)
        logging.warning(r.status_code)
        logging.warning(r.text)

    @classmethod  
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(allstateford_com, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self):
        self.update_progress('done')

    def update_progress(self,status):
        post_info = { "domain" : self.domain , "count" : self.i, "status" : status, "notes": self.crawler.stats.get_stats()}
        logging.warning(json.dumps(post_info, default=str, sort_keys=True))
        header_info = {'Content-Type': 'application/json', 'Api-Key':'api-key-1234567890' }
        resp = requests.post(self._url('/Status/Crawler'), data=json.dumps(post_info, default=str, sort_keys=True), headers=header_info)
        
    def parse(self, response):
        for listing in response.css('ul.inventoryList > li > div.auto'):
            urls = listing.css('a.url::attr(href)').extract()
            data = {
                "year": listing.css('div.hproduct ::attr(data-year)').extract_first(),
                "make": listing.css('div.hproduct ::attr(data-make)').extract_first(),
                "model": listing.css('div.hproduct ::attr(data-model)').extract_first(),
                "ext_color": listing.css('div.hproduct ::attr(data-exteriorcolor)').extract_first(),
                "trim": listing.css('div.hproduct ::attr(data-trim)').extract_first(),
                "body_style": listing.css('div.hproduct ::attr(data-bodystyle)').extract_first(),
                "veh_state" : listing.css('div.hproduct ::attr(data-type)').extract_first(),
            }
            for url in urls:
                url = response.urljoin(url)
                yield scrapy.Request(url=url, callback=self.parse_details, meta=data)

        next_page = response.css('a[rel=next]::attr(data-href)').extract_first()
        follow_url = response.urljoin(next_page)
        yield response.follow(follow_url, self.parse)

    def parse_details(self, response):
        listing = response
        vehicle = VehicleInfo()
        vehicle['domain'] = self.domain
        vehicle['year'] = response.meta["year"]
        if vehicle['year']:
            vehicle['url'] = response.request.url
            vehicle['title'] = listing.css("title::text").extract_first().strip()
            vehicle['make'] = response.meta["make"]
            vehicle['model'] = response.meta["model"]
            vehicle['ext_color'] = response.meta["ext_color"]
            vehicle['trim'] = response.meta["trim"]
            vehicle['body_style'] = response.meta["body_style"]
            vehicle['veh_state'] = response.meta["veh_state"]

            vehicle['vin'] = listing.css("input[name=vin]::attr(value)").extract_first()
            if vehicle['vin']:
                vehicle['vin'] = vehicle['vin'].strip()

            vehicle['stock_no'] = listing.css("li.stockNumber > span.value::text").extract_first()
            if vehicle['stock_no']:
                vehicle['stock_no'] = vehicle['stock_no'].strip()

            vehicle["int_color"] = ""
            if response.xpath('//dt[text()="Interior Color"]/following::dd[1]/span'):
                vehicle['int_color'] = response.xpath('//dt[text()="Interior Color"]/following::dd[1]/span/text()').extract_first()
            elif response.xpath('//span[text()="InteriorColor"]/following::strong'):
                vehicle['int_color'] = response.xpath('//span[text()="InteriorColor"]/following::strong/text()').extract_first()
            elif response.xpath('//span[text()="Interior Color"]/following::span[2]'):
                vehicle['int_color'] = response.xpath('//span[text()="Interior Color"]/following::span[2]/text()').extract_first()
            elif listing.css("li.interiorColor > span.secondary-spec"):
                vehicle['int_color'] = listing.css("li.interiorColor > span.secondary-spec > span.value::text").extract_first()
            elif listing.css("li.interiorColor"):
                vehicle['int_color'] = listing.css("li.interiorColor span.value::text").extract_first()
            if vehicle['int_color']:
                vehicle['int_color'] = vehicle['int_color'].strip()

            vehicle['engine'] = listing.css("li.engine > span.value::text").extract_first()
            if vehicle['engine']:
                vehicle['engine'] = vehicle['engine'].strip()

            vehicle['transmission'] = listing.css("li.engine > span.value::text").extract_first()
            if vehicle['transmission']:
                vehicle['transmission'] = vehicle['transmission'].strip()

            vehicle['miles'] = ""
            if response.xpath('//dt[text()="Odometer"]/following::dd[1]/span/text()'):
                vehicle['miles'] = response.xpath('//dt[text()="Odometer"]/following::dd[1]/span/text()').extract_first()
            elif listing.css("li.odometer"):
                vehicle['miles'] = listing.css("li.odometer > span.value::text").extract_first()
            if vehicle['miles']:
                vehicle['miles'] = vehicle['miles'].replace('miles','').replace(',','').strip()

            if listing.css("li.carfax > a::attr(href)"):
                vehicle['carfax'] = listing.css("li.carfax > a::attr(href)").extract_first()

            vehicle['fuel_highway'] = listing.css("ul.class-specs > li.fuel-efficiency > a > span.value:first-child::text").extract_first()
            vehicle['fuel_city'] = listing.css("ul.class-specs > li.fuel-efficiency > a > span.value:last-child::text").extract_first()

#            vehicle['doors'] = ""
            
            if listing.css('span.final-price'):
                vehicle['price'] = listing.css('span.final-price::attr(data-attribute-value)').extract_first()
            elif listing.css('dl.final-price'):
                vehicle['price'] = listing.css('dl.final-price > dd::text').extract_first()
            if vehicle['price']:
                vehicle['price'] = vehicle['price'].replace("$", "").replace(",", "").replace(".0", "")

#            vehicle['price_type']=""

            vehicle['image'] = ""
            if response.css('li.jcarousel-item'):
                for img in response.css('li.jcarousel-item a::attr(href)'):
                    vehicle['image'] += img.extract() + ","
            elif response.css('img.photo::attr(data-src)'):
                for img in response.css('img.photo::attr(data-src)'):
                    vehicle['image'] += img.extract().replace("/thumb_", "/") + ","
            elif response.css('div.imageViewer img.photo::attr(src)'):
                vehicle['image'] = response.css('div.imageViewer img.photo::attr(src)').extract_first()

            self.i += 1
            self.update_progress("in-progress")
            yield vehicle

