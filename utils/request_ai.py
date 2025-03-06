
from dotenv import load_dotenv
from openai import OpenAI
import os

def get_message_from_ai(message_param):
    load_dotenv()
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    OPENAI_URL=os.getenv("OPENAI_URL")
    client = OpenAI(
        base_url=OPENAI_URL,
        api_key=OPENAI_KEY,
    )
    completion = client.chat.completions.create(
        extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
        },
        extra_body={},
        model="cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
        messages=[
        {
            "role": "user",
            "content": message_param
        }
        ] 
    )
    return(completion.choices[0].message.content)
