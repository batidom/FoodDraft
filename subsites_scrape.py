import json
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INPUT_FILE = "pyszne_restaurants_full.json"
OUTPUT_FILE = "pyszne_restaurants_details.json"
LOAD_TIMEOUT = 30

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = uc.Chrome(options=options)
    return driver

def accept_cookies(driver):
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler'))
        )
        btn.click()
        time.sleep(1)
    except:
        pass

def scrape_restaurant_details(driver, restaurant):
    url = restaurant['url']
    print(f"Scraping: {restaurant['name']}")

    try:
        driver.get(url)
        accept_cookies(driver)

        # Wait until the hero image loads
        WebDriverWait(driver, LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'restaurant-header-image-style_hero-image__img__Dahv_'))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # === Header image ===
        header_img = soup.select_one('img.restaurant-header-image-style_hero-image__img__Dahv_')
        restaurant['header_image'] = header_img['src'] if header_img and 'src' in header_img.attrs else None

        # === Avatar image ===
        avatar_img = soup.select_one('div.restaurant-header-style_avatar__PepGC img')
        restaurant['avatar_image'] = avatar_img['src'] if avatar_img and 'src' in avatar_img.attrs else None

        # === Colophon info (e.g. address, hours, etc.) ===
        colophon_section = soup.select_one('div.colophon-style_row__tBLCx')
        if colophon_section:
            divs = colophon_section.find_all('div')
            restaurant['colophon_info'] = [div.get_text(strip=True) for div in divs if div.get_text(strip=True)]
        else:
            restaurant['colophon_info'] = []

    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        restaurant['header_image'] = None
        restaurant['avatar_image'] = None
        restaurant['colophon_info'] = []

    return restaurant

def main():
    print("Loading restaurant URLs...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        restaurant_list = json.load(f)

    driver = setup_driver()
    scraped_data = []

    try:
        for restaurant in restaurant_list:
            enriched = scrape_restaurant_details(driver, restaurant)
            scraped_data.append(enriched)

        print(f"\nSaving results to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)
        print("Done.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
