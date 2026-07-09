# Delta Knowledge Pipeline (Zendesk to Gemini AI)

This repository contains a stateless, automated pipeline that scrapes Help Center articles from Zendesk and synchronizes them to a Google Gemini File Search Store (Vector Database). It is designed to run as a daily scheduled job (e.g., via DigitalOcean App Platform or a Cron job).

## 🚀 Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lehongquang1502/home_test.git
   cd home_test
   ```

2. **Environment Variables:**
   Rename `.env.sample` to `.env` and insert your Gemini API Key:
   ```bash
   GEMINI_API_KEY="your_actual_api_key_here"
   ```

## 💻 How to Run Locally

### Option 1: Using Python (with `uv`)
Ensure you have Python 3.11+ installed. We recommend using `uv` for lightning-fast dependency management.
```bash
# Install dependencies
uv pip install --system requests markdownify python-dotenv google-genai

# Run the pipeline
uv run main.py
```

### Option 2: Using Docker (Stateless Mode)
To simulate the cloud deployment environment locally, you can use Docker. Notice that `.env` is deliberately ignored in the build process for security, so we inject the variables at runtime.

```bash
# 1. Build the Docker image
docker build -t scraper-app .

# 2. Run the container and inject the API key
docker run -e API_KEY="your_actual_api_key_here" scraper-app
```
*(The container will execute the pipeline once, print the upload summary, and gracefully exit with code 0).*

## 🧩 Chunking Strategy

During the upload phase to Gemini's Vector Database, the system delegates chunking to Google's highly optimized server-side engine using a `white_space_config`:
- **`max_tokens_per_chunk`: 500**
- **`max_overlap_tokens`: 50**

**Rationale:** Help Center articles are highly structured (steps, bullet points). A 500-token limit is large enough to capture an entire troubleshooting step or feature explanation in a single context window, preventing fragmented answers. The 50-token overlap ensures that if a sentence or instruction list crosses a chunk boundary, the LLM retains enough surrounding context to connect the thoughts seamlessly.

## 📊 Daily Job Logs

*Note: The application is deployed as a Scheduled Job on DigitalOcean. View the live execution logs here:*
[Link to DigitalOcean Daily Job Logs] *(Please replace this with your actual DigitalOcean App Platform log URL)*

## 🤖 Assistant Demonstration

Here is a screenshot of OptiBot successfully utilizing the uploaded Vector Store to answer the sample question: *"How do I add a YouTube video?"*

*(Please take a screenshot of your Playground/ask.py testing and save it as `screenshot.png` in this folder, then push it to GitHub).*
![Assistant Answering Sample Question](screenshot.png)
