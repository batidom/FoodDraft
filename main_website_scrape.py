import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://www.pyszne.pl/na-dowoz/jedzenie/20-117"
DELAY = 3  
SCROLL_PAUSE = 2  
LOAD_TIMEOUT = 30  
MAX_SCROLL_ATTEMPTS = 10  

def setup_driver():
    """Configure and return Chrome WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def accept_cookies(driver):
    """Handle cookie consent popup if present"""
    try:
        cookie_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler')))
        cookie_btn.click()
        time.sleep(1)
    except:
        pass

def scroll_to_bottom(driver):
    """Scroll to bottom of page to load more restaurants"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    
    while scroll_attempts < MAX_SCROLL_ATTEMPTS:
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        
        # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
            time.sleep(SCROLL_PAUSE)
            continue
            
        last_height = new_height
        scroll_attempts = 0  # Reset counter if new content loaded
        
        # Check if we've reached the end (no more restaurants loading)
        if "Nie znaleziono więcej restauracji" in driver.page_source:
            break

def scrape_restaurants(driver):
    """Extract all restaurant data after full page load"""
    # Wait for initial content
    WebDriverWait(driver, LOAD_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-qa="restaurant-card"]')))
    
    # Scroll to load all restaurants
    scroll_to_bottom(driver)
    
    # Get all restaurant cards
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.select('div[data-qa="restaurant-card"]')
    
    restaurants = []
    for card in cards:
        try:
            name = card.select_one('[data-qa="restaurant-info-name"]').text.strip()
        except:
            name = None
        
        try:
            url = "https://www.pyszne.pl" + card.select_one('a')['href']
        except:
            url = None
            
        try:
            rating = card.select_one('[data-qa="restaurant-ratings"]').text.strip()
        except:
            rating = None
            
        try:
            rating_count = card.select_one('[class="restaurant-ratings_votes___eTNG"]').text.strip('()')
        except:
            rating_count = None
            
        try:
            cuisine_types = card.select_one('[data-qa="restaurant-cuisine"]').text.strip()
        except:
            cuisine_types = None
            
        try:
            delivery_time = card.select_one('[data-qa="restaurant-eta"]').text.strip()
        except:
            delivery_time = None
            
        try:
            delivery_cost = card.select_one('[data-qa="restaurant-delivery-fee"]').text.strip()
        except:
            delivery_cost = None
            
        try:
            min_order = card.select_one('[data-qa="restaurant-mov"]').text.strip()
        except:
            min_order = None
            
        restaurants.append({
            'name': name,
            'url': url,
            'rating': rating,
            'rating_count': rating_count,
            'cuisine_types': cuisine_types,
            'delivery_time': delivery_time,
            'delivery_cost': delivery_cost,
            'min_order': min_order
        })
    
    return restaurants

def main():
    """Main scraping function"""
    print("Starting scraping process...")
    driver = setup_driver()
    
    try:
        # Load main page
        driver.get(BASE_URL)
        time.sleep(DELAY)
        accept_cookies(driver)
        
        # Scrape all restaurants (with scrolling)
        restaurants = scrape_restaurants(driver)
        
        if restaurants:
            with open('pyszne_restaurants_full.json', 'w', encoding='utf-8') as f:
                json.dump(restaurants, f, ensure_ascii=False, indent=2)
            print(f"Successfully scraped {len(restaurants)} restaurants")
        else:
            print("No restaurants were found")
            
    finally:
        driver.quit()
        print("Scraping completed")

if __name__ == "__main__":
    main()