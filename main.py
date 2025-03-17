import time
import logging
import os
import random
import asyncio
from utils.request_ai import get_message_from_ai
from utils.auth_utils import login_to_facebook
from utils.message_utils import send_message, get_last_message
from utils.env_utils import load_env_variables
from utils.driver_utils import init_driver
from utils.translate import translate_text
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chemins constants
CHROME_DRIVER_PATH = "C:/Users/ACER/Documents/code/Init_selenium/chromedriver.exe"
CHROME_BINARY_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"

class FacebookMessengerBot:
    def __init__(self, email, password, driver_path, binary_path):
        self.email = email
        self.password = password
        self.driver, self.wait = init_driver(driver_path, binary_path)
        self.last_message_count = {}

    def human_pause(self, min_time=2, max_time=5):
        """Pause aléatoire pour simuler un comportement humain."""
        time.sleep(random.uniform(min_time, max_time))

    def random_mouse_move(self):
        window_size = self.driver.get_window_rect()
        window_width = window_size['width']
        window_height = window_size['height']
        x_offset = random.randint(0, window_width - 10)
        y_offset = random.randint(0, window_height - 10)
        action = ActionChains(self.driver)
        action.move_by_offset(x_offset, y_offset).perform()

    def login(self):
        """Connexion à Facebook avec simulation humaine."""
        login_to_facebook(self.driver, self.wait, self.email, self.password)
        logging.info("Authentification initiale réussie.")
        self.human_pause(5, 10)
        self.driver.get("https://www.facebook.com/messages")
        logging.info("Accès aux messages pour déclencher la 2FA.")
        self.human_pause(5, 8)
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        self.human_pause(3, 5)
        input("Après avoir complété la 2FA dans le navigateur, appuyez sur Entrée pour continuer...")

    async def monitor_conversations(self, conversation_ids):
        """Surveille les conversations et répond avec l'IA uniquement aux messages reçus."""
        self.last_message_count = {cid: 0 for cid in conversation_ids}
        try:
            while True:
                for cid in conversation_ids:
                    last_message = get_last_message(self.driver, self.wait, cid)
                    if last_message:
                        logging.info("Dernier message dans %s : %s", cid, last_message["text"])
                        if last_message["sender"] == "recipient":
                            last_message_translated = await translate_text(last_message["text"], 'fr')
                            replied_msg = get_message_from_ai(last_message_translated)
                            if replied_msg:
                                replied_msg_translated = await translate_text(replied_msg, 'mg')
                            send_message(self.driver, self.wait, cid, replied_msg_translated)
                        else:
                            logging.info("Le dernier message est du bot, pas d'action nécessaire.")
                    else:
                        logging.info("Aucun message trouvé pour %s.", cid)
                    time.sleep(2)
                logging.info("Cycle terminé, nouvelle vérification dans 5 secondes...")
                time.sleep(5)
        except KeyboardInterrupt:
            logging.info("Arrêt du monitoring par l'utilisateur.")
            self.driver.quit()

if __name__ == '__main__':
    EMAIL, PASSWORD = load_env_variables()
    conversation_ids = ["9561410110603343"]

    bot = FacebookMessengerBot(EMAIL, PASSWORD, CHROME_DRIVER_PATH, CHROME_BINARY_PATH)
    bot.login()

    for cid in conversation_ids:
        # Générer un message de bienvenue dynamique en malgache
        welcome_message = get_message_from_ai("", is_welcome_message=True)
        welcome_message_translated = asyncio.run(translate_text(welcome_message, 'mg'
        ''))
        send_message(bot.driver, bot.wait, cid, welcome_message_translated)
        time.sleep(3)

    # Exécution asynchrone du bot
    asyncio.run(bot.monitor_conversations(conversation_ids))