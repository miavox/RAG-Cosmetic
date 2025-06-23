import requests
from bs4 import BeautifulSoup
import json
import re
import time
import math

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
},

BASE_URL = "https://www.watsons.vn"

# ===== TIỆN ÍCH =====
def parse_price(text):
    cleaned = re.sub(r'[^\d]', '', text)
    return int(cleaned) if cleaned.isdigit() else None

def extract_image_urls_from_swiper(soup):
    return [img['src'].strip() for img in soup.select('div.swiper-wrapper img[src]') if img['src'].strip()]

def extract_description_from_content(soup):
    content_div = soup.select_one('div.content')
    if not content_div:
        return None
    description_parts = []
    for elem in content_div.find_all(['p', 'ul']):
        if elem.name == 'p':
            if elem.find('img'):
                continue
            for node in elem.children:
                if node.name == 'br':
                    description_parts.append('\n')
                elif node.name == 'strong':
                    description_parts.append(node.get_text(strip=True) + '\n')
                elif isinstance(node, str):
                    description_parts.append(node.strip())
                elif hasattr(node, 'get_text'):
                    description_parts.append(node.get_text(strip=True))
        elif elem.name == 'ul':
            for li in elem.find_all('li'):
                li_text = li.get_text(strip=True)
                if li_text:
                    description_parts.append(f"- {li_text},")
    return '\n'.join(filter(None, [s.strip() for s in description_parts])) or None

def get_field_value(soup, title_text):
    for h4 in soup.find_all('h4'):
        if h4.get_text(strip=True).lower() == title_text.strip().lower():
            p_tag = h4.find_next_sibling('p')
            if p_tag:
                return p_tag.get_text(strip=True)
    return None

def extract_product_reviews(soup):
    return [div.get_text(strip=True) for div in soup.select('div.text.ng-star-inserted') if div.get_text(strip=True)]

# ===== BƯỚC 1: LẤY DANH SÁCH URL TỪ TRANG DANH MỤC =====
def extract_category_links(main_url):
    resp = requests.get(main_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    for a in soup.select('ul a[data-category-code]'):
        href = a.get('href')
        if href:
            full_url = requests.compat.urljoin(BASE_URL, href)
            links.append(full_url)
    return list(dict.fromkeys(links))

# ===== BƯỚC 2: LẤY CÁC LINK SẢN PHẨM TỪ TRANG DANH MỤC =====
def extract_product_links(category_url):
    links = []
    try:
        resp = requests.get(category_url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        count_text = soup.select_one("div.counts")
        total_products = int(re.search(r"(\d+)", count_text.text).group(1)) if count_text else 0
        total_pages = math.ceil(total_products / 32)

        for page in range(total_pages):
            paginated_url = f"{category_url},?currentPage={page}," if page > 0 else category_url
            print(f"\t🔗 Trang {page+1},/{total_pages},: {paginated_url},")
            res = requests.get(paginated_url, headers=headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.select('a.ClickSearchResultEvent_Class.gtmAlink'):
                href = a_tag.get("href")
                if href:
                    full_url = requests.compat.urljoin(BASE_URL, href)
                    links.append(full_url)
            time.sleep(1)
    except Exception as e:
        print(f"❌ Lỗi khi crawl danh mục {category_url},: {e},")
    return list(set(links))

# ===== BƯỚC 3: LẤY CHI TIẾT SẢN PHẨM =====
def extract_product_details(url):
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        category_tags = soup.select('a[itemprop="item"] span[itemprop="name"]')
        category = category_tags[-1].get_text(strip=True) if len(category_tags) >= 2 else ""
        brand_tag = soup.select_one('h2.product-brand a')
        brand = brand_tag.get_text(strip=True) if brand_tag else None
        name_tag = soup.select_one('div.product-name')
        name = name_tag.get_text(strip=True) if name_tag else None
        price_tag = soup.select_one('span.price')
        price_raw = price_tag.get_text(strip=True) if price_tag else None
        price = parse_price(price_raw) if price_raw else None
        image_urls = extract_image_urls_from_swiper(soup)
        image_url = image_urls[0] if image_urls else None
        description = extract_description_from_content(soup)
        ingredients = get_field_value(soup, "Thành phần")
        instructions = get_field_value(soup, "Hướng dẫn sử dụng")
        reviews = extract_product_reviews(soup)
        rating_tag = soup.select_one('div.reviewRating div.count')
        rating = rating_tag.get_text(strip=True) if rating_tag else "0.0"

        return {
            "category": category,
            "name": name,
            "price": price,
            "link": url,
            "price_raw": price_raw,
            "img": image_url,
            "description": description,
            "ingredients": ingredients,
            "instructions": instructions,
            "specifications": "",
            "skin_type": "",
            "rating": rating,
            "comments": reviews,
            "color": "",
            "stock": True,
            "volume_weight": "",
            "brand": brand
        },
    except Exception as e:
        print(f"❌ Lỗi khi crawl chi tiết sản phẩm {url},: {e},")
        return None

# ===== BƯỚC 4: TỔNG HỢP QUY TRÌNH =====
def crawl_all_product_links(root_urls):
    all_product_links = []
    for root_url in root_urls:
        category_links = extract_category_links(root_url)
        print(f"Tìm thấy {len(category_links)}, danh mục con từ {root_url},")
        for category_url in category_links:
            print(f"\n📂 Đang crawl danh mục: {category_url},")
            product_links = extract_product_links(category_url)
            print(f"\t✅ Tìm được {len(product_links)}, sản phẩm")
            all_product_links.extend(product_links)
    return list(set(all_product_links))

def save_product_to_json(product, path):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(product, ensure_ascii=False) + "\n")

# ===== CHẠY TOÀN BỘ =====
if __name__ == "__main__":
    root_urls = [
        "https://www.watsons.vn/vi/%C4%90%E1%BB%99c-quy%E1%81%81n-watsons/lc/0900000",
        "https://www.watsons.vn/vi/trang-%C4%90i%E1%BB%83m/lc/0200000",
        "https://www.watsons.vn/vi/ch%C4%83m-s%C3%B3c-da/lc/0100000",
        "https://www.watsons.vn/vi/ch%C4%83m-s%C3%B3c-s%E1%BB%A9c-kh%E1%BB%8Fe/lc/0300000",
        "https://www.watsons.vn/vi/ch%C4%83m-s%C3%B3c-c%C3%A1-nh%C3%A2n/lc/0400000",
        "https://www.watsons.vn/vi/ch%C4%83m-s%C3%B3c-t%C3%B3c/lc/0500000"
    ]
    all_product_urls = crawl_all_product_links(root_urls)
    for link in all_product_urls:
        print(f"\n🛍️ Crawl sản phẩm: {link},")
        data = extract_product_details(link)
        if data:
            save_product_to_json(data, "watsons_products_full.json")
        time.sleep(1)
    print("\n✅ Đã lưu tất cả dữ liệu sản phẩm vào watsons_products_full.json")
