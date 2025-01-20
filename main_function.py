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
    print("📨 Preparing to send email...")

    # Turn the emails into a list
    recipient_list = [email.strip() for email in recipient_emails.split(",") if email.strip()]
    print(f"✅ Recipients: {recipient_list}")

    try:
        # Connect to the notification email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        print("✅ Logged into SMTP server.")

        # Send the message
        for recipient_email in recipient_list:
            server.sendmail(sender_email, recipient_email, message)
            print(f"📩 Message sent to {recipient_email}")

        server.quit()
        print("✅ Email sending process completed successfully.")

    except Exception as e:
        print(f"❌ Error sending email: {e}")

def get_driver():
    print("🚗 Initializing WebDriver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    try:
        driver = webdriver.Chrome(service=ChromeService(), options=options)
        driver.set_window_size(1920, 1080)
        print("✅ WebDriver initialized successfully.")
        return driver
    except Exception as e:
        print(f"❌ Error initializing WebDriver: {e}")
        return None

def get_flight_info(flight_link, target_price):
    print(f"🔎 Navigating to: {flight_link}")
    driver = get_driver()
    
    if driver is None:
        return "❌ WebDriver failed to initialize."

    driver.get(flight_link)

    print("⏳ Waiting for page to load...")
    time.sleep(10)

    try:
        # Find the "Prices are currently" section
        print("🔍 Searching for price trend text...")
        trend_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Prices are currently')]"))
        )
        print("✅ Found price trend text.")

        # Find the "Cheapest" section
        print("🔍 Searching for cheapest price section...")
        cheapest_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Cheapest')]"))
        )
        print("✅ Found cheapest section.")

        # Find the 4th span after the "Cheapest" label
        print("🔍 Extracting cheapest price...")
        cheapest_price_element = cheapest_section.find_element(By.XPATH, ".//following-sibling::span[1]/span[1]/div/span")
        cheapest_price = int(cheapest_price_element.text.strip().replace("$", "").replace(",", ""))
        print(f"✅ Cheapest flight price: ${cheapest_price}")

        price_trend_text = trend_element.text.replace(" —", ";")
        print(f"📊 Price trend: {price_trend_text}")

    except Exception as e:
        print(f"❌ Error extracting flight data: {e}")
        driver.quit()
        return f"❌ Error extracting flight information: {e}"

    driver.quit()

    # Construct flight info message
    flight_info = f"The current cheapest flight is ${cheapest_price}.\n\n{price_trend_text}."
    if cheapest_price < target_price:
        flight_info = f"BUY NOW! Flights are currently under your target price (${target_price})\n\n{flight_link}\n\n" + flight_info
    
    return flight_info


def main():
    print("🚀 Starting Flight Tracker...")

    # Load environment variables
    #load_dotenv()
    print("✅ Loaded environment variables.")

    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('EMAIL_PASSWORD')
    recipient_emails = os.getenv('RECIPIENT_EMAILS')
    flight_link = os.getenv('FLIGHT_LINK')

    print(f"✉️ Sender Email: {sender_email}")
    print(f"📨 Recipients: {recipient_emails}")
    print(f"🔗 Flight Link: {flight_link}")

    if not sender_email or not sender_password or not recipient_emails or not flight_link:
        print("❌ Missing environment variables. Check your .env file or GitHub Secrets.")
        return

    target_price = 1000
    message = get_flight_info(flight_link, target_price)

    print("📢 Final message to send:")
    print(message)

    send_message(message, sender_email, sender_password, recipient_emails)


if __name__ == "__main__":
    main()
