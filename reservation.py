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

load_dotenv()

url_str = os.getenv('URL')
username_str = os.getenv('USERNAME')
password_str = os.getenv('PASSWORD')

email_message = ""

def login(browser):
    print("Logging in...")
    browser.find_element(By.NAME, "username").send_keys(username_str)
    browser.find_element(By.NAME, "password").send_keys(password_str)
    browser.find_element(By.XPATH, "//input[@value='Log In']").click()
    print("Login Succeeded\n")

# back = False - go back to previous page
def make_reservation(browser, date, slots, back):
    global email_message
    reserved = []
    for slot in slots:
        try:
            if back:
                browser.back()

            slot_container = browser.find_element(By.XPATH, f"//td[@style='width:14%; vertical-align:top;']/div[@date='{date}']")
            slot_container.find_element(By.XPATH, f".//div[contains(text(), 'Slot {slot}')]").click()
            
            xpath1 = "//div[@class='red']" # max registration exceeded
            xpath2 = "//div[@class='alert red']" # no slots
            xpath3 = "//div[@id='idPersonRegistered']" # already registered
            try:
                try:
                    # alert_div = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, xpath1)))
                    alert_div = browser.find_element(By.XPATH, xpath1) 
                except Exception:
                    alert_div = browser.find_element(By.XPATH, xpath2) 
            except Exception:
                try:
                    alert_div = browser.find_element(By.XPATH, xpath3) 
                except Exception:
                    alert_div = "can register"
            
            if not isinstance(alert_div, str):
                alert_div_text = alert_div.text

            try:
                # WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "reserve_1"))).click()
                browser.find_element(By.ID, "reserve_1").click()

                reserved_div = browser.find_element(By.ID, "idPersonRegistered")
                if "registered for this class" in reserved_div.text:
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
            send_email(f"Reservation failed for {slot} on {date}:", str(e))
            browser.quit()
    
    browser.back()

    return reserved
        
def main():
    global email_message
    slots = read_slots()
    
    options = Options()
    options.add_argument("--headless")

    service = ChromeService()
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url_str + "/login.cfm")

    login(browser)

    calendar_button = browser.find_element(By.XPATH, "//*[@id='idNavigation']/ul/li[2]/a")
    user_id = calendar_button.get_attribute('href').split('=')[-1].split(':')[-1]

    calendar_button.click()

    dates, days_str = generate_weekly_dates()
    for date, day in zip(dates, days_str):
        msg = f"==== Reserving slots on {date} ({day}) =====\n\n"
        email_message += msg
        print(msg)
        date_link = f"{url_str}/calendar.cfm?DATE={date}&calendarType=PERSON:{user_id}&VIEW=week&PERSONID:{user_id[2::]}"
        browser.get(date_link)

        reserved_slots = make_reservation(browser, date, slots, False)
        
        msg = f"Slot reserved: {reserved_slots}\n\n"
        email_message += msg
        print(msg)

    send_email(f"Reserved slots and dates", email_message)
    browser.quit()


if __name__ == "__main__":
    main()
    
