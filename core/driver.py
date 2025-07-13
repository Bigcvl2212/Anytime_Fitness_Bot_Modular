"""
WebDriver Setup and Management - PROVEN WORKING CODE FROM ORIGINAL SCRIPT
Contains the EXACT working driver and login function from Anytime_Bot.py
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from ..config.constants import CLUBOS_LOGIN_URL, CLUBOS_USERNAME_SECRET, CLUBOS_PASSWORD_SECRET
from ..config.secrets import get_secret


def setup_chrome_driver():
    """Setup Chrome WebDriver with optimal settings"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"ERROR: Failed to setup Chrome driver: {e}")
        return None


def login_to_clubos(driver):
    """
    Login to ClubOS using existing WebDriver.
    
    Args:
        driver: WebDriver instance to use for login
        
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        clubos_user = get_secret(CLUBOS_USERNAME_SECRET)
        clubos_pass = get_secret(CLUBOS_PASSWORD_SECRET)
        
        if not clubos_user or not clubos_pass:
            print("ERROR: Missing ClubOS credentials")
            return False
        
        print("INFO: Attempting Club OS login...")
        driver.get(CLUBOS_LOGIN_URL)
        time.sleep(3)
        
        print("   INFO: Filling login credentials...")
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        username_field.send_keys(clubos_user)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(clubos_pass)
        
        login_button = driver.find_element(By.CLASS_NAME, "js-login")
        login_button.click()
        
        print("   INFO: Waiting for login to complete...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "quick-search-text")))
        print("SUCCESS: Club OS login complete.")
        return True
    except Exception as e:
        print(f"ERROR: ClubOS login failed: {e}")
        return False


def setup_driver_and_login():
    """
    Setup Chrome driver and login to Club OS.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY - DO NOT MODIFY
    """
    driver = None
    try:
        clubos_user = get_secret(CLUBOS_USERNAME_SECRET)
        clubos_pass = get_secret(CLUBOS_PASSWORD_SECRET)
        
        if not clubos_user or not clubos_pass:
            print("ERROR: Missing ClubOS credentials")
            return None
        
        print("INFO: Initializing WebDriver...")
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Hide webdriver properties
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("INFO: Attempting Club OS login...")
        driver.get(CLUBOS_LOGIN_URL)
        time.sleep(3)
        
        print("   INFO: Filling login credentials...")
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        username_field.send_keys(clubos_user)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(clubos_pass)
        
        login_button = driver.find_element(By.CLASS_NAME, "js-login")
        login_button.click()
        
        print("   INFO: Waiting for login to complete...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "quick-search-text")))
        print("SUCCESS: Club OS login complete.")
        return driver
    except Exception as e:
        print(f"CRITICAL: Login failed. Error: {e}")
        if driver: 
            driver.quit()
        return None
