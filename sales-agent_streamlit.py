from dotenv import load_dotenv
import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import logging
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Set OpenAI and SERP API keys
openai_api_key = os.getenv('openai_api_key')
serp_api_key = os.getenv('serp_api_key')

# Initialize the OpenAI client with API key
client = OpenAI(api_key=openai_api_key)

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Capture INFO level and above
    format='%(asctime)s - %(levelname)s - %(message)s'  # Simple format with timestamp, log level, and message
)

# Define scraping function to extract content for a given URL
def scrape_targeted_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract basic content
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
        "api_key": serp_api_key  # Use the SERP API key here
    }
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        search_results = response.json()
        results = []
        for result in search_results.get('organic_results', [])[:4]:  # Limit to top 4 results
            results.append({
                'url': result.get('link'),
                'text': result.get('snippet', '')
            })
        return results
    else:
        logging.error(f"Request failed with status code: {response.status_code}")
        return None

# Define a function to summarize search results' content extracted from scraping using Open AI
def summarize_search_results(search_results):
    all_texts = []
    for result in search_results:
        content = scrape_targeted_content(result['url'])
        text = content.get("body_text", "")
        if text:
            all_texts.append(text)
        time.sleep(1)  # Respectful delay between requests
    
    combined_text = ' '.join(all_texts)
    max_length = 1000  # Maximum token limit for GPT-4 is around 4096 tokens
    if len(combined_text) > max_length:
        combined_text = combined_text[:max_length]
    
    #st.write(f"Combined text for summarization:\n{combined_text[:1000]}...")  # Print only the first 1000 characters for brevity
    
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
            st.write(f"Searching information for {company_name}...")
            search_results = search_company(company_name)
            
            if search_results:
                for result in search_results:
                    content = scrape_targeted_content(result['url'])
                    #st.write(f"URL: {result['url']}")
                    #st.write(f"Title: {content['title']}")
                    #st.write(f"Meta Description: {content['meta_description']}")
                    #st.write(f"Body Text: {content['body_text'][:200]}...")  # Display only the first 200 characters of body text
                
                summary = summarize_search_results(search_results)
                results_output = "\n\n".join([f"URL: {result['url']}\nText: {result['text']}" for result in search_results])
                st.write(f"Summary for {company_name}:")
                st.write(summary)
                st.write("URLs identified:")
                st.write(results_output)
            else:
                st.write(f"No results found for {company_name}")
        else:
            st.write("Please enter a company name.")

if __name__ == "__main__":
    main()
