import requests
from bs4 import BeautifulSoup

# Using headers to pretend we are a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def silent_web_search(query: str) -> str:
    """
    Performs a web search and scrapes the first few results or a featured snippet.
    """
    print(f"🤫 Performing silent web search for: '{query}'")
    try:
        # We'll use DuckDuckGo as it's generally easier to scrape than Google
        search_url = f"https://duckduckgo.com/html/?q={query}"
        
        response = requests.get(search_url, headers=HEADERS, timeout=5)
        response.raise_for_status() # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all result snippets
        results = soup.find_all('a', class_='result__a')
        
        if not results:
            return "Sorry sir, I couldn't find any direct results for that query."

        # Extract text from the top 3 results
        snippet = ""
        for i, result in enumerate(results[:3]):
            snippet += result.get_text(strip=True) + ". "
        
        return snippet.strip()

    except requests.RequestException as e:
        print(f"❌ Web search failed: {e}")
        return "Sorry sir, I'm having trouble connecting to the internet to perform the search."
    except Exception as e:
        print(f"❌ An error occurred during web scraping: {e}")
        return "Sorry sir, I encountered an error while processing the search results."
