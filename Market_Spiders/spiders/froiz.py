import scrapy
from Market_Spiders.items import MarketSpidersItem


class Froiz(scrapy.Spider):
    name = "froiz"
    domain = "https://loja.froiz.com/"

    def start_requests(self):
        yield scrapy.Request(
            url=self.domain,
            callback=self.get_categories,
        )

    def get_categories(self, response):
        list_categorys_urls = response.css(
            "li.row > div > ul > li > a::attr(href)"
        ).extract()

        for category_url in list_categorys_urls:
            category = category_url.replace("corporativo/super.php", "")

            yield scrapy.Request(
                url=self.domain + category, callback=self.get_sub_category
            )

    def get_sub_category(self, response):
        list_id_category = response.css(
            "div.accordion-inner > ul > li > a::attr(href)"
        ).extract()

        for id_catedory in list_id_category:
            yield scrapy.Request(
                url=self.domain + id_catedory, callback=self.get_products_urls
            )

    def get_products_urls(self, response):
        list_urls_products = response.css("div.product-img a::attr(href)").extract()

        for url_product in list_urls_products:
            yield scrapy.Request(
                url=self.domain + url_product, callback=self.get_product
            )

    def get_product(self, response):
        sku = (
            response.css("div.span5 > div > div > img::attr(src)")
            .extract_first()
            .split("/")[1]
            .split(".")[0]
        )
        name = response.css("div.span7 > div > h3::text").extract_first()
        price = (
            response.css("div.span7 > div > div > span::text")
            .extract_first()
            .split("€")[0]
            .replace(" ", "")
            .replace(",", ".")
        )
        price_offer = response.css(
            "div.span7 > div > div > span > small::text"
        ).extract_first()

        if price_offer != None:
            price_promotion = (
                price_offer.split("€")[0]
                .replace("\n", "")
                .replace(",", ".")
                .replace(" ", "")
            )
        else:
            price_promotion = None

        yield MarketSpidersItem(
            {
                "sku": sku,
                "name": name,
                "price": price,
                "price_promotion": price_promotion,
            }
        )
