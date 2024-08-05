import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def scrape_page(driver, page_number, baseurl, product_links, category,color):
    try:
        url = f'{baseurl}/flooring/hardwood/green/{page_number}'
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

def scrape_product_links(min, max, category, color):
    try:
        baseurl = "https://shawfloors.com"
        product_links = []

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # Initialize the WebDriver with Chrome options
        driver = webdriver.Chrome(options=chrome_options)

        for page_number in range(min, max+1):
            scrape_page(driver, page_number, baseurl, product_links, category, color)

        driver.quit()
        print(f"Total product links found: {len(product_links)}")
        with open(f'{category}_{color}_links.json', 'w') as json_file:
            json.dump(product_links, json_file)
        return product_links

    except Exception as e:
        print(f"An error occurred while scraping product links: {e}")
        return []

# # Example usage
total_pages_to_scrape = 6  # Adjust this value based on your requirements
# # scrape_product_links(total_pages_to_scrape)

scrape_product_links(1,1, 'hardwood', 'green')