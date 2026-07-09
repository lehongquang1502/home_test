import os
import time
import json
import glob
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
STORE_DISPLAY_NAME = "OptiSigns-FileSearch"
LOG_FILE = "log.json"

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None

def get_or_create_store(display_name: str):
    for store in client.file_search_stores.list():
        if store.display_name == display_name:
            return store
        
    return client.file_search_stores.create(
        config={
            "display_name": display_name,
            'embedding_model': 'models/gemini-embedding-2'
        }
    )

def get_existing_documents(store):
    docs_metadata = {}
    try:
        for doc in client.file_search_stores.documents.list(parent=store.name):
            if doc.display_name:
                edited_at = ""
                if doc.custom_metadata:
                    for meta in doc.custom_metadata:
                        if meta.key == "source_edited_at":
                            edited_at = meta.string_value
                docs_metadata[doc.display_name] = {
                    "name": doc.name,
                    "edited_at": edited_at
                }
    except Exception as e:
        print(f"Could not fetch existing document list: {e}")
    return docs_metadata

def upload_delta(scraped_data, store_display_name=STORE_DISPLAY_NAME):
    if not client:
        print("GEMINI_API_KEY or API_KEY not found.")
        return
        
    store = get_or_create_store(store_display_name)
    existing_docs = get_existing_documents(store)
    
    counts = {"added": 0, "updated": 0, "skipped": 0, "failed": 0}
    
    for index, item in enumerate(scraped_data, start=1):
        file_path = item["file_path"]
        incoming_edited_at = item["edited_at"]
        file_name = os.path.basename(file_path)
        
        status = "unknown"
        if file_name in existing_docs:
            existing = existing_docs[file_name]
            if existing["edited_at"] == incoming_edited_at and incoming_edited_at:
                print(f"[{index}/{len(scraped_data)}] Skipping (unchanged): {file_name}")
                counts["skipped"] += 1
                continue
            else:
                print(f"[{index}/{len(scraped_data)}] Updating (delta detected): {file_name}")
                try:
                    client.file_search_stores.documents.delete(name=existing["name"], config={"force": True})
                    status = "updated"
                except Exception as e:
                    print(f"  -> Error deleting old document {file_name}: {e}")
        else:
            print(f"[{index}/{len(scraped_data)}] Adding (new): {file_name}")
            status = "added"
            
        try:
            custom_meta = None
            if incoming_edited_at:
                custom_meta = [{"key": "source_edited_at", "string_value": incoming_edited_at}]
                
            operation = client.file_search_stores.upload_to_file_search_store(
                file=file_path,
                file_search_store_name=store.name,
                config={
                    "display_name": file_name,
                    "mime_type": "text/markdown",
                    "custom_metadata": custom_meta,
                    "chunking_config": {
                        'white_space_config': {
                            'max_tokens_per_chunk': 500,
                            'max_overlap_tokens': 50
                        }
                    }
                }
            )
            
            while not operation.done:
                time.sleep(3)
                operation = client.operations.get(operation)
                
            counts[status] += 1
        except Exception as e:
            print(f"  -> [x] Error uploading {file_name}: {e}")
            counts["failed"] += 1
            
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(counts, f, indent=2)
        
    print("\n" + "=" * 60)
    print("UPLOAD SUMMARY")
    print("=" * 60)
    for k, v in counts.items():
        print(f"{k.capitalize()}: {v}")
    print("=" * 60)
    
    return counts

if __name__ == "__main__":
    md_files = glob.glob("scrape_result/*.md")
    dummy_data = [{"file_path": p, "edited_at": ""} for p in md_files]
    if dummy_data:
        upload_delta(dummy_data)
    else:
        print("No scraped files found.")