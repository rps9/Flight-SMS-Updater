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

    time.sleep(10)
    
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
    price_trend_text = trend_element.text.replace(" —", ";")
    
    driver.quit()

    #conver cheapest price to int
    flight_info = f"The current cheapest flight is ${cheapest_price}.\n\n{price_trend_text}."
    if cheapest_price < target_price:
        flight_info = f"BUY NOW! Flights are currently under your target price (${target_price})\n\n{flight_link}\n\n" + flight_info
    
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