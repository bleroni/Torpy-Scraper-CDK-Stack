from time import time

def get_elements(soup): #html = bs(res.content)
    ret = {}

    seller_soup = soup.find('div', class_="mobile-seller-info")

    try:
        ret["price"] = f"{soup.find('bdi', class_='new-price').find('span')['value'].strip()} {soup.find('bdi', class_='new-price').get_text().strip()}"
    except Exception:
        ret["price"] = False

    try:
        ret["info"] = soup.find('div', class_="mobile-additional-info-area").get_text(separator='\n').replace("\n", "")
    except Exception:
        ret["info"] = False

    try:
        ret["title"] = soup.find('h1', class_="ci-text-base").text
    except Exception:
        ret["title"] = False

    try:
        ret["tags"] = {tag_pair.find("span").text.strip(): tag_pair.find("bdi").text.strip() for tag_pair in soup.find('div', class_="tags-area").findAll('a')}
    except Exception:
        ret["tags"] = False

    try:
        ret["description"] = soup.find('div', class_="description-area").find('span').get_text(separator='\n')
    except Exception:
        ret["description"] = False

    try:
        ret["sellerDescription"] = seller_soup.find("pre", class_="store-container ci-text-base").get_text()
    except Exception:
        ret["sellerDescription"] = False

    try:
        ret["sellerTitle"] = soup.find('div', class_="user-name ci-text-base").text
    except Exception:
        ret["sellerTitle"] = False

    ret["timestamp"] = time()

    return ret

def check_dup(title, data):
    stored_titles = [data[urn]["title"] for urn in data]
    return title in stored_titles
