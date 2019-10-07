from jobparser.spiders.avito import AvitoSpider, AvitoRealtySpider
from jobparser.spiders.facebook import FacebookSpider
import os
from os.path import join, dirname
from os import getenv
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from jobparser import settings

do_env = join(dirname(__file__), '.env')
load_dotenv(do_env)
#
# INST_LOGIN = getenv('INST_LOGIN')
# INST_PWD = getenv('INST_PWD')

FB_LOGIN = getenv('FB_LOGIN')
FB_PWD = getenv('FB_PWD')



if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    # process.crawl(hh_spider)
    # process.crawl(superjob_spider)
    # process.crawl(InstagramSpider, ['pestrova'], INST_LOGIN, INST_PWD)
    # process.crawl(AvitoSpider)
    # process.crawl(AvitoRealtySpider)
    process.crawl(FacebookSpider,['nastya.biryukova'], FB_LOGIN,FB_PWD)
    process.start()
