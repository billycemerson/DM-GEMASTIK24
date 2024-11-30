from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

def scrape_google_maps(query):
    driver.get("https://www.google.com/maps")
    wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@id="searchboxinput"]')))
    search_box = driver.find_element(By.XPATH, '//input[@id="searchboxinput"]')
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    wait.until(EC.visibility_of_element_located((By.XPATH, '//span[@role="img"][@aria-label]')))

    # Click on "More reviews" button to load all reviews
    try:
        more_reviews_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Ulasan lainnya")]')))
        more_reviews_button.click()
        time.sleep(3)  # Wait for the reviews to load
    except Exception as e:
        print(f"Error occurred while clicking on 'More reviews': {e}")

    # Loop to load more reviews and extract data multiple times
    all_reviews = []
    iterations = 5  # Adjust the number of iterations as needed

    for i in range(iterations):
        # Infinite scroll to load more reviews
        scroll_pause_time = 5
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract reviews after scrolling
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        reviews = soup.find_all("div", class_="jftiEf fontBodyMedium")

        for review in reviews:
            href_tag = review.find("button", attrs={"data-href": True})
            href = href_tag['data-href'] if href_tag else "No href found"
            rating_tag = review.find("span", role="img")
            rating = rating_tag['aria-label'] if rating_tag else "No rating found"
            review_text_tag = review.find("span", class_="wiI7pd")
            review_text = review_text_tag.text if review_text_tag else "No review text found"
            all_reviews.append({"href": href, "rating": rating, "review_text": review_text})

        time.sleep(2)  # Wait before the next iteration

    # Save the data to a CSV file
    df = pd.DataFrame(all_reviews)
    csv_filename = query.replace(" ", "_") + '.csv'
    df.to_csv(csv_filename, index=False)

    driver.quit()

# Example usage
keyword = "Puskesmas Pembantu Tegalrejo"
scrape_google_maps(keyword)