import os
import sys
from scraper import fetch_and_save_articles
from uploader import upload_delta

def main():
    print("=" * 60)
    print("STARTING PIPELINE: Scrape Zendesk -> Upload to Gemini")
    print("=" * 60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY or API_KEY is not set. Please set it in your environment.")
        sys.exit(1)
        
    print("\n--- PHASE 1: Scrape Articles ---")
    scraped_data = fetch_and_save_articles()
    
    if not scraped_data:
        print("No articles fetched. Exiting.")
        return
        
    print(f"Total articles scraped: {len(scraped_data)}")
    
    print("\n--- PHASE 2: Delta Upload ---")
    counts = upload_delta(scraped_data)
    
    print("\nPIPELINE COMPLETED SUCCESSFULLY!")
    
if __name__ == "__main__":
    main()
