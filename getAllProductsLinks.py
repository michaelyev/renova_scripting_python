import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def scrape_page(driver, page_number, baseurl, product_links, category):
    try:
        url = f'{baseurl}/flooring/{category}/{page_number}'
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products_list = soup.find_all('div', class_='view-details')
        for product in products_list:
            link = product.find('a', href=True)
            if link:
                product_links.append(baseurl + link['href'])
        print(f"Scraped page {page_number}")
    except Exception as e:
        print(f"An error occurred while scraping page {page_number}: {e}")

def scrape_product_links(min, max, category):
    try:
        baseurl = "https://shawfloors.com"
        product_links = []

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # Initialize the WebDriver with Chrome options
        driver = webdriver.Chrome(options=chrome_options)

        for page_number in range(min, max+1):
            scrape_page(driver, page_number, baseurl, product_links, category)

        driver.quit()
        print(f"Total product links found: {len(product_links)}")
        with open('product_links.json', 'w') as json_file:
            json.dump(product_links, json_file)
        return product_links

    except Exception as e:
        print(f"An error occurred while scraping product links: {e}")
        return []

# # Example usage
# total_pages_to_scrape = 2  # Adjust this value based on your requirements
# # scrape_product_links(total_pages_to_scrape)

# scrape_product_links(total_pages_to_scrape, 'vinyl')