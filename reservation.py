from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from slots import read_slots
from generate_dates import generate_weekly_dates
from notification import send_email
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import DATE_SLOT_MAP
import json
import time

load_dotenv()

url_str = os.getenv('URL')

email_message = ""

def login(browser, username, password):
    print(f"Logging in for {username[:3]}*****...")
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.XPATH, "//input[@value='Log In']").click()
    if browser.current_url == url_str + "/person.cfm":
        print(f"Login succeeded")
        return True
    else:
        print(f"Login failed")
        return False

# back = False - go back to previous page
def make_reservation(browser, date, slot, back):
    global email_message
    reserved = []
    try:
        if back:
            browser.back()

        slot_container = browser.find_element(By.XPATH, f"//td[@style='width:14%; vertical-align:top;']/div[@date='{date}']")
        slot_container.find_element(By.XPATH, f".//div[contains(text(), 'Slot {slot}')]").click()
        
        xpath1 = "//div[@class='red' and contains(text(), 'You've reached the maximum limit of reservations per day')]" # max registration exceeded
        xpath2 = "//div[@class='alert red' and contains(text(), 'All available spots for this class session are now taken.')]" # no slots
        xpath3 = "//div[@id='idPersonRegistered' and contains(text(), 'is registered for this class.')]" # already registered
        try:
            try:
                # alert_div = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, xpath1)))
                alert_div = browser.find_element(By.XPATH, xpath1) 
            except:
                alert_div = browser.find_element(By.XPATH, xpath2) 
        except:
            try:
                alert_div = browser.find_element(By.XPATH, xpath3) 
            except:
                alert_div = "can register"
        
        if not isinstance(alert_div, str):
            alert_div_text = alert_div.text

        try:
            # WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "reserve_1"))).click()
            browser.find_element(By.ID, "reserve_1").click()

            reserved_div = browser.find_element(By.ID, "idPersonRegistered")
            if "can register" in alert_div_text and "registered for this class" in reserved_div.text:
                msg = f"Registration confirmed for slot {slot}\n"
                email_message += msg
                print(msg)

                reserved.append(slot)

            browser.back()

        except Exception:
            if "All available spots for this class session are now taken." in alert_div_text:
                msg = f"No slots left for the {slot} session\n"
                email_message += msg
                print(msg)
            if "You've reached the maximum limit of reservations per day." in alert_div_text:
                msg = f"Max registration reached for {date}\n"
                email_message += msg
                print(msg)
            if "registered for this class" in alert_div_text:
                msg = f"Slot {slot} already registered\n"
                email_message += msg
                print(msg)
        
        if not back:
            back = True
        
    except Exception as e: 
        print(f"An error occurred while trying to reserve {slot}: {str(e)}")
        email_message += "Reservation failed for {date} {slot}\n"
    
    browser.back()

    return reserved
        
def main():
    global email_message

    slot_count = 0

    days, days_str = generate_weekly_dates()

    usernames_passwords = os.getenv('USERNAMES_PASSWORDS')
    usernames_passwords_dict = json.loads(usernames_passwords)

    usernames = usernames_passwords_dict['usernames']
    passwords = usernames_passwords_dict['passwords']

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--incognito")

    service = ChromeService()
    browser = webdriver.Chrome(service=service, options=options)

    for username, password in zip(usernames, passwords):

        browser.get(url_str + "/login.cfm")
        
        login_attempt = login(browser, username, password)
        if not login_attempt:
            msg = f"Login failed for {username}"
            email_message += msg
            continue

        calendar_button = browser.find_element(By.XPATH, "//*[@id='idNavigation']/ul/li[2]/a")
        user_id = calendar_button.get_attribute('href').split('=')[-1].split(':')[-1]

        calendar_button.click()

        msg = f"\n==== Reservation Info for {username[:3]}***** =====\n"
        email_message += msg
        print(msg)

        slots = [slots[slot_count] for slots in DATE_SLOT_MAP.values() if slots]
        
        for date, day, slot in zip(days, days_str, slots):
            msg = f"{date} ({day}):\n"
            email_message += msg
            print(msg)

            date_link = f"{url_str}/calendar.cfm?DATE={date}&calendarType=PERSON%3A{user_id}&VIEW=week&PERSONID={user_id}"

            browser.get(date_link)
            reserved_slots = make_reservation(browser, date, slot, False)
                            
            msg = f"Slots reserved: {reserved_slots}\n"
            email_message += msg
            print(msg)

        slot_count = (slot_count + 1) % 2
        browser.find_element(By.XPATH, "//*[@id='idNavigation']/ul/li[6]").click() # log out
        
    browser.quit()

    send_email("Badminton Reservation", email_message)

if __name__ == "__main__":
    main()
    
