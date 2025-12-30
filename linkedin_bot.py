# LINKEDIN AUTO CONNECT 2025 by Sirat Wali
# By Sirat Wali (Updated & Tested: 8 December 2025)
# Works on ALL Profiles
# =======================================================

import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

# ==================== CONFIG ====================
CSV_FILE = "africa_fiber_operators_with_LinkedIn_Profile.csv"
OUTPUT_FILE = "africa_fiber_operators_linkedin_final_results.csv"
EMAIL = "@gmail.com"  # Enter LinkedIn-EMAIL
PASSWORD = ""            # Enter PASSWORD
DAILY_LIMIT = 3                  # Safe: 80–120 per day
MAX_WAIT = 20
# ================================================

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(chromedriver_autoinstaller.install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => false});"
    })
    return driver

def random_sleep(min_sec=3, max_sec=8):
    time.sleep(random.uniform(min_sec, max_sec))

def login_linkedin(driver):
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "username"))
    ).send_keys(EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)
    random_sleep(5, 9)
    print("Login attempt finished")

# ==================== FINAL SEND FUNCTION (DEC 2025) ====================
def click_send_without_note(driver, wait):
    send_xpaths = [
        "//button[contains(@class,'artdeco-button--primary') and .//span[text()='Send']]",
        "//button[.//span[text()='Send now']]//parent::button",
        "//button[.//span[text()='Send without a note']]//parent::button",
        "//button[@aria-label='Send now']",
        "//button[@aria-label='Send without a note']",
        "//div[@role='dialog']//button[contains(@class,'artdeco-button--primary')]",
        "//button[contains(@class,'artdeco-modal__actionbar')]//button[1]"
    ]
    for xpath in send_xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", btn)
            print("Sent successfully!")
            return True
        except:
            continue
    print("Can't find Send button!")
    return False

def send_connection_request(driver):
    wait = WebDriverWait(driver, 15)
    driver.execute_script("window.scrollTo(0, 800);")
    time.sleep(0.6)

    # CASE 1: DIRECT "Connect" BUTTON
    direct_xpaths = [
        "//button[contains(@class,'artdeco-button--primary') and .//span[text()='Connect']]",
        "//button[.//span[text()='Connect'] and contains(@class,'artdeco-button--primary')]",
        "//button[contains(@class,'pv-top-card') and .//span[text()='Connect']]"
    ]

    for xpath in direct_xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(0.6)
            driver.execute_script("arguments[0].click();", btn)
            print("Direct Connect button clicked!")
            time.sleep(1)
            if click_send_without_note(driver, wait):
                random_sleep(4, 8)
                return True
            return False
        except:
            continue

    # CASE 2: "More" button method
    print("Direct Connect Not Found → Trying More button...")

    more_xpaths = [
        "//button[.//span[text()='More']]//parent::button",
        "//button[@aria-label='More actions']",
        "//button[contains(@class,'artdeco-button--secondary') and .//span[text()='More']]",
        "//div[contains(@class,'pvs-header')]//button[.//span[text()='More']]"
    ]

    for xpath in more_xpaths:
        try:
            more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", more_btn)
            print("More button click successfully!")
            time.sleep(1)
            break
        except:
            continue
    else:
        print("More button not found → Already connected or restricted profile")
        return False

    # Dropdown se Connect click
    connect_dropdown_xpaths = [
        "//span[text()='Connect']/ancestor::div[@role='button']",
        "//div[contains(@aria-label,'Invite') and contains(@aria-label,'to connect')]"
    ]

    for xpath in connect_dropdown_xpaths:
        try:
            connect_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", connect_btn)
            print("Connect clicked through dropdown menu!")
            time.sleep(1)
            break
        except:
            continue
    else:
        print("Couldn't find Connect Button in Dropdown menu!")
        return False

    # Final Send
    return click_send_without_note(driver, wait)

# ========================= PROCESS PROFILE =========================
def process_profile(driver, url):
    print(f"\nOpening → {url}")
    driver.get(url)
    random_sleep(4, 8)
    driver.execute_script("window.scrollTo(0, 800);")
    time.sleep(0.6)
    if send_connection_request(driver):
        return "Sent"
    else:
        return "Failed"

# ========================= MAIN =========================
def main():
    print("LinkedIn Auto Connect By Sirat Wali")
    df = pd.read_csv(CSV_FILE)
    url_col = df.columns[0]
    urls = df[url_col].dropna().str.strip().tolist()

    if "status" not in df.columns:
        df["status"] = ""

    driver = get_driver()
    try:
        login_linkedin(driver)
        sent = 0
        for url in urls:
            if sent >= DAILY_LIMIT:
                print(f"Daily limit {DAILY_LIMIT} Reached!")
                break

            if df.loc[df[url_col] == url, "status"].iloc[0] == "Sent":
                print("Already sent → skip")
                continue

            status = process_profile(driver, url)
            df.loc[df[url_col] == url, "status"] = status
            df.to_csv(OUTPUT_FILE, index=False)

            if status == "Sent":
                sent += 1
                print(f"Total Sent Today: {sent}")

        print(f"\nSuccessfully Task Completed! Total {sent} connections sended.")

    except Exception as e:
        print("Error Occurred:", e)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
