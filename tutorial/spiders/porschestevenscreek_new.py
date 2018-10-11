import scrapy


class QuotesSpider(scrapy.Spider):
    name = "porschestevenscreek_new"

    def start_requests(self):
        urls = [
            'https://www.porschestevenscreek.com/porsche.aspx']
        # 'https://www.porschestevenscreek.com/used-cars.aspx']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        i = 0
        stext = " "
        tt = response.css('.srp-vehicle-block')
        for listing in response.css('.srp-vehicle-block'):
            # urls = response.css('#srp-vehicle-details').extract()
            data = {
                "year": (listing.xpath('//*[@id="srp-vehicle-title"]/div/h2/a/text()').extract()[i])[0:4],
                "make": ((listing.xpath('//*[@id="srp-vehicle-title"]/div/h2/a/text()').extract()[i]).split())[1],
                "model": stext.join(
                    ((listing.xpath('//*[@id="srp-vehicle-title"]/div/h2/a/text()').extract()[i]).split())[2:]),
                "ext_color": listing.xpath('//*[@id="srp-vehicle-details"]/ul/li[3]/text()').extract()[i],
                "trim": listing.css('div.hproduct ::attr(data-trim)').extract_first(),
                "body_style": listing.xpath('//*[@id="srp-vehicle-title"]/div/h3/text()').extract()[i],
                "veh_state": listing.css('div.hproduct ::attr(data-type)').extract_first(),
            }
            i = i + 1
            print(data)
