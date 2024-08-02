import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Load environment variables
load_dotenv()

# Set OpenAI and SERP API keys
openai_api_key = os.getenv('OPENAI_API_KEY')
serp_api_key = os.getenv('SERP_API_KEY')

# Initialize the OpenAI client with API key
client = OpenAI(api_key=openai_api_key)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define scraping function to extract content for a given URL
def scrape_targeted_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else ''
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_description['content'] if meta_description else ''
        body_text = ' '.join(p.get_text() for p in soup.find_all('p'))
        
        return {
            "title": title,
            "meta_description": meta_description,
            "body_text": body_text
        }
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return {}

# Define Search function using SERP API
def search_company(company_name):
    search_url = "https://serpapi.com/search"
    query = f"{company_name} company overview OR about OR wiki OR products and services"

    params = {
        "engine": "google",
        "q": query,
        "api_key": serp_api_key
    }
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        search_results = response.json()
        results = []
        for result in search_results.get('organic_results', [])[:4]:
            results.append({
                'url': result.get('link'),
                'text': result.get('snippet', '')
            })
        return results
    else:
        logging.error(f"Request failed with status code: {response.status_code}")
        return None

# Define Search function for latest news using SERP API
def search_latest_news(company_name):
    search_url = "https://serpapi.com/search"
    query = f"{company_name} latest news"

    params = {
        "engine": "google",
        "q": query,
        "tbm": "nws",
        "api_key": serp_api_key
    }
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        search_results = response.json()
        news_results = []
        for result in search_results.get('news_results', [])[:5]:
            news_results.append({
                'url': result.get('link'),
                'title': result.get('title'),
                'snippet': result.get('snippet')
            })
        return news_results
    else:
        logging.error(f"Request failed with status code: {response.status_code}")
        return None

# Define a function to summarize search results' content extracted from scraping using Open AI
def summarize_search_results(search_results):
    all_texts = []
    progress_bar = st.progress(0)
    total_results = len(search_results)
    
    for i, result in enumerate(search_results):
        content = scrape_targeted_content(result['url'])
        text = content.get("body_text", "")
        if text:
            all_texts.append(text)
        time.sleep(1)
        progress_bar.progress((i + 1) / total_results)
    
    combined_text = ' '.join(all_texts)
    max_length = 1000
    if len(combined_text) > max_length:
        combined_text = combined_text[:max_length]
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text to give an overview about the given company: {combined_text}"}
        ],
        model="gpt-4",
        max_tokens=300,
        temperature=0.7
    )
    
    summary = response.choices[0].message.content
    return summary

# Define the Streamlit UI
def main():
    st.title("AI Company Research Agent")
    company_name = st.text_input("Enter Company Name")
    
    if st.button("Search"):
        if company_name:
            status_text = st.empty()
            progress_text = st.empty()

            status_text.text(f"Searching information for {company_name}...")
            with st.spinner('Fetching search results...'):
                search_results = search_company(company_name)
            
            if search_results:
                for result in search_results:
                    content = scrape_targeted_content(result['url'])

                with st.spinner('Summarizing search results...'):
                    summary = summarize_search_results(search_results)
                
                status_text.empty()
                progress_text.empty()
                
                results_output = "\n\n".join([f"URL: {result['url']}\nText: {result['text']}" for result in search_results])
                st.write(f"Summary for {company_name}:")
                st.write(summary)
                #st.write("URLs identified:")
                #st.write(results_output)
                
                # Fetch and display latest news
                status_text.text(f"Fetching latest news for {company_name}...")
                with st.spinner('Fetching latest news...'):
                    news_results = search_latest_news(company_name)
                
                if news_results:
                    st.write(f"Latest news for {company_name}:")
                    for news in news_results:
                        st.write(f"{news['url']}")
                        st.write(f"Title: {news['title']}")
                        st.write(f"Snippet: {news['snippet']}")
                        
                else:
                    st.write(f"No latest news found for {company_name}")
                
                status_text.empty()
            else:
                status_text.empty()
                st.write(f"No results found for {company_name}")
        else:
            st.write("Please enter a company name.")

if __name__ == "__main__":
    main()
