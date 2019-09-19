import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class superjob_spider(scrapy.Spider):

    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):

        next = response.xpath('//a[contains(@class, "dalshe")]/@href').extract_first()
        if next:
            next_page = 'https://www.superjob.ru' + next
            yield (response.follow(next_page, callback=self.parse))

        vacancies = response.xpath('//a[contains(@class, "icMQ_ _1QIBo f-test-link")]/@href').extract()
        for link in vacancies:
            yield response.follow('https://www.superjob.ru' + link, callback=self.vac_parse)

    def vac_parse(self, response: HtmlResponse):

        url = response.url
        name = response.xpath('//h1[contains(@class, "_3mfro rFbjy s1nFK _2JVkc")]//text()').get()
        employer = response.xpath('//h2[contains(@class, "_3mfro PlM3e _2JVkc _2VHxz _3LJqf _15msI")]//text()').get()
        salary = ''.join(response.xpath('//span[contains(@class, "_3mfro _2Wp8I ZON4b PlM3e _2JVkc")]//text()').extract())

        yield JobparserItem(url=url, name=name, employer=employer, salary=salary, spider=self.name)
