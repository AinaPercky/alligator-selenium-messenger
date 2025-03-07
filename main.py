import time
import logging
from utils.request_ai import get_message_from_ai
from utils.auth_utils import login_to_facebook
from utils.message_utils import send_message, get_last_message, reverse_message
from utils.env_utils import load_env_variables
from utils.driver_utils import init_driver 

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chemins constants
CHROME_DRIVER_PATH = "/home/percky/Documents/code/alligator-selenium-messenger/chromedriver"
CHROME_BINARY_PATH = "/usr/bin/google-chrome"

class FacebookMessengerBot:
    def __init__(self, email, password, driver_path, binary_path):
        self.email = email
        self.password = password
        self.driver, self.wait = init_driver(driver_path, binary_path)
        self.last_message_count = {}

    def login(self):
        """Connexion à Facebook, accès à la page des messages pour déclencher la 2FA, puis pause pour compléter la 2FA."""
        login_to_facebook(self.driver, self.wait, self.email, self.password)
        logging.info("Authentification initiale réussie.")
        
        # Accéder aux messages pour déclencher l'authentification à double facteur
        self.driver.get("https://www.facebook.com/messages")
        logging.info("Accès aux messages pour déclencher l'authentification à double facteur.")
        
        # Pause manuelle pour permettre à l'utilisateur de compléter la 2FA (environ 1 à 2 minutes)
        input("Après avoir complété la 2FA dans le navigateur, appuyez sur Entrée pour continuer...")

    def monitor_conversations(self, conversation_ids):
        """Surveille les conversations et répond en renversant le message uniquement pour les messages reçus."""
        self.last_message_count = {cid: 0 for cid in conversation_ids}
        try:
            while True:
                for cid in conversation_ids:
                    last_message = get_last_message(self.driver, self.wait, cid)
                    
                    if last_message:
                        logging.info("Dernier message dans %s : %s", cid, last_message["text"])
                        
                        if last_message["sender"] == "recipient":
                            reversed_msg = reverse_message(last_message["text"])
                            # Vous pouvez intégrer ici la réponse générée par l'IA si nécessaire :
                            # replied_msg = get_message_from_ai(last_message["text"])
                            send_message(self.driver, self.wait, cid, reversed_msg)
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
    # Chargement des identifiants
    EMAIL, PASSWORD = load_env_variables()

    # Liste des conversations à surveiller
    conversation_ids = ["9022970501162249", "25520837117532030", "10099134706781390"]

    # Initialisation et démarrage du bot
    bot = FacebookMessengerBot(EMAIL, PASSWORD, CHROME_DRIVER_PATH, CHROME_BINARY_PATH)
    bot.login()

    # Envoi d'un message initial "Salut" dans chaque conversation
    for cid in conversation_ids:
        send_message(bot.driver, bot.wait, cid, "Salut")
        time.sleep(3)

    # Démarrage de la surveillance des conversations
    bot.monitor_conversations(conversation_ids)
