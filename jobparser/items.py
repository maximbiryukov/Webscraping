import scrapy


class JobparserItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    employer = scrapy.Field()
    salary = scrapy.Field()
    spider = scrapy.Field()
    pass
