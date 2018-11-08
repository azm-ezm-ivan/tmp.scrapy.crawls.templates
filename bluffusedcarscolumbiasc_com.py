import base64
import json
import re

import scrapy
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


def find_fjson(jsonData, param, id_param):
    for x in jsonData[id_param]:
        return x[param]


class bluffusedcarscolumbiasc_com(scrapy.Spider):
    name = 'bluffusedcarscolumbiasc_com'
    domain = 'bluffusedcarscolumbiasc.com'
    allowed_domains = ['bluffusedcarscolumbiasc.com']
    start_urls = ['http://www.bluffusedcarscolumbiasc.com/inventory']

    '''custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'DOWNLOAD_TIMEOUT': 5,
        'LOG_LEVEL': 'ERROR',
        'DOWNLOAD_FAIL_ON_DATALOSS': 'false',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'ACCEPT_ENCODING': 'gzip, deflate, br',
            'ACCEPT_LANGUAGE': 'en-US,en;q=0.9',
            'CONNECTION': 'keep-alive',
        }
    }'''

    i = 0




    def parse(self, response):
        for listing in response.css('#results-holder'):
            urls = listing.css('div> div.result-item-image > a::attr(href)').extract()
            for url in urls:
                url = response.urljoin(url)
                yield scrapy.Request(url=url, callback=self.parse_details)

        next_page = response.css('div.pagination.pull-left.text-left>a::attr(href)').extract()[-1]
        follow_url = response.urljoin(next_page)
        print("URL" + follow_url)
        yield response.follow(next_page, self.parse)

    def parse_details(self, response):
        jsonData_content = response.xpath('//script[@type="application/ld+json"]//text()').extract_first()
        listing = response
        vehicle = VehicleInfo()
        vehicle['domain'] = self.name.replace("_", ".")
        vehicle['url'] = response.request.url
        if jsonData_content:
            jsonData = json.loads(jsonData_content)
            vehicle['make'] = find_fjson(jsonData, "manufacturer", "@graph")
            vehicle['ext_color'] = find_fjson(jsonData, "color", "@graph")
            vehicle['model'] = find_fjson(jsonData, "model", "@graph")
            vehicle["miles"] = find_fjson(jsonData, "mileageFromOdometer", "@graph")
            vehicle['fuel_type'] = find_fjson(jsonData, "fuelType", "@graph")
            vehicle['year'] = find_fjson(jsonData, "productionDate", "@graph")
            vehicle['int_color'] = find_fjson(jsonData, "vehicleInteriorColor", "@graph")
            vehicle['transmission'] = find_fjson(jsonData, "vehicleTransmission", "@graph")
            vehicle['title'] = find_fjson(jsonData, "name", "@graph")
        vehicle['stock_no'] = listing.css('div.col-md-8.col-sm-8.col-xs-8 > p::text').extract_first()
        vin_decode = re.findall(r'"(\w+.)', listing.css('div.col-md-8.col-sm-8.col-xs-8 > p > span').extract_first())[0]
        vehicle['vin'] = base64.b64decode(vin_decode).decode('utf-8')

        str_prise = re.findall(r'(\d+[^,])', listing.css('div.inv-name > div > h3::text').extract_first())
        vehicle['price'] = ''.join(str_prise)
        vehicle['veh_state'] = "Used"
        vehicle['engine'] = listing.css('tbody:nth-child(8) > tr > td:nth-child(1)::text').extract_first()
        carfax_stat = listing.css(
            'div.car-detail > div:nth-child(7) > div.col-md-6.text-left > a::attr(href)').extract_first()
        if isinstance(carfax_stat, NoneType):
            vehicle['carfax'] = "unknown"
        else:
            vehicle['carfax'] = "http://www." + listing.css(
                'div.car-detail > div:nth-child(7) > div.col-md-6.text-left > a::attr(href)').extract_first()
        vehicle['doors'] = \
        listing.css('body > table > tbody:nth-child(8) > tr > td:nth-child(3)::text').extract_first().split(" ")[-1]
        body_style_str = listing.css(
            'body > table > tbody:nth-child(8) > tr > td:nth-child(3)::text').extract_first().split(" ")[:-1]
        vehicle['body_style'] = ' '.join(body_style_str)
        vehicle['description'] = listing.css('head > meta[name="Description"]::attr(content)').extract_first()[:97] + "..."

        #vehicle['trim'] = ""
        #vehicle['drivetrain'] = ""
        #vehicle['fuel_combined'] = ""
        #vehicle['fuel_highway'] = ""
        #vehicle['fuel_city'] = ""
        #vehicle['induction'] = ""
        #vehicle['displacement'] = ""
        #vehicle['cylinder'] = ""






        vehicle['image'] = ""
        if response.css('#thumbs > ul> li> a > img::attr(src)'):
            for img in response.css('#thumbs > ul> li> a > img::attr(src)'):
                vehicle['image'] += response.urljoin(img.extract()) + ","


        print(vehicle)



        ''' vehicle['title'] = response.meta["year"]
            vehicle['make'] = response.meta["make"]
            vehicle['model'] = response.meta["model"]
            vehicle['ext_color'] = response.meta["ext_color"]
            if listing.css("span.drivemotors::attr(data-price)"):
                vehicle['price'] = listing.css("span.drivemotors::attr(data-price)").extract_first()

            vehicle['vin'] = response.meta["vin"]
            vehicle['trim'] = response.meta["trim"]
            vehicle['body_style'] = response.meta["body_style"]
            #            vehicle['veh_state'] = ""

            #            vehicle['stock_no'] = ""
            vehicle['int_color'] = listing.css(
                "li.exteriorColor > span.secondary-spec > span.value::text").extract_first()

            vehicle['engine'] = listing.css("li.engine > span.value::text").extract_first()
            vehicle['transmission'] = listing.css("li.engine > span.value::text").extract_first()

            vehicle['miles'] = response.meta["miles"]
            if not vehicle['miles']:
                for vdpSpec in listing.css("div.vdp-vehicle-title > ul > li::text").extract():
                    if "Mileage" in vdpSpec:
                        vehicle['miles'] = vdpSpec.split(":")[1]
            if vehicle['miles']:
                vehicle['miles'] = vehicle['miles'].replace(",", "").strip()

            # vehicle['drivetrain']= ""
            # vehicle['induction']= ""
            # vehicle['displacement']= ""
            # vehicle['cylinder']= ""
            # vehicle["body_type"] = ""
            if listing.css('a.carfaxOneImg'):
                vehicle['carfax'] = listing.css('a.carfaxOneImg::attr(href)').extract_first()
            # vehicle['fuel_type'] = ""

            vehicle['fuel_combined'] = listing.css("li.techSpec-c-25::text").extract_first()
            if vehicle['fuel_combined']:
                vehicle['fuel_combined'] = vehicle['fuel_combined'].split(":")[1].strip()
                vehicle['fuel_combined'] = vehicle['fuel_combined'].replace("(Est)", "").strip()
            vehicle['fuel_highway'] = listing.css("li.techSpec-c-27::text").extract_first()
            if vehicle['fuel_highway']:
                vehicle['fuel_highway'] = vehicle['fuel_highway'].split(":")[1].strip()
                vehicle['fuel_highway'] = vehicle['fuel_highway'].replace("(Est)", "").strip()
            vehicle['fuel_city'] = listing.css("li.techSpec-c-26::text").extract_first()
            if vehicle['fuel_city']:
                vehicle['fuel_city'] = vehicle['fuel_city'].split(":")[1].strip()
                vehicle['fuel_city'] = vehicle['fuel_city'].replace("(Est)", "").strip()

            #            vehicle['doors'] = ""'''







