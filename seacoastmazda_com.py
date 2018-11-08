import scrapy
import requests
import logging
import json
import re
from urlparse import urlparse
from scrapy import signals
from scrapy import Spider
from scrapy.spiders import SitemapSpider
from scrapy.utils.sitemap import Sitemap
from scrapy.utils.gz import gunzip
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



class seacoastmazda_com(scrapy.Spider):
    name = 'seacoastmazda_com'
    domain = 'seacoastmazda.com'
    allowed_domains = ['seacoastmazda.com']
    start_urls = ['http://www.seacoastmazda.com/sitemap-vehicle.xml.gz']

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT': 5,
        'LOG_LEVEL': 'DEBUG',
        'DOWNLOAD_FAIL_ON_DATALOSS': 'false',
        'COOKIES_ENABLED': 'true',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'REDIRECT_ENABLED': 'false',
        'DEFAULT_REQUEST_HEADERS': {
            'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'ACCEPT_ENCODING': 'gzip, deflate, br',
            'ACCEPT_LANGUAGE': 'en-US,en;q=0.9',
            'CONNECTION': 'keep-alive',
        }
    }

    i = 0

    def _url(self, path):
        return 'http://fbi.targetmediapartners.com' + path

    def get_current_ip(self):
        header_info = {'Content-Type': 'application/json'}
        r = requests.get('http://ipinfo.io', headers=header_info)
        logging.warning(r.status_code)
        logging.warning(r.text)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(seacoastmazda_com, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self):
        self.update_progress('done')

    def update_progress(self, status):
        post_info = {"domain": self.domain, "count": self.i, "status": status, "notes": self.crawler.stats.get_stats()}
        logging.warning(json.dumps(post_info, default=str, sort_keys=True))
        header_info = {'Content-Type': 'application/json', 'Api-Key': 'api-key-1234567890'}
        resp = requests.post(self._url('/Status/Crawler'), data=json.dumps(post_info, default=str, sort_keys=True), headers=header_info)

    def findItem(self, str, response):
        key = response.css('.vehicle-specification-wrapper > div > div.row > ul> li > span.title::text').extract()
        value = response.css('.vehicle-specification-wrapper > div > div.row > ul> li > span.value::text').extract()
        ziplist = zip(key, value)
        dictoflist = dict(ziplist)
        return dictoflist.get(str)

    def parse(self, response):
        body = ""
        body = gunzip(response.body)
        s = Sitemap(body)
        for sitelink in s:
            url = sitelink['loc']
            yield scrapy.Request(url, callback=self.parse_details)

    def parse_details(self, response):
        java_script = response.xpath('/html/head/script/text()').extract()
        vehicle = VehicleInfo()
        vehicle['domain'] = self.domain
        vehicle['year'] = response.css("meta[itemprop='releaseDate']::attr(content)").extract_first()
        if vehicle['year']:
            vehicle['description'] = ''.join(re.findall('(\S+[ ]+)', response.css('div.clip-text__main::text').extract_first()))[:97] + "..."
            vehicle['url'] = response.request.url
            vehicle['title'] = response.css("meta[itemprop='name']::attr(content)").extract_first()
            vehicle['make'] = response.css("meta[itemprop='manufacturer']::attr(content)").extract_first()
            vehicle['model'] = response.css("meta[itemprop='model']::attr(content)").extract_first()
            vehicle['ext_color'] = response.css("meta[itemprop='color']::attr(content)").extract_first()

            vehicle['stock_no'] = response.css("meta[itemprop='sku']::attr(content)").extract_first()
            vehicle['vin'] = response.css("meta[itemprop='serialNumber']::attr(content)").extract_first()

            trim = response.xpath(".//span[@class='title']/strong[contains(text(), 'Trim:')]/../following-sibling::span/text()").extract_first()
            if not isinstance(trim, NoneType):
                vehicle['trim'] = trim
            else:
                vehicle['trim'] = self.findItem(str="Trim:", response=response)

            body_style = response.xpath(".//span[@class='title']/strong[contains(text(), 'Body:')]/../following-sibling::span/text()").extract_first()
            if not isinstance(body_style, NoneType):
                vehicle['body_style'] = body_style
            else:
                vehicle['body_style'] = self.findItem(str="Body style:", response=response)

            doors = response.xpath(".//span[@class='title']/strong[contains(text(), 'Doors:')]/../following-sibling::span/text()").extract_first()
            if not isinstance(doors, NoneType):
                vehicle['doors'] = doors
            else:
                vehicle['doors'] = self.findItem(str="Doors:", response=response)

            vehicle['veh_state'] = response.css("link[itemprop='itemCondition']::attr(href)").extract_first()
            if vehicle['veh_state']:
                vehicle['veh_state'] = vehicle['veh_state'].replace("http://schema.org/", "").replace("Condition", "")

            int_color = response.xpath(".//span[@class='title']/strong[contains(text(), 'Interior:')]/../following-sibling::span/text()").extract_first()
            if not isinstance(int_color, NoneType):
                vehicle['int_color'] = int_color
            else:
                vehicle['int_color'] = self.findItem(str="Interior:", response=response)

            if response.xpath(".//span[@class='title']/strong[contains(text(), 'Engine:')]/../following-sibling::span/text()"):
                vehicle['engine'] = response.xpath(".//span[@class='title']/strong[contains(text(), 'Engine:')]/../following-sibling::span/text()").extract_first()
            elif response.xpath(".//span[contains(text(), 'Engine')]/following-sibling::span/text()"):
                vehicle['engine'] = response.xpath(".//span[contains(text(), 'Engine')]/following-sibling::span/text()").extract_first()

            if response.xpath(".//span[@class='title']/strong[contains(text(), 'Transmission:')]/../following-sibling::span/text()"):
                vehicle['transmission'] = response.xpath(".//span[@class='title']/strong[contains(text(), 'Transmission:')]/../following-sibling::span/text()").extract_first()
            elif response.xpath(".//span[contains(text(), 'Transmission')]/following-sibling::span/text()"):
                vehicle['transmission'] = response.xpath(".//span[contains(text(), 'Transmission')]/following-sibling::span/text()").extract_first()

            if response.xpath(".//span[@class='title']/strong[contains(text(), 'Mileage:')]/../following-sibling::span/text()"):
                vehicle['miles'] = response.xpath(".//span[@class='title']/strong[contains(text(), 'Mileage:')]/../following-sibling::span/text()").extract_first()
            elif response.xpath(".//span[contains(text(), 'Mileage')]/following-sibling::span/text()"):
                vehicle['miles'] = response.xpath(".//span[contains(text(), 'Mileage')]/following-sibling::span/text()").extract_first()

            drivetrain = response.xpath(".//span[@class='title']/strong[contains(text(), 'Drive:')]/../following-sibling::span/text()").extract_first()
            if not isinstance(drivetrain, NoneType):
                vehicle['drivetrain'] = drivetrain
            else:
                vehicle['drivetrain'] = self.findItem(str="Drivetrain:", response=response)
            mpg = response.xpath(".//span[@class='title']/strong[contains(text(), 'MPG*:')]/../following-sibling::span/text()").extract_first()
            if mpg:
                vehicle['fuel_highway'] = mpg.split("/")[1].replace("Hwy", "").strip()
                vehicle['fuel_city'] = mpg.split("/")[0].replace("City", "").strip()

            vehicle['price'] = response.css("meta[itemprop='price']::attr(content)").extract_first()
            if vehicle['price']:
                vehicle['price'] = vehicle['price'].replace("$", "").replace(",", "")
            vehicle['price_type'] = response.css("meta[itemprop='priceCurrency']::attr(content)").extract_first()

            vehicle['image'] = ""
            if response.css("div.thumb-group img[itemprop='image']"):
                images = response.css("div.thumb-group img[itemprop='image']::attr(data-preview)").extract()
            elif response.css("div.images img[itemprop='image']"):
                images = response.css("div.images img[itemprop='image']::attr(src)").extract()

            for img in images:
                vehicle['image'] += img + ","

            self.i += 1
            self.update_progress('in-progress')
            yield vehicle