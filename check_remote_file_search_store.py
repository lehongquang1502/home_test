from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

TARGET_STORE_NAME = "OptiSigns-FileSearch"


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is missing in the environment.")
        return

    client = genai.Client(api_key=api_key)
    stores = list(client.file_search_stores.list())

    if not stores:
        print("No file search stores found.")
        return

    stores = sorted(stores, key=lambda store: store.create_time or 0, reverse=True)

    print(f"File search stores found: {len(stores)}")
    for index, store in enumerate(stores, start=1):
        print("-" * 60)
        print(f"#{index} (newest first)")
        print(f"create_time: {store.create_time}")
        print(f"name: {store.name}")
        print(f"display_name: {store.display_name}")
        print(f"embedding_model: {store.embedding_model}")
        print(f"active_documents_count: {store.active_documents_count}")
        print(f"pending_documents_count: {store.pending_documents_count}")
        print(f"failed_documents_count: {store.failed_documents_count}")
        print(f"size_bytes: {store.size_bytes}")

    matched = [store for store in stores if store.display_name == TARGET_STORE_NAME]
    print("-" * 60)
    if matched:
        store = matched[0]
        print(f"Target store '{TARGET_STORE_NAME}' found: {store.name}")
        print("Listing uploaded documents:")
        docs = list(client.file_search_stores.documents.list(parent=store.name))
        if not docs:
            print("  -> No documents found in this store yet.")
        else:
            for d in docs[:10]:
                print(f"  - {d.display_name} (Chunks: {getattr(d, 'chunk_count', 'unknown')})")
            if len(docs) > 10:
                print(f"  ... and {len(docs) - 10} more.")
    else:
        print(f"Target store '{TARGET_STORE_NAME}' not found.")


if __name__ == "__main__":
    main()
