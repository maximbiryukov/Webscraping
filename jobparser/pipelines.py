
from pymongo import MongoClient
import time
# from scrapy.pipelines.images import ImagesPipeline

def find_chain(user_1, user_2):  # проверяет Монго на связи между user_1 и user_2, возвращает
    # строку с цепочкой и глубину (глубина -1: цепочка не найдена)
    client = MongoClient("localhost", 27017, maxPoolSize=10000)
    collection = client['vacancies']

    pipeline = [{'$match': {'username': user_1}},
                {'$graphLookup': { # !!!
                    'from': 'facebook_parser',
                    'startWith': '$username',
                    'connectFromField': 'friends',
                    'connectToField': 'friends',
                    'as': 'connections',
                    'maxDepth': 10,
                    'depthField': 'depth',
                    'restrictSearchWithMatch': {}}},
                ]

    chain_raw = list(collection.facebook_parser.aggregate(pipeline))

    visited_links = []
    chain = f'{user_1}'
    depth = 0
    got_user_2 = False

    for item in chain_raw:
        for item_2 in item['connections']:
            if item_2['username'][0] == user_2:
                got_user_2 = True
            if item_2['username'][0] != user_1 and got_user_2:
                visited_links.append(item_2['username'][0])
                depth += 1
    for link in visited_links[::-1]:
        chain += f'-->{link}'
    return depth - 1, chain


def check_user(cursor, user):
    is_there = False
    for item in cursor:
        if item['username'][0] == user:
            is_there = True
    return is_there

def fill_queue(queue, friendlist):
    for item in friendlist:
        if item not in queue:
            queue.append(item)

class MainPipeline(object):

    def __init__(self):

        client = MongoClient('localhost', 27017)
        self.mongo_db = client['vacancies']

    def process_item(self, item, spider):

        collection = self.mongo_db[spider.name]
        cursor = collection.find()
        if not check_user(cursor, item['username'][0]): # проверяем нет ли такого в базе уже
            collection.insert_one(item) # закидываем в базу
            time.sleep(5)
            try: # проверяем цепочки и загружаем
                if find_chain(item['search'][0],item['search'][1])[0] < 0:
                    fill_queue(spider.queue, item['friends'])
            except IndexError:
                fill_queue(spider.queue, item['friends'])

            if not find_chain(item['search'][0],item['search'][1]):
                pass
            elif find_chain(item['search'][0],item['search'][1])[0] >= 0:
                spider.chain = find_chain(item['search'][0],item['search'][1])
                spider.queue = []
                print(spider.ask_for_chains()) # Печатаем tuple с глубиной и цепочкой. Конец.

        return item

# class AvitoPhotosPipelines(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         if item['photos']:
#             for img in item['photos']:
#                 try:
#                     yield scrapy.Request(img)
#                 except TypeError:
#                     pass
#
#     def item_completed(self, results, item, info):
#         if results:
#             item['photos'] = [itm[1] for itm in results if itm[0]]
#         return item
#
# class FacebookPhotosPipelines(ImagesPipeline):
#     def get_media_requests(self, item, info):
#
#         try:
#             if item['photos']:
#                 for img in item['photos']:
#                     try:
#                         yield scrapy.Request(img)
#                     except TypeError:
#                         pass
#         except KeyError:
#             pass
#
#     def item_completed(self, results, item, info):
#         if results:
#             item['photos'] = [itm[1] for itm in results if itm[0]]
#         return item