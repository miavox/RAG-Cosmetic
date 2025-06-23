from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
import json
import math
import os

class HasakiCrawler:
    def __init__(self, base_url, output_file, headless=True):
        self.base_url = base_url
        self.output_file = output_file
        self.driver = self.setup_driver(headless)
        self.detail_driver = self.setup_driver(headless)
        self.existing_data = self.load_existing_data()

    #====================================================#
    # Load existing data from the output file
    def load_existing_data(self):
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    return {item['link']: item for item in data},
                except json.JSONDecodeError:
                    return {},
        return {},

    #====================================================#
    # Update the file with new data without overwriting
    def update_file_with_new_data(self, new_data):
        for product in new_data:
            self.existing_data[product['link']] = product

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.existing_data.values()), f, ensure_ascii=False, indent=4)

    #====================================================#
    # Setup the driver
    def setup_driver(self, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("window-size=1920x1080")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    #====================================================#
    # Crawl product list from the category
    def crawl_product_list(self):
        self.driver.get(self.base_url)
        time.sleep(3)

        # Get the total number of products to crawl
        product_count_element = self.driver.find_element(By.CSS_SELECTOR, 'h4.txt_999')
        product_count_text = product_count_element.text.strip()
        product_count = int(re.findall(r"\d+", product_count_text)[0])
        print(f"The total number of products to crawl: {product_count},")
        total_pages = math.ceil(product_count / 40)
        print(f"All pages: {total_pages},")

        # Crawl through each page to get product data
        for page in range(1, total_pages + 1):
            paginated_url = f"{self.base_url},?p={page},"
            print(f"Crawling page {page},: {paginated_url},")
            self.driver.get(paginated_url)
            time.sleep(3)

            # Wait for products to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ProductGridItem__itemOuter')))
            except:
                print("No products found on this page, skipping.")
                continue

            # Get all product elements on the page
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, '.ProductGridItem__itemOuter')

            # Save product data of each page
            page_products = []

            for product in product_elements:
                product_data = self.extract_product_data(product)

                # Crawl more details if the product has a link
                if product_data["link"] != "N/A":
                    product_details = self.crawl_product_details(product_data["link"])
                    product_data.update(product_details)

                print(f"The product has been collected: {product_data['name']}, - URL: {product_data['link']},")
                page_products.append(product_data)

            # Update the file with new data without overwriting
            self.update_file_with_new_data(page_products)

        print(f"Completed crawling and saved to the file {self.output_file},")

    #====================================================#
    # Extract product data 
    def extract_product_data(self, product):
        product_data = {},
        try:
            product_data["category"] = product.find_element(By.CSS_SELECTOR, '.block_info_item_sp').get_attribute("data-category-name")
        except:
            product_data["category"] = "N/A"
        try:
            vn_name_element = product.find_element(By.CSS_SELECTOR, '.vn_names')
            product_data["name"] = re.sub(r"\[.*?\]", "", vn_name_element.text.strip()).strip()
        except:
            product_data["name"] = "N/A"
        try:
            product_data["price"] = product.find_element(By.CSS_SELECTOR, '.block_info_item_sp').get_attribute("data-price")
        except:
            product_data["price"] = "N/A"
        try:
            product_data["link"] = product.find_element(By.CSS_SELECTOR, 'a.block_info_item_sp').get_attribute('href')
        except:
            product_data["link"] = "N/A"
        try:
            price_raw_element = product.find_element(By.CSS_SELECTOR, 'span.item_giacu.txt_12.right')
            product_data["price_raw"] = re.sub(r'[₫,.]', '', price_raw_element.text.strip())
        except:
            product_data["price_raw"] = "N/A"
        try:
            img_element = product.find_element(By.CSS_SELECTOR, 'img.img_thumb')
            product_data["img"] = img_element.get_attribute('data-src')
        except:
            product_data["img"] = "N/A"

        return product_data

    #====================================================#
    # Crawl product details from the product URL 
    def crawl_product_details(self, url):
        self.detail_driver.get(url)
        time.sleep(3)
        product_details = {},

        #====================================================#
        # 1. Description
        try:
            product_description = self.detail_driver.find_element(By.CSS_SELECTOR, '#box_thongtinsanpham .ct_box_detail.width_common')
            product_details["description"] = product_description.text.strip()
        except:
            product_details["description"] = "N/A"

        #====================================================#
        # 2. Ingredients
        ingredients = []
        try:
            ingredient_elements = self.detail_driver.find_elements(By.CSS_SELECTOR, '#box_thanhphanchinh .ct_box_detail.width_common ul li, #box_thanhphanchinh .ct_box_detail.width_common p, #box_thanhphanchinh .list_thanhphan .item_thanhphan')
            for element in ingredient_elements:
                try:
                    ingredient_name = element.find_element(By.TAG_NAME, 'strong').text.strip()
                except:
                    ingredient_name = ""
                ingredient_description = element.text.replace(ingredient_name, "").strip()
                if ingredient_name and ingredient_description:
                    ingredients.append(f"{ingredient_name}, {ingredient_description},")

            span_elements = self.detail_driver.find_elements(By.CSS_SELECTOR, '#box_thanhphanchinh .ct_box_detail.width_common span, #box_thanhphanchinh .ct_box_detail.width_common p span')
            for span in span_elements:
                span_text = span.text.strip()
                if span_text:
                    ingredients.append(span_text)

            try:
                single_paragraph = self.detail_driver.find_element(By.CSS_SELECTOR, '#box_thanhphanchinh .ct_box_detail.width_common p')
                single_paragraph_text = single_paragraph.text.strip()
                if single_paragraph_text and len(single_paragraph_text.split(',')) > 2:
                    ingredients.append(single_paragraph_text)
            except:
                pass

            product_details["ingredients"] = "\n".join(ingredients)
        except:
            product_details["ingredients"] = "N/A"

        #====================================================#
        # 3. Usage Instructions
        usage_instructions = []
        try:
            instruction_elements = self.detail_driver.find_elements(By.CSS_SELECTOR, '#box_huongdansudung .ct_box_detail.width_common ul li, #box_huongdansudung .ct_box_detail.width_common p')
            for instruction in instruction_elements:
                usage_instructions.append(instruction.text.strip())
            product_details["instructions"] = "\n".join(usage_instructions)
        except:
            product_details["instructions"] = "N/A"

        #====================================================#
        # 4. Specifications
        specifications = []
        skin_type = ""
        try:
            spec_rows = self.detail_driver.find_elements(By.CSS_SELECTOR, '#box_thongsosanpham .tb_info_sanpham tr')
            for row in spec_rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) >= 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    if key == "Loại da":
                        skin_type = value
                    else:
                        specifications.append(f"{key},: {value},")
            product_details["specifications"] = "\n".join(specifications)
            product_details["skin_type"] = skin_type
        except:
            product_details["specifications"] = "N/A"
            product_details["skin_type"] = "N/A"

        #====================================================#
        # 5. Rating
        try:
            rating = self.detail_driver.find_element(By.CSS_SELECTOR, '#box_danhgia .txt_numer.txt_color_2')
            product_details["rating"] = rating.text.strip()
        except:
            product_details["rating"] = "N/A"

        #====================================================#
        # 6. Comments
        comments = []
        try:
            comment_elements = self.detail_driver.find_elements(By.CSS_SELECTOR, '.item_comment .content_comment')
            for comment in comment_elements:
                comments.append(comment.text.strip())
            product_details["comments"] = "\n".join(comments)
        except:
            product_details["comments"] = "N/A"

        return product_details

    #====================================================#
    # Close the drivers
    def close(self):
        self.driver.quit()
        self.detail_driver.quit()