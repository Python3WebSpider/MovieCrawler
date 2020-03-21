# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from scrapy_djangoitem import DjangoItem
from app.models import Movie


class MovieItem(DjangoItem):
    django_model = Movie
