import json
import scrapy
from unidecode import unidecode
from Market_Spiders.items import MarketSpidersItem


class OpenfoodfactsSpider(scrapy.Spider):
    name = "openfoodfacts"

    def start_requests(self):
        yield from self.requests_products()

    def requests_products(self, page=1):
        url = f"https://pt.openfoodfacts.org/cgi/search.pl?action=process&sort_by=unique_scans_n&page_size=20&page={page}&sort_by=unique_scans_n"

        yield scrapy.Request(
            url=url,
            method="GET",
            headers=self.headers,
            callback=self.parse_products,
            meta={"page": page},
            dont_filter=True,
        )

    def parse_products(self, response):
        meta = response.meta
        page = meta["page"]

        block_products = response.xpath(
            "//script[@type='text/javascript']/text()"
        ).extract_first()
        data = json.loads(block_products.split("var products = ")[1].replace(";", ""))
        for products in data:
            eans = products.get("code")

            if len(eans) > 8 and len(eans) <= 13:
                eans = [int(eans)]
            else:
                eans = []

            name = unidecode(products.get("product_display_name"))
            products_urls = products.get("url")

            if eans:
                yield scrapy.Request(
                    url=products_urls,
                    method="GET",
                    headers=self.headers,
                    callback=self.get_brand,
                    meta={"item": {"eans": eans, "name": name}},
                )

        if data:
            yield from self.requests_products(page + 1)

    def get_brand(self, response):
        meta = response.meta
        item = meta["item"]

        brand = response.xpath(
            '/html/head/meta[@name="twitter:data1"]/@content'
        ).extract_first()
        item["brand"] = brand

        yield MarketSpidersItem(item)
