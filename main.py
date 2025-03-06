import time
import logging
from utils.request_ai import get_message_from_ai
from utils.auth_utils import login_to_facebook
from utils.message_utils import send_message, get_last_message
from utils.env_utils import load_env_variables
from utils.driver_utils import init_driver
import os

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

    def login(self):
        """Log in to Facebook."""
        login_to_facebook(self.driver, self.wait, self.email, self.password)

    def monitor_conversations(self, conversation_ids):
        """Monitor conversations and respond with AI-generated messages only from recipients."""
        self.last_message_count = {cid: 0 for cid in conversation_ids}
        try:
            while True:
                for cid in conversation_ids:
                    last_message = get_last_message(self.driver, self.wait, cid)

                    if last_message:
                        logging.info("Dernier message dans %s : %s", cid, last_message["text"])

                        if last_message["sender"] == "recipient":
                            ai_response = get_message_from_ai(last_message["text"])
                            send_message(self.driver, self.wait, cid, ai_response)
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
    # Load credentials
    EMAIL, PASSWORD = load_env_variables()
    WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")

    # Liste des conversations à surveiller
    conversation_ids = ["9012249938894046", "103891624739166", "100033562244981"]

    # Initialize and run bot
    bot = FacebookMessengerBot(EMAIL, PASSWORD, CHROME_DRIVER_PATH, CHROME_BINARY_PATH)
    bot.login()

    # Send initial welcome message
    for cid in conversation_ids:
        send_message(bot.driver, bot.wait, cid, WELCOME_MESSAGE)
        time.sleep(3)

    # Start monitoring
    bot.monitor_conversations(conversation_ids)
