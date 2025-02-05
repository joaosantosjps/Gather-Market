import scrapy


class MarketSpidersItem(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    eans = scrapy.Field()
    sku = scrapy.Field()
    price = scrapy.Field()
    price_promotion = scrapy.Field()
    measurement_value = scrapy.Field()
    measurement = scrapy.Field()
    photo_urls = scrapy.Field()
    markets_urls = scrapy.Field()
    store_name = scrapy.Field()
    created_at = scrapy.Field()
