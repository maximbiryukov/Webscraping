import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
import re

def cleaner_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values

def feature_cleaner(values):
    for key, value in values.items():
        values[key] = value.replace(u'\xa0м² ', '')
        values[key] = re.sub(r' ','',values[key])
    return values

def fb_friend_cleaner(item):
    output = ''
    if re.search('profile.php', item):
        output += (re.search('(?<=id=)(.*)(?=&fref)', item).group(0))
    else:
        output += (re.search('(?<=.com/)(.*)(?=\?)', item).group(0))

    return output

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

class AvitoRealEstate(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field()
    price = scrapy.Field()
    features = scrapy.Field(input_processor=MapCompose(feature_cleaner))
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))

class FacebookItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    photos = scrapy.Field()
    friends = scrapy.Field(input_processor=MapCompose(fb_friend_cleaner))