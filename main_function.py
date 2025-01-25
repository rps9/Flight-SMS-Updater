import requests
import smtplib
from dotenv import load_dotenv
import os
from selenium import webdriver
import urllib.request
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

# Sends message using SMTP
def send_message(message, sender_email, sender_password, recipient_emails):
    # Turn the emails into a list
    recipient_list = [email.strip() for email in recipient_emails.split(",") if email.strip()]

    # Connect to the notification email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    # Send the message
    for recipient_email in recipient_list:
        server.sendmail(sender_email, recipient_email, message)

    server.quit()

def get_driver():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.set_window_size(1920, 1080)
    return driver


def get_flight_info(flight_link, target_price):
    driver = get_driver()

    driver.get(flight_link)

    time.sleep(30)
    
    where_from_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@aria-label, 'Where from?')]"))
    )
    where_from = where_from_element.get_attribute("value").strip()

    where_to_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@aria-label, 'Where to?')]"))
    )
    where_to = where_to_element.get_attribute("value").strip()

    departure_date_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Departure']"))
    )
    departure_date = departure_date_element.get_attribute("value").strip()

    return_date_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Return']"))
    )
    return_date = return_date_element.get_attribute("value").strip()

    trend_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Prices are currently')]"))
    )
    cheapest_section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Cheapest')]"))
    )

    # Find the 4th span after the "Cheapest" label
    cheapest_price_element = cheapest_section.find_element(By.XPATH, ".//following-sibling::span[1]/span[1]/div/span")

    # Extract the price text
    cheapest_price = int(cheapest_price_element.text.strip().replace("$", "").replace(",", "")) # Extract and convert to an int
    price_trend_text = trend_element.text.replace(" —", ";").strip()
    
    driver.quit()

    flight_info = f"The current cheapest flight from {where_from} to {where_to} is ${cheapest_price}.\nDate: {departure_date} -> {return_date}.\n\n{price_trend_text}.\n{flight_link}"
    if cheapest_price < target_price:
        flight_info = f"BUY NOW! Flights are currently under your target price (${target_price})\n\n" + flight_info
    
    return flight_info


    
def main():
    #load_dotenv() # UNCOMMENT FOR TESTING

    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('EMAIL_PASSWORD')
    recipient_emails = os.getenv('RECIPIENT_EMAILS')
    flight_link = os.getenv('FLIGHT_LINK')
    
    target_price = 1000
    message = get_flight_info(flight_link, target_price)
    print(message)

    send_message(message, sender_email, sender_password, recipient_emails)


if __name__ == "__main__":
    main()