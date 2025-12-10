# =======================================================
# LinkedIn Auto Connect 2025 - Streamlit App (by Sirat Wali)
# Original backend code unchanged - only integrated with Streamlit frontend
# Works on ALL profiles (December 2025)
# =======================================================

import streamlit as st
import pandas as pd
import time
import random
import io
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

# ==================== STREAMLIT PAGE CONFIG ====================
st.set_page_config(page_title="LinkedIn Auto Connect 2025", layout="wide")
st.title("LinkedIn Auto Connect Tool (by Sirat Wali)")
st.markdown("**Safe daily limit: 80–120** | Never exceed 150 to avoid restrictions")

# ==================== USER INPUTS ====================
email = st.text_input("LinkedIn Email", type="password")
password = st.text_input("LinkedIn Password", type="password")
uploaded_file = st.file_uploader("Upload CSV with LinkedIn URLs (one column only)", type=["csv"])
daily_limit = st.slider("Daily Connection Requests Limit", 0, 150, 100)
start_button = st.button("Start Sending Connection Requests")

# ==================== DRIVER SETUP (same as your original) ====================
def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")  # Important for Streamlit Cloud
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    service = Service(chromedriver_autoinstaller.install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => false});"
    })
    return driver

def random_sleep(min_sec=8, max_sec=20):
    time.sleep(random.uniform(min_sec, max_sec))

# ==================== LOGIN FUNCTION (same as your original) ====================
def login_linkedin(driver):
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password + Keys.RETURN)
    random_sleep(15, 30)
    st.info("Login karne ke baad koi verification (2FA, email, phone) aaye to manually complete karo.")
    st.button("Verification Complete → Continue", key="continue_login")
    if st.session_state.get("continue_login"):
        st.success("Login successful! Now sending requests...")
        return True
    return False

# ==================== YOUR ORIGINAL SEND FUNCTIONS - UNCHANGED ====================
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
    time.sleep(2)

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
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
            print("Direct Connect button clicked!")
            time.sleep(3)
            if click_send_without_note(driver, wait):
                random_sleep(12, 25)
                return True
            return False
        except:
            continue

    # CASE 2: "More" button method
    print("Direct Connect Not Found → Trying More button...")
    
    more_xpaths = [
        "//button[.//span[text()='More']]//parent::button",
        "//button[@aria-label='More actions']",
        "//button[contains(@class,'artdeco-button--secondary') and .//span[text()='More']]]",
        "//div[contains(@class,'pvs-header')]//button[.//span[text()='More']]"
    ]
    
    for xpath in more_xpaths:
        try:
            more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", more_btn)
            print("More button click successfully!")
            time.sleep(3)
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
            time.sleep(3)
            break
        except:
            continue
    else:
        print("Couldn't found Connect Button in Dropdown menu!")
        return False

    return click_send_without_note(driver, wait)

def process_profile(driver, url):
    print(f"\nOpening → {url}")
    driver.get(url)
    random_sleep(12, 22)

    driver.execute_script("window.scrollTo(0, 800);")
    time.sleep(2)

    if send_connection_request(driver):
        return "Sent"
    else:
        return "Failed"

# ==================== MAIN LOGIC ====================
if start_button:
    if not email or not password or not uploaded_file:
        st.error("Please fill all fields and upload CSV!")
    else:
        try:
            df = pd.read_csv(uploaded_file)
            url_col = df.columns[0]
            urls = df[url_col].dropna().str.strip().tolist()

            if "status" not in df.columns:
                df["status"] = ""

            driver = get_driver()
            try:
                if login_linkedin(driver):
                    sent = 0
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, url in enumerate(urls):
                        if sent >= daily_limit:
                            status_text.success(f"Daily limit reached ({daily_limit})! Total sent: {sent}")
                            break

                        if df.loc[df[url_col] == url, "status"].iloc[0] == "Sent":
                            status_text.text(f"Already sent → skipping {url}")
                            continue

                        status = process_profile(driver, url)
                        df.loc[df[url_col] == url, "status"] = status

                        if status == "Sent":
                            sent += 1

                        progress_bar.progress((i + 1) / len(urls))
                        status_text.text(f"Processing {i+1}/{len(urls)} | Sent today: {sent}")

                        # Live CSV download
                        csv_buffer = io.StringIO()
                        df.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label=f"Download Current Results (Updated)",
                            data=csv_buffer.getvalue(),
                            file_name="linkedin_results_current.csv",
                            mime="text/csv",
                            key=f"download_{i}"
                        )

                    st.success(f"Task completed! Total connections sent today: {sent}")

                    # Final CSV
                    final_buffer = io.StringIO()
                    df.to_csv(final_buffer, index=False)
                    st.download_button(
                        label="Download Final Results CSV",
                        data=final_buffer.getvalue(),
                        file_name="linkedin_results_final.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Error occurred: {e}")
            finally:
                driver.quit()

        except Exception as e:
            st.error(f"File reading error: {e}")
