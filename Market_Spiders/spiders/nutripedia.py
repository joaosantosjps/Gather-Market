import scrapy
from Market_Spiders.items import MarketSpidersItem

class NutripediaSpider(scrapy.Spider):
    name = "nutripedia"

    def start_requests(self):
        yield from self.requests_products()

    def requests_products(self, page=1):
        url = "https://nutripedia.pt/api/product?"
        querystring = f"page=%7B%22filter%22:%7B%22nutriscore%22:%5B%5D%7D,%22page%22:%22{page}%22,%22pageSize%22:24,%22query%22:%22%22,%22sort%22:%7B%22key%22:%22rank%22,%22order%22:1,%22orderNulls%22:1,%22operator%22:2%7D%7D"

        yield scrapy.Request(
            url=url + querystring,
            method="GET",
            callback=self.parse_products,
            headers={"cookie": "nutripedia-api-version=2024-02-19"},
            cookies={"nutripedia-api-version": "2024-02-19"},
            meta={"page": page},
        )

    def parse_products(self, response):
        meta = response.meta
        page = meta["page"]
        data = response.json()
        items = data["result"]

        for products in items:
            eans = products.get("ean")
            name = products.get("nome")
            brand = products.get("marca")
            markets_urls = list(products.get("supermercadoUrl", {}).values())

            yield MarketSpidersItem({
                "eans": eans,
                "name": name,
                "brand": brand,
                "markets_urls": markets_urls
            })

        if items:
            yield from self.requests_products(page+1)
