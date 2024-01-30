from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chromedriver_py import binary_path
from selenium.webdriver.common.action_chains import ActionChains
import random
import pickle
import time
import json
import os
import requests

from .config import login_password, login_email, order_detail_page




def save_cookies(driver):
    # cookies = driver.get_cookies()

    cookies = {}
    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        cookies[cookie['name']] = cookie['value']
        
    with open('cookies_mod.json','w') as fp:
        json.dump(cookies,fp)
    
    
def move_cursor_randomly(driver):
    actions = ActionChains(driver)

    # Get the size of the browser window
    window_size = driver.get_window_size()
    window_width = window_size['width']
    window_height = window_size['height']

    # Generate random coordinates within the window
    random_x = random.randint(0, 80)
    random_y = random.randint(0, 100)

    # Move the cursor to the random coordinates
    
    actions.move_to_element_with_offset(driver.find_element(By.TAG_NAME,'body'), random_x, random_y)
    actions.perform()

# Move the cursor randomly multiple times (you can adjust the loop count)

    
def login(driver, email, password):
    for _ in range(3):
        move_cursor_randomly(driver)
    google = driver.find_element(By.XPATH,'//button[@class="sui-button-common sui-button-common__default sui-button-common__H44PX google-btn"]')
    actions = ActionChains(driver)
    actions.move_to_element(google).perform()
    login_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//input[@class="sui-input__inner sui-input__inner-suffix"]'))
    )
    login_input.send_keys(email)

    login_button = driver.find_element(By.XPATH, '//button[@class="sui-button-common sui-button-common__primary sui-button-common__H44PX page__login_mainButton"]')
    time.sleep(10)

    
    login_button.click()
    
    time.sleep(10)

    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="main-content"]/div/div[@class="input_filed-text"]/div[@class="sui-input"]/input[@class="sui-input__inner sui-input__inner-suffix"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView();", password_input)
    #time.sleep(8)
    password_input.click()
    password_input.send_keys(password)

    finish_button = driver.find_element(By.XPATH, '//div[4]/div[8]/div[1]/button[@class="sui-button-common sui-button-common__primary sui-button-common__H44PX page__login_mainButton"]')
    driver.execute_script("arguments[0].scrollIntoView();", finish_button)
    finish_button.click()

    driver.save_screenshot('screenshot.png')
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="skip"]/span'))
    ).click()
    
    time.sleep(5)
    
    links = driver.find_elements(By.XPATH,'//table[@class="c-order-detail-table new-order-table"]/tbody/tr/td[1]/div/div[@class="info"]/span/p/a')
    qty = driver.find_elements(By.XPATH,'//table[@class="c-order-detail-table new-order-table"]/tbody/tr/td[2]')
    sku = driver.find_elements(By.XPATH,'//table[@class="c-order-detail-table new-order-table"]/tbody/tr/td[3]')
    prices = driver.find_elements(By.XPATH,"//table[@class='c-order-detail-table new-order-table']/tbody/tr/td[4]/div/span[contains(@class,'struct-price__dis')]")
    
    items_list = []

    # Iterate through the elements and create dictionaries
    for link, quantity, sku, price in zip(links, qty, sku, prices):
        item_dict = {
            'link': link.get_attribute('href'),
            'qty': quantity.text.strip(),
            'SKU': sku.text.strip(),
            'price': price.text.strip()
        }
        items_list.append(item_dict)
    

    return items_list


def main():
    service_object = Service(binary_path)
    options = webdriver.ChromeOptions()
    userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service_object, options=options)
    driver.maximize_window()

    email = login_email
    password = login_password
   

    driver.get(order_detail_page)

    data = login(driver,email=email,password=password)
    
    driver.quit()
    
    return data
    

  






