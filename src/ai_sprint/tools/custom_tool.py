import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List
import json
import re

class CustomScrapingTool:
    """Tool for scraping product information from e-commerce websites."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.dynamic_content_threshold = 3  # Number of retries for dynamic content

    def scrape_product_data(self, url_input: str) -> str:
        """Main method to scrape product data from a given URL."""
        try:
            # Clean and validate URL input
            url = self._preprocess_url(url_input)
            if not url:
                return json.dumps({"error": "Invalid URL format. URL must start with http:// or https://"})

            # Try scraping with requests first (faster for static content)
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Detect platform and scrape
            platform = self._detect_platform(url)
            products = self._scrape_by_platform(soup, platform)

            # If no products found, try dynamic scraping with Selenium
            if not products:
                products = self._scrape_dynamic_content(url, platform)

            if not products:
                return json.dumps({"error": "No products found on the page"})

            return json.dumps({"products": products, "platform": platform})

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Failed to fetch URL: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Error processing {url_input}: {str(e)}"})

    def _preprocess_url(self, url_input: str) -> str:
        """Clean and validate the URL."""
        url = url_input.strip().strip('"').strip("'").strip()
        if not url.startswith(('http://', 'https://')):
            return ""
        return url

    def _detect_platform(self, url: str) -> str:
        """Detect the e-commerce platform from the URL."""
        if 'amazon' in url.lower():
            return 'amazon'
        elif 'ebay' in url.lower():
            return 'ebay'
        elif 'walmart' in url.lower():
            return 'walmart'
        elif 'bestbuy' in url.lower():
            return 'bestbuy'
        return 'generic'

    def _scrape_by_platform(self, soup: BeautifulSoup, platform: str) -> List[Dict]:
        """Route scraping to appropriate method based on platform."""
        if platform == 'amazon':
            return self._scrape_amazon(soup)
        elif platform == 'ebay':
            return self._scrape_ebay(soup)
        elif platform == 'walmart':
            return self._scrape_walmart(soup)
        elif platform == 'bestbuy':
            return self._scrape_bestbuy(soup)
        return self._generic_scrape(soup)

    def _scrape_amazon(self, soup: BeautifulSoup) -> List[Dict]:
        """Scrape product information from Amazon pages."""
        products = []
        items = soup.select('.s-result-item[data-asin]:not([data-asin=""])') or \
                soup.select('.sg-col-inner')

        for item in items[:3]:
            try:
                title_elem = item.select_one('h2 a span') or item.select_one('.a-text-normal')
                price_elem = item.select_one('.a-price .a-offscreen') or item.select_one('.a-price-whole')
                rating_elem = item.select_one('i.a-icon-star-small span') or item.select_one('.a-icon-star')

                if not (title_elem and price_elem):
                    continue

                product = {
                    'title': title_elem.text.strip(),
                    'price': price_elem.text.strip(),
                    'rating': rating_elem.text.strip() if rating_elem else 'N/A',
                    'platform': 'Amazon'
                }
                products.append(product)

                if len(products) >= 3:
                    break

            except Exception:
                continue

        return products

    def _scrape_ebay(self, soup: BeautifulSoup) -> List[Dict]:
        """Scrape product information from eBay pages."""
        products = []
        items = soup.select('.s-item') or soup.select('.srp-results .s-item')

        for item in items[:3]:
            try:
                title_elem = item.select_one('.s-item__title')
                price_elem = item.select_one('.s-item__price')
                shipping_elem = item.select_one('.s-item__shipping')

                if not (title_elem and price_elem):
                    continue

                product = {
                    'title': title_elem.text.strip(),
                    'price': price_elem.text.strip(),
                    'shipping': shipping_elem.text.strip() if shipping_elem else 'N/A',
                    'platform': 'eBay'
                }
                products.append(product)

                if len(products) >= 3:
                    break

            except Exception:
                continue

        return products

    def _scrape_walmart(self, soup: BeautifulSoup) -> List[Dict]:
        """Scrape product information from Walmart pages."""
        products = []
        items = soup.select('.search-result-gridview-item') or soup.select('.search-result-product')

        for item in items[:3]:
            try:
                title_elem = item.select_one('.product-title-link') or item.select_one('.product-title')
                price_elem = item.select_one('.price-current') or item.select_one('.price-main')

                if not (title_elem and price_elem):
                    continue

                product = {
                    'title': title_elem.text.strip(),
                    'price': price_elem.text.strip(),
                    'platform': 'Walmart'
                }
                products.append(product)

                if len(products) >= 3:
                    break

            except Exception:
                continue

        return products

    def _scrape_bestbuy(self, soup: BeautifulSoup) -> List[Dict]:
        """Scrape product information from Best Buy pages."""
        products = []
        items = soup.select('.sku-item') or soup.select('.list-item')

        for item in items[:3]:
            try:
                title_elem = item.select_one('.sku-title') or item.select_one('.product-title')
                price_elem = item.select_one('.priceView-customer-price') or item.select_one('.price-main')

                if not (title_elem and price_elem):
                    continue

                product = {
                    'title': title_elem.text.strip(),
                    'price': price_elem.text.strip(),
                    'platform': 'Best Buy'
                }
                products.append(product)

                if len(products) >= 3:
                    break

            except Exception:
                continue

        return products

    def _generic_scrape(self, soup: BeautifulSoup) -> List[Dict]:
        """Scrape product information from unknown e-commerce platforms."""
        products = []
        price_patterns = ['$', '£', '€', 'USD', 'EUR']

        for pattern in price_patterns:
            if len(products) >= 3:
                break

            elements = soup.find_all(text=lambda text: text and pattern in text)

            for element in elements:
                if len(products) >= 3:
                    break

                try:
                    parent = element.parent
                    for _ in range(3):
                        if not parent:
                            break

                        title = parent.find('h1') or parent.find('h2') or parent.find('h3')
                        if title:
                            product = {
                                'title': title.text.strip(),
                                'price': element.strip(),
                                'platform': 'Unknown'
                            }

                            if not any(p['title'] == product['title'] for p in products):
                                products.append(product)
                                break

                        parent = parent.parent

                except Exception:
                    continue

        return products[:3]

    def _scrape_dynamic_content(self, url: str, platform: str) -> List[Dict]:
        """Scrape dynamic content using Selenium."""
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        try:
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
            )

            # Get the page source and parse it
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            return self._scrape_by_platform(soup, platform)

        except Exception as e:
            return []
        finally:
            driver.quit()