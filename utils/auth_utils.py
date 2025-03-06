import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def login_to_facebook(driver, wait, email, password):
    """Log in to Facebook using provided credentials."""
    driver.get("https://www.facebook.com")
    logging.info("Page Facebook chargée : %s", driver.title)
    try:
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        password_field = driver.find_element(By.ID, "pass")
        login_button = driver.find_element(By.NAME, "login")
        
        email_field.send_keys(email)
        password_field.send_keys(password)
        login_button.click()

        logging.info("Si un CAPTCHA apparaît, veuillez le résoudre. Attente de 30 secondes...")
        time.sleep(30)
        logging.info("Connexion effectuée. Titre après connexion : %s", driver.title)
    except Exception as e:
        logging.error("Erreur lors de la connexion : %s", e)