from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from rich import print
from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
load_dotenv()


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    results = tavily.search(query=query, max_results=5)

    out = []

    for r in results['results']:
        out.append(
            f"Tittle: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )

    return "\n----\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page(
                user_agent="Mozilla/5.0"
            )

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # get the fully loaded html
            html = page.content()

            browser.close()
        # parse html using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        # extract clean text
        text = soup.get_text(separator=" ", strip=True)
        return text[:3000]
    
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

print(scrape_url.invoke("https://apnews.com/hub/war-and-unrest"))