import json
import scrapy
from Market_Spiders.items import MarketSpidersItem


class MiniPrecoSpider(scrapy.Spider):
    name = "minipreco"
    domain = "https://www.minipreco.pt"

    def start_requests(self):
        yield scrapy.Request(
            url=f"{self.domain}",
            callback=self.get_categories,
        )

    def get_categories(self, response):
        category = response.xpath(
            '//div[contains(@class, "category-link")]/a/@href'
        ).extract_first()

        yield scrapy.Request(
            url=self.domain + category,
            callback=self.get_category_product,
        )

    def get_category_product(self, response):
        category_product = (
            response.css('li[itemprop="itemListElement"]').css("a").attrib["href"]
        )

        yield from self.request_products(category_product=category_product)

    def request_products(self, category_product, page=0):
        string_page = f"?q=%3Arelevance&page={page}&disp="

        yield scrapy.Request(
            url=self.domain + category_product + string_page,
            callback=self.get_urls_products,
            meta={"page": page, "category_product": category_product},
        )

    def get_urls_products(self, response):
        meta = response.meta

        for url in response.css("div.product-list--row > div.product-list__item"):
            url_product = url.css("div.prod_grid > a::attr(href)").extract_first()

            yield scrapy.Request(
                url=self.domain + url_product, callback=self.get_products
            )

        next_page = response.css("li.next > a::attr(class)").get()
        if next_page != "btn-pager btn-pager--next disabled":
            yield from self.request_products(
                category_product=meta["category_product"],
                page=meta["page"] + 1,
            )

    def get_products(self, response):
        paht_product = response.css(
            "html > body > script:nth-of-type(2)::text"
        ).extract_first()
        process_string = (
            paht_product.split("obj= ")[1]
            .split(";")[0]
            .replace(" // Incidencia DIAEC-584, EMF, 201507", "")
            .replace("\"'", "['")
            .replace("'\"", "']")
            .replace("'", '"')
        )
        json_product = json.loads(process_string)

        sku = json_product["productoid"]
        name = json_product["fn"]
        brand = json_product["brand"]
        price = json_product["prize"]
        photo_urls = response.css("div.item > span > a > img::attr(data-zoomimagesrc)").extract()
        if not photo_urls:
            photo_urls = response.css('div.prod_image_main > a::attr(href)').extract()
        
        if price:
            price = str(price).strip().replace(" €", "")

        price_promotion = response.xpath('//*[@id="productDetailUpdateable"]/div[2]/div[1]/p/span[2]/text()').extract_first()
        if price_promotion:
            price_promotion = float(str(price_promotion).strip().replace("€", "").replace("\xa0", "").replace(",", "."))

        yield MarketSpidersItem({
            "sku": int(sku),
            "name": name,
            "brand": brand,
            "price": float(price),
            "price_promotion": price_promotion,
            "photo_urls": photo_urls
        })
