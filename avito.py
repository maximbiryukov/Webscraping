import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup

import lxml
import time
import random


mongo_url = 'mongodb://localhost:27017'
client = MongoClient('localhost', 27017)
database = client.avito

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/76.0.3809.100 Chrome/76.0.3809.100 Safari/537.36'


def get_ads(url):

    base_url = 'https://www.avito.ru'

    response = requests.get(url, headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(response.text, 'lxml')

    try:
        price = soup.body.findAll('span', attrs={'class': 'js-item-price', 'itemprop': 'price'})[0].attrs.get('content')
    except IndexError:
        price = None

    name = soup.body.find('div', attrs={'class':'seller-info-name js-seller-info-name'}).text.strip('\n').strip(' ').strip('\n')

    seller = soup.body.find('div', attrs={'class':'seller-info-name js-seller-info-name'}).find('a')

    if seller:
        seller_link = soup.body.find('div', attrs={'class':'seller-info-name js-seller-info-name'}).find('a').attrs.get('href')
    else:
        seller_link = None

    result = {'seller_name': name if name else None,
              'seller_link': base_url+seller_link if seller_link else None,
              'params': [tuple(itm.text.split(':')) for itm in
                         soup.body.findAll('li', attrs={'class': 'item-params-list-item'})],
              'price': int(price) if price and price.isdigit else None,
              'url': response.url
              }

    return result


def get_urls(category, pagenum): # category - категория обьявления (1 для просмотра квартир на продажу)

    base_url = 'https://www.avito.ru/'

    url = 'https://www.avito.ru/moskva/kvartiry'

    urls = []

    for i in range(pagenum):

        params = {'cd': category, 'p': i}

        response = requests.get(url, headers={'User-Agent': USER_AGENT}, params=params ,proxies={'ip': 'port'})

        soup = BeautifulSoup(response.text, 'lxml')

        body = soup.html.body

        ads = body.findAll('a', attrs={'class': 'item-description-title-link'})

        urls += [(base_url + itm['href']) for itm in ads]

    return urls


collection = database.avito

for itm in get_urls(1, 1):

    result = get_ads(itm)
    print(result)
    collection.insert_one(result)
    time.sleep(random.randint(1, 5))
