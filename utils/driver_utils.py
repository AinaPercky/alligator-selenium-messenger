from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

def init_driver(driver_path, binary_path, wait_timeout=15):
    """Initialize and return a Selenium WebDriver instance."""
    options = Options()
    options.binary_location = binary_path
    options.add_argument("--start-maximized")
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver, WebDriverWait(driver, wait_timeout)