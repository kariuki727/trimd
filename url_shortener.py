import requests
import json

TRIMD_API_ENDPOINT = "https://trimd.cc/api/url/add"

def shorten_url(long_url: str, api_key: str) -> str | None:
    """
    Shortens a single URL using the Trimd API.

    :param long_url: The original long URL to be shortened.
    :param api_key: The developer API key for Trimd.
    :return: The shortened URL as a string, or None if shortening fails.
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "url": long_url,
        # 'status': 'public' # Optional: make link public if desired
    }

    try:
        response = requests.post(TRIMD_API_ENDPOINT, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        result = response.json()
        
        # Check for API-specific error, as per the documentation
        if result.get("error") == 0 and "shorturl" in result:
            return result["shorturl"]
        else:
            print(f"Trimd API Error for URL '{long_url}': {result.get('message', 'Unknown error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed to Trimd API: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response from Trimd API.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during URL shortening: {e}")
        return None

def find_and_shorten_urls(text: str, api_key: str) -> str:
    """
    Finds and replaces all URLs in a given text with their shortened versions.

    :param text: The input text potentially containing multiple URLs.
    :param api_key: The developer API key for Trimd.
    :return: The text with all found URLs replaced by their shortened versions.
    """
    import re
    # Simple regex to find common URL patterns (http/https)
    url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
    
    # Use a set to store unique long URLs and their shortened versions to avoid redundant API calls
    url_map = {}
    
    # 1. Find all unique URLs
    long_urls = set(url_pattern.findall(text))
    
    # 2. Shorten each unique URL
    for long_url in long_urls:
        short_url = shorten_url(long_url, api_key)
        if short_url:
            url_map[long_url] = short_url
        else:
            # If shortening fails, keep the original URL
            url_map[long_url] = long_url 

    # 3. Replace long URLs with short ones in the original text
    new_text = text
    for long_url, short_url in url_map.items():
        # Use re.escape for safe string replacement, especially with regex patterns
        new_text = new_text.replace(long_url, short_url)

    return new_text
