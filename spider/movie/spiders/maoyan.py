# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from furl import furl
from ..items import MovieItem


class MaoyanSpider(Spider):
    name = 'maoyan'
    allowed_domains = ['maoyan.com']
    start_url = 'https://maoyan.com/board/4'

    def start_requests(self):
        for index in range(10):
            offset = index * 10
            index_url = furl(self.start_url).add({
                'offset': offset
            }).url
            yield Request(index_url, callback=self.parse_index)

    def parse_index(self, response):
        for item in response.css('dl.board-wrapper dd'):
            rank = item.css('.board-index::text').extract_first()
            detail_href = item.css('p.name a::attr(href)').extract_first()
            detail_url = response.urljoin(detail_href)
            score = response.css('.score .integer::text').extract_first().strip() + \
                    response.css('.score .fraction::text').extract_first().strip()
            yield Request(detail_url, callback=self.parse_detail, meta={
                'rank': rank,
                'score': score
            })

    def parse_detail(self, response):
        rank = response.meta.get('rank')
        score = response.meta.get('score')
        name = response.css('h1.name::text').extract_first()
        alias = response.css('.ename::text').extract_first()
        categories = response.css('ul > li.ellipsis > a.text-link::text').extract()
        categories = [category.strip() for category in categories if category]
        info1 = response.css('ul > li.ellipsis:nth-child(2)::text').extract_first()
        regions = info1.split('/')[0].split(',') if len(info1.split('/')) else []
        regions = [region.strip() for region in regions if region]
        minute = response.css('ul > li.ellipsis:nth-child(2)::text').re_first('(\d+)分钟')
        published_at = response.css('ul > li.ellipsis:nth-child(3)::text').re_first('(\d{4}-\d{2}-\d{2})')
        cover = response.css('.avatar-shadow .avatar::attr(src)').extract_first()
        drama = response.css('.mod-content span.dra::text').extract_first()
        directors = []
        directors_info = response.xpath(
            '//div[@class="celebrity-type" and normalize-space() = "导演"]/following-sibling::ul[contains(@class, "celebrity-list")]//li')
        for director_info in directors_info:
            director_image = director_info.xpath(
                './/a[@class="portrait"]/img[@class="default-img"]/@data-src').extract_first()
            director_name = director_info.xpath('.//a[@class="name"]/text()').extract_first()
            director_name = director_name.strip() if director_name else None
            if director_name:
                directors.append({
                    'name': director_name,
                    'image': director_image
                })
        actors_info = response.xpath(
            '//div[contains(@class, "tab-celebrity")]//div[@class="celebrity-type" and contains(text(), "演员")]/following-sibling::ul[contains(@class, "celebrity-list")]//li[contains(@class, "actor")]')
        actors = []
        for actor_info in actors_info:
            actor_name = actor_info.xpath('.//a[@class="name"]/text()').extract_first()
            actor_name = actor_name.strip() if actor_name else None
            actor_role = actor_info.xpath('.//span[@class="role"]/text()').re_first('饰：(.*)')
            actor_role = actor_role.strip() if actor_role else None
            actor_image = actor_info.xpath(
                './/a[@class="portrait"]/img[@class="default-img"]/@data-src').extract_first()
            if actor_name and actor_role:
                actors.append({
                    'name': actor_name,
                    'role': actor_role,
                    'image': actor_image
                })
        photos = response.xpath('//div[contains(@class, "tab-img")]//li//img[@class="default-img"]/@data-src').extract()
        item = MovieItem({
            'name': name,
            'alias': alias,
            'score': score,
            'rank': rank,
            'cover': cover,
            'regions': regions,
            'categories': categories,
            'minute': minute,
            'published_at': published_at,
            'drama': drama,
            'directors': directors,
            'actors': actors,
            'photos': photos,
        })
        yield item
