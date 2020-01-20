import urllib

def hyperlink_encode (text, base_url = "https://en.wikipedia.org/wiki/"):
    try:
        link = base_url + urllib.quote_plus(text.encode("utf-8").replace(" ", "_"))
        return link.encode('utf-8')
    except:
        return "0"
