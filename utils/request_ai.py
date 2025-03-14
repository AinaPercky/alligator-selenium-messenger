
from dotenv import load_dotenv
from openai import OpenAI
import os
import re

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
