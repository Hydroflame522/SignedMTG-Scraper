from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore
from datetime import datetime
import xlsxwriter
import os
import shutil
import time
import string
import random
import argparse

def generate_random_suffix(length=6):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrape tcgplayer listings for signed cards. See https://github.com/Hydroflame522/SignedMTG-Scraper for additional documentation")
    parser.add_argument("-n", "--name", type=str, help="Search for a card by name. Place quotation marks around this query.")
    parser.add_argument("-c", "--color", type=str, help="Search for a card by color. Acceptable values are White, Blue, Black, Red, Green, Colorless.")
    parser.add_argument("-s", "--seller", type=str, help="Search for a card by tcgplayer Seller ID. Go to the feedback page of the seller you want, and their seller ID will be in the URL (ex. 43db324c).")
    parser.add_argument("-t", "--type", type=str, help="Search for a card by card type. Acceptable values are Creature, Artifact, Legendary, Land, Instant, Sorcery, Enchantment, Planeswalker.")
    parser.add_argument("-r", "--rarity", type=str, help="Search for a card by rarity. Acceptable values are Common, Uncommon, Rare, Mythic, Special, Token, Land, Promo.")
    parser.add_argument("-a", "--altered", action="store_true", help="Add the filters for altered cards to the task. Will add "alter" to the filter words.")
    parser.add_argument("-g", "--graded", action="store_true", help="Add the filters for graded cards to the task. Will add "bgs", "cgc", "psa", "graded" to the filter words.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Meant for development, adds extra debug logs to the command line.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    color = args.color
    name = args.name
    seller = args.seller
    type = args.type
    rarity = args.rarity
    verbose = args.verbose
    altered = args.altered
    graded = args.graded

    random_suffix = generate_random_suffix()
    output_filename = f'output_{random_suffix}.xlsx'

    start_time = datetime.now()
    print(Fore.CYAN + f"[{start_time.strftime('%H:%M:%S')}] Initializing Scrape..." + Fore.RESET)

    driver = webdriver.Chrome()
    workbook = xlsxwriter.Workbook(output_filename)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 50)
    worksheet.set_column('C:D', 10)

    worksheet.write(0, 0, "Product Link")
    worksheet.write(0, 1, "Listing Title")
    worksheet.write(0, 2, "Listing URL")
    worksheet.write(0, 3, "Price")

    if not os.path.isdir("tmp"):
        os.mkdir("tmp")

    row_count = 1
    total_listings_indexed = 0

    def scrape_signed_listings():
        global row_count, total_listings_indexed
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//section[@class='listing-item']")))
        except:
            if verbose:
                print("No listings found on this page. Skipping.")
            return

        processed_listings = set()

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            listings = driver.find_elements(By.XPATH, "//section[@class='listing-item']")
            if verbose:
                print(f"Found {len(listings)} listings on the page.")

            for listing in listings:
                total_listings_indexed += 1
                try:
                    title_element = listing.find_element(By.XPATH, ".//div[@class='listing-item__listing-data__listo__title']/div")
                    title = title_element.text.strip().replace("View Details", "").strip()
                    if verbose:
                        print("Title:", title)

                    keywords = ["artist", "signed", "signature"]
                    if altered:
                        keywords += ["alter"]
                    if graded:
                        keywords += ["graded", "bgs", "cgc", "psa", "tcg"]

                    if not any(keyword.lower() in title.lower() for keyword in keywords):
                        if verbose:
                            print("Skipping listing: Title does not contain keywords.")
                        continue

                    listing_url_element = listing.find_element(By.XPATH, ".//a[@class='listing-item__listing-data__listo__see-more']")
                    listing_url = listing_url_element.get_attribute("href")
                    if verbose:
                        print("Listing URL:", listing_url)

                    price_element = listing.find_element(By.XPATH, ".//div[@class='listing-item__listing-data__info__price']")
                    price = price_element.text.strip()
                    if verbose:
                        print("Price:", price)

                    if listing_url in processed_listings:
                        if verbose:
                            print("Skipping duplicate listing:", listing_url)
                        continue

                    processed_listings.add(listing_url)

                    worksheet.write(row_count, 0, driver.current_url)
                    worksheet.write(row_count, 1, title)
                    worksheet.write(row_count, 2, listing_url)
                    worksheet.write(row_count, 3, price)

                    log_time = datetime.now()
                    print(Fore.GREEN + f"[{log_time.strftime('%H:%M:%S')}] Wrote row {row_count}: {title}, {price}" + Fore.RESET)
                    row_count += 1
                except Exception as e:
                    print(f"Error processing listing: {str(e)}")

            try:
                next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
                if "disabled" in next_button.get_attribute("class"):
                    if verbose:
                        print("No more pages available.")
                    break

                driver.execute_script("arguments[0].click();", next_button)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//section[@class='listing-item']"))
                )
            except Exception as e:
                print(f"Error clicking next button: {str(e)}")
                break


    def scrape_by_query():
        base_url = "https://www.tcgplayer.com/search/magic/product?productLineName=magic&ProductTypeName=Cards&view=grid&inStock=true&ListingType=custom"
        query_filters = ""

        if name:
            query_filters += f"&q={name.replace(' ', '+')}"
        if color:
            query_filters += f"&Color={color}"
        if seller:
            query_filters += f"&seller={seller}"
        if type:
            query_filters += f"&RequiredTypeCb={type}"
        if rarity:
            query_filters += f"&Rarity={rarity}"

        if query_filters == "":
            duration = 10
            print(Fore.YELLOW + "Warning: You have specified no arguments, so the scraper will start to search ALL magic cards. Press 'CTRL'+'C' to cancel." + Fore.RESET)

            for i in range(duration, 0, -1):
                print(Fore.YELLOW + f"Proceeding with task in {i}..." + Fore.RESET)
                time.sleep(1)

        print(Fore.MAGENTA + f"Scrape started with query: '{query_filters}'" + Fore.RESET)
        driver.get(base_url + query_filters)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='search-result']"))
        )

        while True:
            product_links = driver.find_elements(By.XPATH, "//div[@class='search-result']//a[contains(@href, '/product/')]")
            if verbose:
                print(f"Found {len(product_links)} product links on the page.")

            for link in product_links:
                product_url = link.get_attribute("href")
                if verbose:
                    print(f"Scraping listings for product: {product_url}")

                driver.execute_script("window.open(arguments[0]);", product_url)
                driver.switch_to.window(driver.window_handles[1])  # Switch to the new tab

                scrape_signed_listings()

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='search-result']"))
                )

            try:
                next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
                if "disabled" in next_button.get_attribute("class"):
                    if verbose:
                        print("No more pages available.")
                    break

                driver.execute_script("arguments[0].click();", next_button)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='search-result']"))
                )
            except Exception as e:
                print(f"Error clicking next button: {str(e)}")  # Print only the error message
                break


    scrape_by_query()

    workbook.close()
    driver.quit()
    shutil.rmtree("tmp")

    end_time = datetime.now()
    total_time_seconds = (end_time - start_time).total_seconds()
    elapsed_minutes = int(total_time_seconds // 60)
    elapsed_seconds = int(total_time_seconds % 60)

    print(Fore.CYAN + f"[{end_time.strftime('%H:%M:%S')}] Scanned {total_listings_indexed} listings with photos in {elapsed_minutes}m {elapsed_seconds}s" + Fore.RESET)
    print(Fore.CYAN + f"[{end_time.strftime('%H:%M:%S')}] Scrape Complete, {row_count - 1} entries made to {output_filename}" + Fore.RESET)