from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem, AvitoRealEstate
import scrapy
import re
from scrapy.loader import ItemLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    query = '1c'
    start_urls = [f'https://www.avito.ru/rossiya/vakansii?q={query}/']

    def parse(self, response: HtmlResponse):
        try:
            pages_num = int(response.xpath('//div[contains(@class,"pagination")]/a/text()').extract()[-1])
            if pages_num:
                for i in range(2, pages_num + 1):
                    yield response.follow(f'/rossiya/vakansii?p={i}&amp;q={self.query}', callback=self.get_vacancies)
        except IndexError:
            yield response.follow(self.start_urls[0], callback=self.get_vacancies)

    def get_vacancies(self, response: HtmlResponse):
        vacancies = response.xpath('//a[contains(@class,"item-description-title-link")]/@href').extract()
        for item in vacancies:
            yield response.follow('https://www.avito.ru' + item, callback=self.vac_parse)

    def vac_parse(self, response: HtmlResponse):
        url = response.url
        name = response.xpath('//span[contains(@class, "title-info-title-text")]/text()').extract_first()
        employer = response.xpath('//div[contains(@class, "seller-info-name")]/a/text()').extract_first()[2:-2]
        salary = response.xpath('//span[contains(@class, "js-item-price")]/@content').extract_first()
        yield JobparserItem(url=url, name=name, employer=employer, salary=salary, spider=self.name)

class AvitoRealtySpider(scrapy.Spider):

    name = 'avito_realty'
    allowed_domains = ['www.avito.ru']
    base_url = 'www.avito.ru'
    start_urls = ['https://www.avito.ru/moskva_i_mo/kvartiry?cd=1']

    def parse(self, response: HtmlResponse):
        try:
            pages_num = int(re.findall(r'[?=p]\w+', response.xpath('//div[contains(@class,"pagination")]/a/@href').extract()[-1])[1][1:])
            if pages_num:
                for i in range(1, 3):
                    yield response.follow(f'{self.start_urls[0]}?p={i}', callback=self.page_parse)
        except IndexError:
            yield response.follow(self.start_urls[0], callback=self.page_parse)

    def page_parse(self, response: HtmlResponse):
        links = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        for item in links:
            yield response.follow(item, callback=self.parse_flat)

    def parse_flat(self, response: HtmlResponse):
        price = response.xpath('//span[contains(@class,"js-item-price")]/@content').extract()[0]
        link = response._url
        feature_names = response.xpath('//ul[contains(@class,"item-params-list")]//li//span/text()').extract()
        try:
            feature_names.remove('Название новостройки: ')
        except ValueError:
            pass
        feature_values = [x for x in response.xpath('//ul[contains(@class,"item-params-list")]//li/text()').extract() if x.strip()]
        features = dict(zip(feature_names, feature_values))

        loader = ItemLoader(item=AvitoRealEstate(), response=response)
        loader.add_value('price', price)
        loader.add_value('link', link)
        loader.add_xpath('photos',
                         '//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url')
        loader.add_css('title', 'h1.title-info-title span.title-info-title-text::text')
        loader.add_value('features', features)
        yield loader.load_item()
