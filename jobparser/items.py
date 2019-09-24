import scrapy


class JobparserItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    employer = scrapy.Field()
    salary = scrapy.Field()
    spider = scrapy.Field()
    pass


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    user = scrapy.Field()
    post = scrapy.Field()
    entry_type = scrapy.Field()
    author = scrapy.Field()
    comment_text = scrapy.Field()
