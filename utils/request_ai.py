from dotenv import load_dotenv
from openai import OpenAI
import os
import re  # Import pour utiliser les expressions régulières

def get_message_from_ai(message_param, site_url=None, site_name=None):
    # Charge les variables d'environnement depuis le fichier .env
    load_dotenv()
    
    # Récupère la clé API et l'URL de base depuis les variables d'environnement
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    OPENAI_URL = os.getenv("OPENAI_URL")
    
    # Si l'URL et le nom du site ne sont pas passés, utilise des valeurs par défaut
    site_url = site_url or os.getenv("SITE_URL", "<DEFAULT_SITE_URL>")
    site_name = site_name or os.getenv("SITE_NAME", "<DEFAULT_SITE_NAME>")
    
    # Récupère le prompt depuis la variable d'environnement
    prompt = os.getenv("PROMPT")
    
    # Crée un client OpenAI
    client = OpenAI(
        base_url=OPENAI_URL,
        api_key=OPENAI_KEY,
    )
    
    # Combine le prompt et le message de l'utilisateur
    full_prompt = prompt + " " + message_param
    
    # Effectue la demande à l'API OpenAI avec le prompt
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": site_url,  # URL du site pour les classements
            "X-Title": site_name,  # Nom du site pour les classements
        },
        extra_body={},
        model="cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
        messages=[{
            "role": "user",
            "content": full_prompt  # Le message de l'utilisateur avec le prompt intégré
        }]
    )
    
    # Récupère la réponse générée par l'IA
    ai_response = completion.choices[0].message.content
    
    # Supprime les balises <think> et leur contenu à l'aide d'une expression régulière
    ai_response_cleaned = re.sub(r"<think>.*?</think>", "", ai_response, flags=re.DOTALL)
    
    # Retourne la réponse propre
    return ai_response_cleaned.strip()

