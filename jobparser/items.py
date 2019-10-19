import scrapy
from scrapy.loader.processors import MapCompose
import re


def fb_friend_cleaner(item):
    output = ''
    if re.search('profile.php', item): #парсим юзернеймы
        output += (re.search('(?<=id=)(.*)(?=&fref)', item).group(0))
    else:
        output += (re.search('(?<=.com/)(.*)(?=\?)', item).group(0))

    return output


class FacebookItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    username = scrapy.Field()
    photos = scrapy.Field()
    friends = scrapy.Field(input_processor=MapCompose(fb_friend_cleaner))
    search = scrapy.Field()
