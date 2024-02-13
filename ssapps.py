import scrapy
import re
from rustore.items import ShopAppItem

class SsappsSpider(scrapy.Spider):
    name = "ssapps"
    start_urls = ["https://apps.shopify.com/sitemap.xml"]


    def parse(self, response):
        for loc in response.xpath('//*[local-name()="loc"]/text()').getall():
            if loc.count('/') == 3:
                yield scrapy.Request(url=loc,
                                     callback=self.parse_app)

    def parse_app(self, response):
        item = ShopAppItem()
        # name
        item["name"] = response.xpath('//h1/text()').get(default='').strip()
        # slogan
        item["slogan"] = response.xpath('//div[@id="app-details"]/h2[@class="tw-text-heading-4"]/text()').get(default='').strip()
        # description
        item["description"] = response.xpath('//div[@id="app-details"]/p/text()').get(default='').strip().replace('\n', ' ')
        features = response.xpath('//div[@id="app-details"]/ul/li/div/span[2]/text()').getall()
        # features
        features = self.strip_list(features)
        item["features"] = '. '.join(features)
        # rating
        rating_pattern = r'Rating \((\d+(?:\.\d+)?)\)'
        rating = response.xpath('//span[contains(text(), "Rating")]/text()').get(default='')
        ratings = re.findall(rating_pattern, rating)
        item["rating"] = ratings[0]
        # reviews
        reviews = response.xpath('//a[@id="reviews-link"]/@aria-label').get(default='')
        reviews = self.getnubmer(reviews)
        if len(reviews):
            reviews = reviews[0]
        else:
            reviews = 0
        item["reviews"] = reviews
        # Plans
        plans = response.xpath('//div[@class="pricing-cards--mobile lg:tw-hidden"]//div[@class="app-details-pricing-plan-card__head"]//h3/text()').getall()
        plans = self.strip_list(plans)
        plans = ', '.join(plans)
        item["plans"] = plans

        # date Launched
        item["date_start"] = response.xpath('//section[@id="adp-details-mobile"]//p[contains(text(), "Launched")]/following::p[1]/text()').get(default='').strip().replace('\n', '')
        # Languages
        item["languages"] = response.xpath('//section[@id="adp-details-mobile"]//p[contains(text(), "Languages")]/following::p[1]/text()').get(default='').strip()
        # Categories
        categories = response.xpath('//section[@id="adp-details-mobile"]//p[contains(text(), "Categories")]/following::span[@class="tw-text-fg-tertiary tw-text-body-sm"]/a/text()').getall()
        categories = self.strip_list(categories)
        item["categories"] = ', '.join(categories)
        # Works with
        item["work_with"] = response.xpath('//div[@class="tw-mt-4 tw-space-y-6"]//p[contains(text(), "Works with")][1]/following::span/text()[1]').get(default='').strip().replace('\n', '')
        # support email
        item["email"] = response.xpath('//h3[contains(text(), "Support")]/following::p/text()[1]').get(default='').strip()
        # support link
        item["support_partal"] = response.xpath('//a[contains(text(), "Support portal")]/@href').get(default='').strip()
        item["privacy"] = response.xpath('//a[contains(text(), "Privacy policy")]/@href').get(default='').strip()
        item["faq"] = response.xpath('//a[contains(text(), "FAQ")]/@href').get(default='').strip()
        # developer
        #   name
        item["developer"] = response.xpath('//section[@id="adp-hero"]//a[contains(@href, "/partners/")]/text()').get(default='').strip()
        #   website
        item["website"] = response.xpath('//section[@id="adp-developer"]//a[contains(text(), "Website")]/@href').get(default='').strip()
        #   count apps
        count_apps = response.xpath('//section[@id="adp-developer"]//a[contains(text(), "app")]/text()').get(default='').strip()
        item["count_apps"] = self.getnubmer(count_apps)[0]
        item["url"] = response.url

        yield item


    def getnubmer(self, line):
        return ''.join(c if c.isdigit() else ' ' for c in line).split()


    def strip_list(self, row):
        return list(map(str.strip, row))