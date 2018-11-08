import scrapy
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
    description = scrapy.Field()

class danpfeiffer_net(scrapy.Spider):
    name = 'danpfeiffer_net'
    domain = 'danpfeiffer.net'
    allowed_domains = ['danpfeiffer.net']
    start_urls = ['http://www.danpfeiffer.net/preowned.aspx']

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
    for listing in response.css('#ctl02_ctl00_ContentPane > div.i07r'):
        urls = listing.css('a::attr(href)').extract()
        data = {
            "year": listing.css('div.hproduct ::attr(data-year)').extract_first(),
            "make": listing.css('div.hproduct ::attr(data-make)').extract_first(),
            "model": listing.css('div.hproduct ::attr(data-model)').extract_first(),
            "ext_color": listing.css('div.hproduct ::attr(data-exteriorcolor)').extract_first(),
            "trim": listing.css('div.hproduct ::attr(data-trim)').extract_first(),
            "body_style": listing.css('div.hproduct ::attr(data-bodystyle)').extract_first(),
            "veh_state": listing.css('div.hproduct ::attr(data-type)').extract_first(),
        }
        ''' for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_details, meta=data)

    next_page = response.css('a[rel=next]::attr(data-href)').extract_first()
    follow_url = response.urljoin(next_page)
    yield response.follow(follow_url, self.parse)'''
