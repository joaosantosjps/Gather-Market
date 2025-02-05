import json
import scrapy
from Market_Spiders.items import MarketSpidersItem


class AtetiSpider(scrapy.Spider):
    name = "ateti"
    api_route = "https://www.ateti.pt/loja/loja"
    per_page = 40
    wp_cron = "1709923592.1213610172271728515625"

    def start_requests(self):
        yield from self.requests_products()

    def requests_products(self, page=1):
        url = "{}/page/{}/?per_page={}&s&post_type=product&doing_wp_cron={}".format(
            self.api_route, page, self.per_page, self.wp_cron
        )

        yield scrapy.Request(
            url=url,
            method="GET",
            callback=self.parse_urls,
            meta={"page": page},
            dont_filter=True,
        )

    def parse_urls(self, response):
        if response.status == 404:
            return

        meta = response.meta
        page = meta["page"]

        for urls_products in response.xpath('//div[@class="product-wrapper"]'):
            url_product = urls_products.css(
                "div.thumbnail-wrapper a::attr(href)"
            ).extract_first()
            brand = urls_products.css("div.product-brands a::text").extract_first()

            yield scrapy.Request(
                url=url_product,
                method="GET",
                callback=self.parse_products,
                meta={"brand": brand},
            )

        yield from self.requests_products(page + 1)

    def parse_products(self, response):
        meta = response.meta
        brand = meta["brand"]

        data_raw = response.xpath(
            '/html/body/script[@type="application/ld+json"]/text()'
        ).extract_first()
        data = json.loads(data_raw)

        if "@graph" in data:
            path_product = data.get("@graph")[1]
            name = path_product.get("name")
            sku_raw = path_product.get("sku")

            if "-" in str(sku_raw):
                sku = str(sku_raw).split("-", maxsplit=1)[0]
            else:
                sku = str(sku_raw)

            if len(sku) > 8 and len(sku) <= 13:
                eans = [int(sku)]
            else:
                eans = []

            yield MarketSpidersItem(
                {"sku": sku, "name": name, "brand": brand, "eans": eans}
            )
