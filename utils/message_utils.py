import time
import logging
import random
import json
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from openai import OpenAI

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

def get_message_from_ai(message_param, site_url=None, site_name=None):
    """Génère une réponse avec OpenAI."""
    load_dotenv()
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    OPENAI_URL = os.getenv("OPENAI_URL")
    site_url = site_url or os.getenv("SITE_URL", "<DEFAULT_SITE_URL>")
    site_name = site_name or os.getenv("SITE_NAME", "<DEFAULT_SITE_NAME>")
    prompt = os.getenv("PROMPT", "")
    
    client = OpenAI(
        base_url=OPENAI_URL,
        api_key=OPENAI_KEY,
    )
    
    full_prompt = prompt + " " + message_param
    
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": site_url,
            "X-Title": site_name,
        },
        extra_body={},
        model="cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
        messages=[{
            "role": "user",
            "content": full_prompt
        }]
    )
    
    ai_response = completion.choices[0].message.content
    ai_response_cleaned = re.sub(r"<think>.*?</think>", "", ai_response, flags=re.DOTALL)
    return ai_response_cleaned.strip()

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
        time.sleep(random.uniform(1, 3))
    except Exception as e:
        logging.error("Erreur lors de l'envoi du message à %s : %s", conversation_id, str(e))
        return False
    return True

def get_last_message(driver, wait, conversation_id):
    """Récupère le dernier message visible d'une conversation Messenger."""
    conversation_url = f"https://www.facebook.com/messages/t/{conversation_id}"
    driver.get(conversation_url)
    time.sleep(random.uniform(2, 5))
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='grid']")))
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
            logging.warning(f"Impossible de déterminer l'expéditeur pour {conversation_id} : {str(e)}")
        
        return {"text": text, "sender": sender}
    except Exception as e:
        logging.error("Erreur lors de la récupération du dernier message pour %s : %s", conversation_id, str(e))
        return None

def bot_logic(driver, wait, conversation_id):
    """Gère la logique du bot."""
    global first_run_per_conversation
    last_message = get_last_message(driver, wait, conversation_id)
    welcome_message = os.getenv("WELCOME_MESSAGE")
    
    if first_run_per_conversation.get(conversation_id, True):
        if last_message and last_message["sender"] == "recipient":
            logging.info("Un message existe déjà, le bot répond directement.")
            time.sleep(2)
            response = get_message_from_ai(last_message["text"])
            send_message(driver, wait, conversation_id, response)
        else:
            send_message(driver, wait, conversation_id, welcome_message)
        first_run_per_conversation[conversation_id] = False
        save_state()
    elif last_message and last_message["sender"] == "recipient":
        logging.info("Réponse en cours d'élaboration avec AI...")
        time.sleep(2)
        response = get_message_from_ai(last_message["text"])
        send_message(driver, wait, conversation_id, response)
    else:
        logging.info("Aucune action requise pour %s.", conversation_id)
