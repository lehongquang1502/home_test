import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

input = str(input())

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
STORE_DISPLAY_NAME = "OptiSigns-FileSearch"

store = next((s for s in client.file_search_stores.list() if s.display_name == STORE_DISPLAY_NAME), None)

if store:
    print("Thinking...\n" + "-"*40)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=input,
        config={
            
            'tools': [{'file_search': {'file_search_store_names': [store.name]}}],
            'system_instruction': (
                "You are OptiBot, the customer-support bot for OptiSigns.com.\n"
                "• Tone: helpful, factual, concise.\n"
                "• Only answer using the uploaded docs.\n"
                "• Max 5 bullet points; else link to the doc.\n"
                "• Cite up to 3 \"Article URL:\" lines per reply.\n"
            )
        }
    )
    print(response.text)
else:
    print("Cannot find Store!")