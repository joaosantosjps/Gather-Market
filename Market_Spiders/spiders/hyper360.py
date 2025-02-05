import json
import scrapy
from Market_Spiders.utils import  get_cookies
from Market_Spiders.items import MarketSpidersItem


class Hyper360(scrapy.Spider):
    name = "hyper360"
    domain = "https://www.360hyper.pt"
    domain_api = "https://prd-360hyper-func-stores.azurewebsites.net"
    token = "Dq_fEbWFgppVBaq76w3kpO1cshnK09eMReqiUHBMrN06AzFu9qf6Lw=="
    postal_code = "3500-002"

    def start_requests(self):
        yield scrapy.Request(
            self.domain,
            headers=self.headers,
            callback=self.get_cookies_session
        )

    def get_cookies_session(self, response):
        self.cookies = get_cookies(response)

        verification_token = response.xpath('//input[@name="__RequestVerificationToken"]/@value').extract_first()
        self.headers["Requestverificationtoken"] = verification_token
        self.headers["Content-Type"] = "application/json"
        
        yield scrapy.Request(
            method="POST",
            headers=self.headers,
            url=f"{self.domain}/Store/UpdateStoreItemsCookie",
            body=json.dumps(
                {
                    "PostalCode": self.postal_code,
                    "AutoRedirectToLocalStore": False,
                    "IgnoreRedirectPopups": False,
                    "DownloadMobileAppLastTimeDisplayed": None,
                }
            ),
            cookies=self.cookies,
            callback=self.get_categories_markets,
        )

    def get_categories_markets(self, response):
        self.cookies = get_cookies(response)

        yield scrapy.Request(
            url=f"{self.domain_api}/api/Stores/Categories?culture=pt-PT&code={self.token}&postalCode={self.postal_code}",
            cookies=self.cookies,
            headers=self.headers,
            callback=self.get_store_categories
        )

    def get_store_categories(self, response):
        data = response.json()
        for category in data:
            category_id = category["id"]

            yield scrapy.Request(
                url=f"{self.domain_api}/api/Stores/Summary?culture=pt-PT&categoryId={category_id}&code={self.token}",
                cookies=self.cookies,
                headers=self.headers,
                callback=self.get_stores,
            )

    def get_stores(self, response):
        data = response.json()

        for store in data:
            store_url = store["storeUrl"].replace(self.domain, "")
            store_name = store_url[1:].split("/")[0]

            yield scrapy.Request(
                url=self.domain + store_url,
                callback=self.get_categories,
                cookies=self.cookies,
                headers=self.headers,
                meta={"store_url": store_url, "store_name": store_name},
            )

    def get_categories(self, response):
        meta = response.meta

        for category_id in response.xpath(
            '//div[contains(@class, "spc spc-categories landscape products-4")]/@data-categorygroupid'
        ).extract():
            yield from self.request_products(
                meta["store_url"], category_id, store_name=meta["store_name"]
            )

    def request_products(self, store_url, category_id, store_name, page=1):
        print(f"STORE NAME {store_name} | CATEGORY ID {category_id} | PAGE {page}")

        yield scrapy.Request(
            url=f"{self.domain}{store_url}category/products?categoryId={category_id}&pagenumber={page}",
            callback=self.get_products,
            cookies=self.cookies,
            headers=self.headers,
            meta={
                "store_url": store_url,
                "category_id": category_id,
                "page": page,
                "store_name": store_name,
            },
        )

    def get_products(self, response):
        meta = response.meta
        products = response.css("h2.product-title > a::attr(href)").extract()

        for product in products:
            yield scrapy.Request(
                url=self.domain + product,
                callback=self.get_product,
                cookies=self.cookies,
                headers=self.headers,
                meta={"store_name": meta["store_name"]},
            )

        if products:
            yield from self.request_products(
                store_url=meta["store_url"],
                category_id=meta["category_id"],
                page=meta["page"] + 1,
                store_name=meta["store_name"],
            )

    def get_product(self, response):
        meta = response.meta
        name = response.xpath('//meta[@itemprop="name"]/@content').extract_first()
        sku = response.xpath('//meta[@itemprop="sku"]/@content').extract_first()
        gtin = response.xpath('//meta[@itemprop="gtin"]/@content').extract_first()
        price_promotion = response.xpath(
            '//meta[@itemprop="price"]/@content'
        ).extract_first()
        price = response.xpath(
            '//span[@class="oldprice-value-54579"]/text()'
        ).extract_first()
        brand = None

        for row in response.css(
            "div#quickTab-specifications > div > div > table > tbody > tr"
        ):
            row_key = str(row.css("td.spec-name::text").extract_first()).strip()
            row_value = str(row.css("td.spec-value::text").extract_first()).strip()

            if row_key == "Marca":
                brand = row_value
                break

        if not price:
            price = float(price_promotion)
            price_promotion = None
        else:
            price = float(price.replace("€", ""))
            price_promotion = float(price_promotion)

        yield MarketSpidersItem({
            "name": name,
            "sku": sku,
            "eans": gtin.split(","),
            "price_promotion": price_promotion,
            "brand": brand,
            "price": price,
            "store_name": meta["store_name"],
        })
