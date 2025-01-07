from crawl_data.hasaki_crawler import HasakiCrawler

# Khởi tạo đối tượng và chạy chương trình
if __name__ == "__main__":
    url = ""
    crawler = HasakiCrawler(url, "")
    crawler.crawl_product_list()
    crawler.close()
    
    