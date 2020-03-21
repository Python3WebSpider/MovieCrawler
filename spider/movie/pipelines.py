# -*- coding: utf-8 -*-

class PgSQLPipeline():
    def process_item(self, item, spider):
        item.save()
        return item
