from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
import scrapy


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
