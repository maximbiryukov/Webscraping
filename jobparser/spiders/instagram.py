# -*- coding: utf-8 -*-
import scrapy
import json
import re
from urllib.parse import urlencode, urljoin
from copy import deepcopy
from scrapy.http import HtmlResponse
from jobparser.items import InstagramItem


class InstagramSpider(scrapy.Spider):

    name = 'instagram'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    # variables_base = {'fetch_mutual': 'false', "include_reel": 'true', "first": 100}
    variables_base = {'count': 100, 'first': 100}

    followers = {}

    def __init__(self, user_links, login, password, *args, **kwargs):
        self.user_links = user_links
        self.login = login
        self.password = password
        self.query_hash = 'c76146de99bb02f6415203be841dd25a'
        super().__init__(*args, **kwargs)

    def parse(self, response):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            'https://www.instagram.com/accounts/login/ajax',
            method='POST',
            callback=self.parse_users,
            formdata={'username': self.login, 'password': self.password},
            headers={'X-CSRFToken': csrf_token}
        )

    def parse_users(self, response=HtmlResponse):

        body = json.loads(response.body)

        if body.get('authenticated'):
            for user in self.user_links:
                yield response.follow(urljoin(self.start_urls[0], user),
                                      callback=self.parse_user_posts,
                                      cb_kwargs={'user': user})

    def parse_user_posts(self, response, user):

        data = json.loads(response.xpath('/html/body/*').extract()[4][52:-10])

        for i in range(10):
            code = data.get('entry_data').get('ProfilePage')[0].get('graphql').get('user').\
                    get('edge_owner_to_timeline_media').get('edges')[i].get('node').get('shortcode')

            yield response.follow(urljoin(self.start_urls[0], f'p/{code}'),
                                  callback=self.parse_post_comments,
                                  cb_kwargs={'user': user, 'code': code})

    def parse_post_comments(self, response, user, code):
        data = json.loads(response.xpath('/html/body/*').extract()[4][52:-10])
        comments = data.get('entry_data').get('PostPage')[0].get('graphql').get('shortcode_media').\
                    get('edge_media_to_parent_comment').get('edges')

        if len(comments) > 10:
            for i in range(10):
                text = comments[i].get('node').get('text')
                author = comments[i].get('node').get('owner').get('username')

                yield InstagramItem(user=user, post=self.start_urls[0]+'p/'+code, entry_type='comment',
                                    author=self.start_urls[0]+author, comment_text=text)
        else:
            for comment in comments:
                text = comment.get('node').get('text')
                author = comment.get('node').get('owner').get('username')

                yield InstagramItem(user=user, post=self.start_urls[0]+'p/'+code, entry_type='comment',
                                    author=self.start_urls[0]+author, comment_text=text)

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
