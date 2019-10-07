# -*- coding: utf-8 -*-
import scrapy
import time
import json
import re
from urllib.parse import urlencode, urljoin
from copy import deepcopy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from scrapy.loader import ItemLoader
from selenium.webdriver.support.wait import WebDriverWait
from jobparser.items import FacebookItem


class FacebookSpider(scrapy.Spider):
    name = 'facebook'
    allowed_domains = ['facebook.com']
    start_urls = ['https://www.facebook.com/']
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_driver = webdriver.Chrome(chrome_options=chrome_options)

    def __init__(self, user_links, login, password, *args, **kwargs):
        self.user_links = user_links
        self.login = login
        self.password = password
        self.wait = WebDriverWait(self.chrome_driver, 10)
        super().__init__(*args, **kwargs)

    def _get_friends_list(self):
        return self.chrome_driver.find_elements_by_xpath('//*[contains(@id,"pagelet_timeline_medley_friends")][1]/div[2]/div/ul/li/div/a')

    def get_photos(self):

        self.chrome_driver.find_element_by_css_selector('#u_0_x').click()
        time.sleep(5)

        photos = []
        while True:
            if self.chrome_driver.find_elements_by_class_name('spotlight').__getitem__(0).get_attribute('src') not in photos:
                photos.append(self.chrome_driver.find_elements_by_class_name('spotlight').__getitem__(0).get_attribute('src'))
                self.chrome_driver.find_element_by_xpath(
                        '//*[@id="photos_snowlift"]/div[2]/div/div[1]/div[1]/div[1]/a[2]').click()
                time.sleep(5)
            else:
                break
        self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
        return photos

    def get_friends_list(self):

        num_of_loaded_friends = len(self._get_friends_list())
        while True:
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            time.sleep(7)
            if len(self._get_friends_list()) > num_of_loaded_friends:
                num_of_loaded_friends = len(self._get_friends_list())
                continue
            else:
                break

        return [friend.get_attribute('href') for friend in self._get_friends_list()]

    def parse(self, response):
        self.chrome_driver.get(response.url)
        username = self.chrome_driver.find_element_by_id("email")
        password = self.chrome_driver.find_element_by_id("pass")

        username.send_keys(self.login)
        password.send_keys(self.password)
        print(1)

        if not self.chrome_driver.find_element_by_id("loginbutton").click(): # логинимся
            try:
                self.chrome_driver.find_element_by_id("u_0_b").click()
            except ElementNotInteractableException:
                pass

        time.sleep(7)

        for user in self.user_links:

            self.chrome_driver.get(urljoin(self.start_urls[0], user)) # Заходим на страницу юзера

            name = self.chrome_driver.find_element_by_xpath('//*[@id="fb-timeline-cover-name"]/a').text # Вытаскиваем имя

            photos = self.get_photos() # Вытаскиваем фотки

            self.chrome_driver.find_element_by_css_selector('#u_0_10 > li:nth-child(3) > a').click() # переходим к списку друзей

            friends = self.get_friends_list() # Вытаскиваем список друзей

            loader = ItemLoader(item=FacebookItem())
            loader.add_value('name',name)
            loader.add_value('photos',photos)
            loader.add_value('friends',friends)

            yield loader.load_item()


