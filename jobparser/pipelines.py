
from database.base import VacanciesDB
from database.models import Vacancies
from pymongo import MongoClient
from pymongo import MongoClient
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class JobparserPipeline(object):

    def __init__(self):

        client = MongoClient('localhost', 27017)
        self.mongo_db = client.vacancies
        self.sql_db = VacanciesDB('sqlite:///vacancies.sqlite')

    def process_item(self, item, spider):

        collection = self.mongo_db[spider.name]
        collection.insert_one(item)

        db_item = Vacancies(name=item.get('name'), spider=spider.name, url=item.get('url'),
                            employer=item.get('employer'), salary=item.get('salary'))
        self.sql_db.add_row(db_item)
        return item

class AvitoPhotosPipelines(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except TypeError:
                    pass

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
