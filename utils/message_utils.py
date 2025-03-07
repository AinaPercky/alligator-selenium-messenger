import time
import logging
import random
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def open_conversation(driver, wait, conversation_id):
    """Ouvre une conversation et clique sur le bouton 'Continuer' si nécessaire (pour le chiffrement de bout en bout)."""
    conversation_url = f"https://www.facebook.com/messages/t/{conversation_id}"
    driver.get(conversation_url)
    logging.info("Ouverture de la conversation %s", conversation_id)
    
    # Vérifier la présence du bouton "Continuer" lié au chiffrement de bout en bout
    try:
        continue_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continuer')]"))
        )
        continue_button.click()
        logging.info("Bouton 'Continuer' cliqué pour accéder à la conversation.")
        time.sleep(random.uniform(1, 2))  # Petit délai après le clic
    except Exception as e:
        logging.info("Pas de bouton 'Continuer' détecté, conversation accessible.")

def send_message(driver, wait, conversation_id, message):
    """Envoie un message à une conversation Messenger."""
    open_conversation(driver, wait, conversation_id)
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

def get_last_message(driver, wait, conversation_id, max_wait=30):
    """
    Récupère le dernier message visible d'une conversation Messenger en s'assurant que le chargement est terminé.
    
    max_wait: temps maximum en secondes pour attendre que la conversation soit entièrement chargée.
    """
    open_conversation(driver, wait, conversation_id)
    # Augmenter le délai initial pour les connexions lentes
    time.sleep(random.uniform(3, 6))
    
    try:
        # Attendre la présence de la grille de messages
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='grid']")))
        
        last_message_elem = None
        start_time = time.time()
        # Boucle de tentative pendant max_wait secondes pour récupérer un message non vide et chargé
        while time.time() - start_time < max_wait:
            messages = driver.find_elements(By.XPATH, "//div[@role='grid']//div[@dir='auto']")
            if messages:
                last_message_elem = messages[-1]
                text = last_message_elem.text.strip()
                # Vérifier que le texte est bien chargé et ne ressemble pas à un indicateur de chargement
                if text and "loading" not in text.lower() and "chargement" not in text.lower():
                    break
            time.sleep(1)
        else:
            logging.error("Aucun message valide trouvé après %s secondes pour %s.", max_wait, conversation_id)
            return None
        
        text = last_message_elem.text.strip()
        sender = "unknown"
        
        try:
            classes = last_message_elem.get_attribute("class").split()
            if "x18lvrbx" in classes:
                sender = "recipient"
            elif "xyk4ms5" in classes:
                sender = "bot"
        except Exception as e:
            logging.warning("Impossible de déterminer l'expéditeur pour un message dans %s : %s", conversation_id, str(e))
        
        return {"text": text, "sender": sender}
    except Exception as e:
        logging.error("Erreur lors de la récupération du dernier message pour %s : %s", conversation_id, str(e))
        return None
def reverse_message(text):
    """Inverse un message : inverse les lettres si un seul mot, sinon inverse l'ordre des mots."""
    words = text.split()
    return text[::-1] if len(words) == 1 else " ".join(words[::-1])