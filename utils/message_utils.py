import time
import logging
import random
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Chemin du fichier pour persister l'état
STATE_FILE = "conversation_state.json"

# Charger l'état depuis le fichier s'il existe, sinon initialiser un dictionnaire vide
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        first_run_per_conversation = json.load(f)
else:
    first_run_per_conversation = {}

def save_state():
    """Sauvegarde l'état dans le fichier JSON."""
    with open(STATE_FILE, "w") as f:
        json.dump(first_run_per_conversation, f)

def send_message(driver, wait, conversation_id, message):
    """Envoie un message à une conversation Messenger."""
    conversation_url = f"https://www.facebook.com/messages/t/{conversation_id}"
    driver.get(conversation_url)
    logging.info("Ouverture de la conversation %s", conversation_id)
    try:
        message_box = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox']"))
        )
        message_box.click()
        message_box.send_keys(message)
        message_box.send_keys(Keys.RETURN)
        logging.info("Message '%s' envoyé à %s", message, conversation_id)
        time.sleep(random.uniform(1, 3))  # Délai aléatoire pour imiter un humain
    except Exception as e:
        logging.error("Erreur lors de l'envoi du message à %s : %s", conversation_id, str(e))
        return False
    return True

def get_last_message(driver, wait, conversation_id):
    """Récupère le dernier message visible d'une conversation Messenger."""
    conversation_url = f"https://www.facebook.com/messages/t/{conversation_id}"
    driver.get(conversation_url)
    time.sleep(random.uniform(2, 5))  # Délai pour permettre le chargement
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='grid']")))

        # Récupérer le dernier message visible
        last_message_elem = driver.find_elements(By.XPATH, "//div[@role='grid']//div[@dir='auto']")[-1]
        text = last_message_elem.text.strip()
        sender = "unknown"

        try:
            classes = last_message_elem.get_attribute("class").split()
            if "x18lvrbx" in classes:
                sender = "recipient"
            elif "xyk4ms5" in classes:
                sender = "bot"
        except Exception as e:
            logging.warning(f"Impossible de déterminer l'expéditeur pour un message dans {conversation_id} : {str(e)}")

        return {"text": text, "sender": sender}
    except Exception as e:
        logging.error("Erreur lors de la récupération du dernier message pour %s : %s", conversation_id, str(e))
        return None

def reverse_message(text):
    """Inverse un message : inverse les lettres si un seul mot, sinon inverse l'ordre des mots."""
    words = text.split()
    return text[::-1] if len(words) == 1 else " ".join(words[::-1])

def bot_logic(driver, wait, conversation_id):
    """Gère la logique du bot."""
    global first_run_per_conversation

    if first_run_per_conversation.get(conversation_id, True):
        send_message(driver, wait, conversation_id, "Salut !")
        first_run_per_conversation[conversation_id] = False
        save_state()
    else:
        last_message = get_last_message(driver, wait, conversation_id)
        if last_message and last_message["sender"] == "recipient":
            response = reverse_message(last_message["text"])
            send_message(driver, wait, conversation_id, response)
        else:
            logging.info("Aucune action requise pour %s.", conversation_id)
