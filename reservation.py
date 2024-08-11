from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

load_dotenv()

url_str = os.getenv('URL')
username_str = os.getenv('USERNAME')
password_str = os.getenv('PASSWORD')

def generate_weekly_dates():
    today = datetime.today()
    days = []
    
    start_of_week = today - timedelta(days=today.weekday())
    
    for i in range(7):
        current_date = start_of_week + timedelta(days=i)
        if current_date.weekday() == 4 or current_date.weekday() == 5: # only Friday and Saturday
            days.append(current_date.strftime('%Y-%m-%d'))
    
    return days

def login(browser):
    print("Logging in...")
    browser.find_element(By.NAME, "username").send_keys(username_str)
    browser.find_element(By.NAME, "password").send_keys(password_str)
    browser.find_element(By.XPATH, "//button[@type='SUBMIT']").click()
    print("Login Succeeded")

def make_reservation(browser, slots):
    for slot in slots:
        try:
            browser.find_element(By.LINK_TEXT, slot).click()
            
            slot_div = browser.find_element(By.XPATH, "//*[@id='idPage']/div/div[2]")
            alert_red_div = slot_div.find_element(By.CLASS_NAME, "alert.red")
            alert_div = slot_div.find_element(By.CLASS_NAME, "alert")

            if "All available spots for this class session are now taken." in alert_div.text:
                print(f"No spots left for the {slot} session.")
                continue
            elif "registered for this class" in alert_div.text:
                print(f"Slot {slot} already registered")
            
            reserve_button = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='reserve_1']")))
            reserve_button.click()

            reserved_div = browser.find_element(By.ID, "idPersonRegistered")
            if "registered for this class" in reserved_div.text:
                print(f"Registration confirmed for slot {slot}")   
                return True, slot
            
        except Exception as e: 
            print(f"An error occurred while trying to reserve {slot}: {e}")
    
    return False, None
        
def main(slots):
    browser = webdriver.Chrome(executable_path='/opt/homebrew/bin/chromedriver')
    browser.get(url_str + "/login.cfm")

    login(browser)

    calendar_button = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='idNavigation']/ul/li[2]/a")))
    user_id = calendar_button.get_attribute('href').split('=')[-1].split(':')[-1]

    calendar_button.click()

    reservations = []
    for date in generate_weekly_dates():
        print(f"+++Booking slots on {date}+++")
        date_link = f"{url_str}/calendar.cfm?DATE={date}&calendarType=PERSON%3A7C84D896%2D17CC%2D4D8B%2D87EF%2D0F40C84D654B&VIEW=week&PERSONID={user_id}"
        browser.get(date_link)
        
        reserved, reserved_slot = make_reservation(browser, slots)
        if reserved:
            reservations.append((date, reserved_slot))
            print(f"Slot reserved: {date}  {reserved_slot}")


if __name__ == "__main__":
    slots = ["8:00 PM", "9:00 PM"]

    main(slots)
