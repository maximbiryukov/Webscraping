import scrapy
from scrapy.http import HtmlResponse
from ..items import JobparserItem


class hh_spider(scrapy.Spider):

    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['http://hh.ru/search/vacancy?area=1&st=searchVacancy&text=python']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacancies = response.css('div.vacancy-serp-item__info a.bloko-link::attr(href)').extract()
        for link in vacancies:
            yield(response.follow(link, callback=self.vac_parse))

    def vac_parse(self, response: HtmlResponse):
        url = response.url
        name = response.css('div.vacancy-title h1.header::text').extract_first()
        employer = response.css('div.vacancy-company-wrapper p.vacancy-company-name-wrapper meta::attr(content)').extract()[0]
        salary = response.css('div.vacancy-title p::text').extract_first()
        yield JobparserItem(url=url, name=name, employer=employer, salary=salary, spider=self.name)
