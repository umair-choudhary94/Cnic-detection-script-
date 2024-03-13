from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException,TimeoutException
import pandas as pd
import time
import os
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from calendar import monthrange
def open_browser():
    
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=chrome_options)
    driver.maximize_window()
    return driver
def get_days_of_month(year, month):
    _, last_day = monthrange(year, month)
    return [datetime(year, month, day) for day in range(1, last_day + 1)]

# Loop through dates from today back to 2010
end_date = datetime(2010, 1, 1)
current_date = datetime.now()
# current_date = datetime(2022, 2, 6)
driver = open_browser()
num_windows = 5
while current_date >= end_date:
    # Open windows
    windows = [open_browser() for _ in range(num_windows)]

    # Switch to each window and perform some actions
    for i, window in enumerate(windows):
        window.get('https://nims.nadra.gov.pk/nims/certificate')

        wait = WebDriverWait(window, 30)

        cnic_input = wait.until(EC.presence_of_element_located((By.ID, "checkEligibilityForm:cnic")))
        cnic_input.send_keys("3220250766109")
        time.sleep(2)

        # Select a date from the calendar
        issue_date_input = window.find_element(By.ID, "checkEligibilityForm:issueDate_input")
        issue_date_input.click()

        date_to_select = current_date.strftime("%d")
        date_xpath = f"//a[contains(text(), '{date_to_select}')]"
        date_element = WebDriverWait(window, 30).until(EC.element_to_be_clickable((By.XPATH, date_xpath)))

        # try:

        try:
            actions = ActionChains(driver)
            actions.move_to_element(date_element).click().perform()
            WebDriverWait(driver, 30).until(
                lambda driver: issue_date_input.get_attribute("value") == date_to_select
            )

            time.sleep(3)

        except StaleElementReferenceException:
            print("Stale Element Exception after waiting. Element might not be clickable.")
            date_element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, date_xpath)))
            
            actions = ActionChains(driver)
            actions.move_to_element(date_element).click().perform()
            time.sleep(2)
            print("Element clicked successfully.")
        except TimeoutException:
            print(f"TimeoutException: Element not found or not clickable for {current_date.strftime('%Y-%m-%d')}")

        first_num = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div/section/div/div/div[1]/div/article/div/form/div[2]/div[3]/div/div[1]/span[1]')))
        second_num = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div/section/div/div/div[1]/div/article/div/form/div[2]/div[3]/div/div[1]/span[2]')))
        result_value = int(first_num.text) + int(second_num.text)

        captcha_input = driver.find_element(By.CSS_SELECTOR, '.submit__input')
        captcha_input.send_keys(str(result_value))

        confirm_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div/section/div/div/div[1]/div/article/div/form/div[3]/input')))
        confirm_button.click()

        # Find the element by its ID
        message_element = driver.find_element(By.ID, "checkEligibilityForm:messages")

        # Check if the message is present
        is_message_present = message_element.is_displayed()

        # Print the result
        print(f"{current_date.strftime('%Y-%m-%d')}: {is_message_present}")

        # Move to the previous date
        current_date -= timedelta(days=1)
        driver.quit()
    

# Close the browser window
driver.quit()
