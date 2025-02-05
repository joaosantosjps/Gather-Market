import scrapy
from Market_Spiders.items import MarketSpidersItem


class Apolonia(scrapy.Spider):
    name = "apolonia"
    domain = "https://www.apolonia.com/pt"

    def start_requests(self):
        yield scrapy.Request(
            url=f"{self.domain}",
            callback=self.get_categories,
        )

    def get_categories(self, response):
        for category in response.css("li.category > a::attr(href)").extract():
            yield from self.request_category(
                category=category.replace("/pt", ""), page=1
            )

    def request_category(self, category, page=1):
        string_page = f"?s%5Blimit%5D=50&s%5Border%5D=0&s%5Bprice%5D=&p={page}"

        yield scrapy.Request(
            url=self.domain + category + string_page,
            callback=self.get_product,
            meta={"page": page, "category": category},
        )

    def get_product(self, response):
        meta = response.meta

        for product in response.css("div.info"):
            sku = (
                product.css("a::attr(href)")
                .extract_first()
                .replace("/pt/catalogo/", "")
                .split("/")[0]
            )
            name = product.css("a::attr(title)").extract_first()
            brand = None
            price = (
                product.css("span > span.price > span.amount::text")
                .extract_first()
                .replace(",", ".")
            )
            price_promotion = product.xpath(
                'span[@class="prices-container"]/span[@class="price promocao"]/span[@class="amount"]/text()'
            ).extract_first()
            price_old = product.xpath(
                'span[@class="prices-container"]/span[@class="price original"]/span/span[@class="amount"]/text()'
            ).extract_first()

            if price_old:
                price = price_old.replace(",", ".")
                price_promotion = float(price_promotion.replace(",", "."))

            yield MarketSpidersItem(
                {
                    "sku": sku,
                    "name": name,
                    "brand": brand,
                    "price": float(price),
                    "price_promotion": price_promotion,
                }
            )

        next_page = response.css("li.setas.pagSeguinte > a::attr(href)").extract_first()
        if next_page:
            yield from self.request_category(
                category=meta["category"], page=meta["page"] + 1
            )
