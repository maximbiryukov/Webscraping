import scrapy
import time
from urllib.parse import urljoin
from copy import deepcopy

import selenium
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from scrapy.loader import ItemLoader
from selenium.webdriver.support.wait import WebDriverWait

from jobparser.items import FacebookItem


def login(LOGIN, PWD, url='https://www.facebook.com/'):

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")
    chrome_driver = webdriver.Chrome(chrome_options=chrome_options)
    chrome_driver.get(url)

    try:
        username = chrome_driver.find_element_by_id("email") # перебираем три варианта первой страницы
        pwd = chrome_driver.find_element_by_id("pass")
    except selenium.common.exceptions.NoSuchElementException:

        try:

            username = chrome_driver.find_element_by_css_selector('#u_0_9 > div:nth-child(3) > input')
            pwd = chrome_driver.find_element_by_css_selector('#u_0_9 > div:nth-child(4) > input')
        except selenium.common.exceptions.NoSuchElementException:

            username = chrome_driver.find_element_by_css_selector('#u_0_9 > div:nth-child(4) > input')
            pwd = chrome_driver.find_element_by_css_selector('#u_0_9 > div:nth-child(5) > input')

    username.send_keys(LOGIN)
    pwd.send_keys(PWD)

    try:
        chrome_driver.find_element_by_id("loginbutton").click()  # логинимся
    except selenium.common.exceptions.NoSuchElementException:

        try:
            chrome_driver.find_element_by_id("u_0_b").click()
        except ElementNotInteractableException:
            try:
                chrome_driver.find_element_by_css_selector('#u_0_9 > div:nth-child(5) > button').click()
            except selenium.common.exceptions.NoSuchElementException:
                chrome_driver.find_element_by_css_selector('#u_0_9 > div:nth-child(6) > button').click()

    # chrome_driver.implicitly_wait(5)
    return chrome_driver




class FacebookSpider(scrapy.Spider):
    name = 'facebook_parser'
    allowed_domains = ['facebook.com']
    start_urls = ['https://www.facebook.com/']

    def __init__(self, users, driver):
        self.chrome_driver = driver
        self.wait = WebDriverWait(self.chrome_driver, 10)
        self.queue = deepcopy(users)
        self.search = deepcopy(users)
        self.chains = []

    def get_current_friends_list(self):
        return self.chrome_driver.find_elements_by_xpath('//*[contains(@id,"pagelet_timeline_medley_friends")][1]/'
                                                         'div[2]/div/ul/li/div/a')

    def ask_for_chains(self):
        return self.chains

    def get_friends_list(self):

        num_of_loaded_friends = len(self.get_current_friends_list()) # листаем страничку

        while True:

            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            time.sleep(5)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            time.sleep(5)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            self.chrome_driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            time.sleep(5)

            if len(self.get_current_friends_list()) > num_of_loaded_friends:
                num_of_loaded_friends = len(self.get_current_friends_list())
                continue
            else:
                break

        return [friend.get_attribute('href') for friend in self.get_current_friends_list()]

    def parse(self, response):

        while self.queue:
            user = self.queue.pop(0)
            self.chrome_driver.get(urljoin(self.start_urls[0], user))  # Заходим на страницу юзера

            name = self.chrome_driver.find_element_by_xpath('//*[@id="fb-timeline-cover-name"]/a').text  # Вытаскиваем имя

            try:
                self.chrome_driver.find_element_by_css_selector(
                    '#u_0_10 > li:nth-child(3) > a').click()  # переходим к списку друзей
            except selenium.common.exceptions.NoSuchElementException:
                self.chrome_driver.find_element_by_xpath('//*[@id="u_0_z"]/li[3]/a').click()

            time.sleep(2)

            friends = self.get_friends_list()  # Вытаскиваем список друзей

            loader = ItemLoader(item=FacebookItem())
            loader.add_value('name', name)
            loader.add_value('username', user)
            loader.add_value('friends', friends)
            loader.add_value('search', self.search)

            yield loader.load_item() # засылаем item в pipeline

