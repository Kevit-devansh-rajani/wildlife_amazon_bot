# Wildlife Amazon Bot

<img width="1825" height="816" alt="image" src="https://github.com/user-attachments/assets/f68b902f-05e8-4f18-baaf-19ac9e553f47" />


This project is a chatbot that can answer questions about the Amazon rainforest. It uses a web scraper to gather information from the World Wildlife Fund website and then uses the OpenAI Assistants API to power the chatbot.

## Workflow

The project follows this workflow:

1.  **Scrape Data:** A Python script using Selenium scrapes data from the [World Wildlife Fund's Amazon page](https://www.worldwildlife.org/places/amazon).
2.  **Store Data:** The scraped data is stored locally.
3.  **Process Data:** The data is converted into a JSON format that can be used by the OpenAI Assistants API.
4.  **Chatbot:** A Streamlit application provides a user interface for interacting with the chatbot. The OpenAI Assistants API with the Retrieval tool is used to answer user questions based on the scraped data.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/wildlife_amazon_bot.git
    cd wildlife_amazon_bot
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up ChromeDriver:**
    This project uses Selenium with Chrome, so you need to have ChromeDriver installed and configured. The path to the ChromeDriver executable is hardcoded in `amazon_scrapper.py`. You will need to update this path to match your system.

    ```python
    PATH = "/path/to/your/chromedriver"
    service = Service(PATH)
    driver = webdriver.Chrome(service=service)
    ```

## Usage

1.  **Run the scraper:**
    ```bash
    python amazon_scrapper.py
    ```
    This will scrape the data from the website and save it locally.

2.  **Run the Streamlit chatbot:**
    ```bash
    streamlit run streamlit_UI.py 
    ```
    This will start the Streamlit application, and you can open it in your browser to start asking questions.

## Requirements

The project's dependencies are listed in the `requirements.txt` file.

```
# --- Web Scraping ---
selenium
beautifulsoup4
lxml
html2text
requests
tqdm

# --- Data Handling & Utilities ---
pandas
numpy

# --- OpenAI Assistant + Retrieval ---
openai
tiktoken

# --- Optional: Local Vector Storage (if not using OpenAI's retrieval) ---
chromadb
faiss-cpu

# --- Browser Automation Drivers (for Selenium) ---
webdriver-manager

streamlit
```
