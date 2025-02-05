import json
import scrapy
from Market_Spiders.items import MarketSpidersItem


class Elcorteingles(scrapy.Spider):
    name = "elcorteingles"
    domain = "https://www.elcorteingles.pt/supermercado"

    def start_requests(self):
        yield scrapy.Request(
            url=f"{self.domain}",
            callback=self.get_categories,
        )

    def get_categories(self, response):
        list_categorys_urls = response.css("nav.top_menu > a::attr(href)").extract()

        for category_url in list_categorys_urls[1:]:
            yield from self.request_category(category=category_url)

    def request_category(self, category):
        category = category.split("/supermercado")[1]

        yield scrapy.Request(
            url=self.domain + category,
            callback=self.get_products,
            meta={
                "category": category,
            },
        )

    def get_products(self, response):
        meta = response.meta

        for path_products in response.xpath(
            '//div[@class=" grid-item   product_tile _retro _supermarket  dataholder js-product "]'
        ):
            json_product = json.loads(path_products.xpath("@data-json").extract_first())
            eans = json_product["id"].replace("_", "")
            name = json_product["name"]
            brand = json_product.get("brand")

            if "original" in json_product["price"]:
                price_promotion = float(json_product["price"]["final"])
                price = float(json_product["price"]["original"])
            else:
                price_promotion = None
                price = float(json_product["price"]["final"])

            yield MarketSpidersItem(
                {
                    "eans": [eans],
                    "name": name,
                    "brand": brand,
                    "price": price,
                    "price_promotion": price_promotion,
                }
            )

        meta["category"] = response.xpath(
            '//li[@id="pagination-next"]/a/@href'
        ).extract_first()
        if meta["category"]:
            yield from self.request_category(
                category=meta["category"],
            )
