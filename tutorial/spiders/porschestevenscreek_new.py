import scrapy
import re
from scrapy import Selector
from scrapy.http import HtmlResponse
from scrapy.selector import SelectorList

__all__ = ['Selector', 'SelectorList']


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


class VehicleInfo(VDPVehicleInfo):
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


class PorscheStevensCreek(scrapy.Spider):
    name = "porschestevenscreek_new"

    def start_requests(self):
        urls = [
            'https://www.porschestevenscreek.com/porsche.aspx']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        listings = response.css('.srp-vehicle-block')
        urls = listings.css('#srp-vehicle-title > div > h2 > a::attr(href)').extract()

        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_model)

    def parse_model(self, listing):
        vehicle = VehicleInfo()
        full_name = SelectorList(listing.xpath('//*[@id="vdp-title"]/div/div/div[1]/div[1]/div[1]/h1/text()')).extract_first()
        url_split = listing.url.split('/')
        ulr_path = re.sub('detail-', '', url_split[url_split.__len__() - 1])

        vehicle['year'] = re.findall('[0-9]{4}', ulr_path)[0]
        vehicle['make'] = re.sub('_', ' ', re.split('-', ulr_path)[1]).capitalize()
        vehicle['model'] = re.sub(vehicle['year'] + ' ' + vehicle['make'] + ' ', '', full_name)

        vehicle['ext_color'] = listing.xpath('//*[@id="tab-details"]/div[3]/table/tbody/tr[1]/td[2]/text()').extract_first().strip()

        image_urls = listing.css('#tab-slideshow-photos .swiper-slide a::attr(href)').extract()

        image_url = "https:" + image_urls[0]
        image_page_url = ''
        yield vehicle
