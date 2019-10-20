from jobparser.spiders.facebook import FacebookSpider
from jobparser.spiders.facebook import login
from os.path import join, dirname
from os import getenv
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from jobparser import settings
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument('-u', '--users', type=str, required=True, help='2 usernames separated by a comma, '
                                                                   'to find the chain that connects them')

parser = parser.parse_args()
users = parser.users.split(',')


do_env = join(dirname(__file__), '.env')
load_dotenv(do_env)

FB_LOGIN = getenv('FB_LOGIN')
FB_PWD = getenv('FB_PWD')

config = Settings()
config.setmodule(settings)
process = CrawlerProcess(config)


session = login(FB_LOGIN,FB_PWD)
while True:
    if session:
        break

process.crawl(FacebookSpider, users, session)

process.start()


