def get_cookies(response):
    original_cookies = response.headers.getlist("Set-Cookie")
    cookies = {}

    for item in original_cookies:
        item = item.decode("utf-8")
        item = item.split(";")[0]
        item = item.split("=")
        cookies["{0}".format(item[0])] = "=".join(item[1:])

    return cookies