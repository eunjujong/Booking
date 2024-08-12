from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta

load_dotenv()

url_str = os.getenv('URL')
username_str = os.getenv('USERNAME')
password_str = os.getenv('PASSWORD')

def generate_weekly_dates():
    days = []
    
    # cronjob runs on Sunday night UDT
    today = datetime.today()
    
    friday = today + timedelta((4 - today.weekday()) % 7)
    saturday = today + timedelta((5 - today.weekday()) % 7)
    
    days.append(friday.strftime('%Y-%m-%d'))
    days.append(saturday.strftime('%Y-%m-%d'))
    
    return days

def login(browser):
    print("Logging in...")
    browser.find_element(By.NAME, "username").send_keys(username_str)
    browser.find_element(By.NAME, "password").send_keys(password_str)
    browser.find_element(By.XPATH, "//input[@value='Log In']").click()
    print("Login Succeeded\n")

# back = False - go back to previous page
def make_reservation(browser, date, slots, back):
    reserved = []
    for slot in slots:
        try:
            if back:
                browser.back()

            slot_container = browser.find_element(By.XPATH, f"//td[@style='width:14%; vertical-align:top;']/div[@date='{date}']")
            slot_container.find_element(By.XPATH, f".//div[contains(text(), 'Slot {slot}')]").click()
            
            xpath1 = "//div[@class='alert red']"
            xpath2 = "//div[@id='idPersonRegistered']"
            try:
                # alert_div = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, xpath1)))
                alert_div = browser.find_element(By.XPATH, xpath1)
            except Exception:
                try:
                    # alert_div = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, xpath2)))
                    alert_div = browser.find_element(By.XPATH, xpath2)
                except Exception:
                    alert_div = "can register"
            
            if not isinstance(alert_div, str):
                alert_div_text = alert_div.text

            try:
                # WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "reserve_1"))).click()
                browser.find_element(By.ID, "reserve_1").click()

                reserved_div = browser.find_element(By.ID, "idPersonRegistered")
                if "registered for this class" in reserved_div.text:
                    print(f"Registration confirmed for slot {slot}\n")   

                reserved.append(slot)

                browser.back()

            except Exception:
                if "All available spots for this class session are now taken." in alert_div_text:
                    print(f"No slots left for the {slot} session\n")
                elif "registered for this class" in alert_div_text:
                    print(f"Slot {slot} already registered\n")
            
            if not back:
                back = True
            
        except Exception as e: 
            print(f"An error occurred while trying to reserve {slot}: {e}")
            browser.quit()
    
    browser.back()

    return reserved
        
def main(slots):
    service = Service(executable_path='/opt/homebrew/bin/chromedriver')
    browser = webdriver.Chrome(service=service)
    browser.get(url_str + "/login.cfm")

    login(browser)

    calendar_button = browser.find_element(By.XPATH, "//*[@id='idNavigation']/ul/li[2]/a")
    user_id = calendar_button.get_attribute('href').split('=')[-1].split(':')[-1]

    calendar_button.click()

    for date in generate_weekly_dates():
        print(f"==== Reserving slots on {date} =====\n")
        date_link = f"{url_str}/calendar.cfm?DATE={date}&calendarType=PERSON:{user_id}&VIEW=week&PERSONID:{user_id[2::]}"
        browser.get(date_link)

        reserved_slots = make_reservation(browser, date, slots, False)
        
        print(f"Slot reserved: {reserved_slots}\n")

    browser.quit()

if __name__ == "__main__":
    slots = ["8:00 PM", "9:00 PM"]

    main(slots)
