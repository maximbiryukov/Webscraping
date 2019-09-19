# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from database.base import VacanciesDB
from database.models import Vacancies
from pymongo import MongoClient


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
