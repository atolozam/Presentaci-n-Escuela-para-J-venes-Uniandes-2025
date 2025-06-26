# pip install playwright jmespath scrapfly-sdk

import asyncio
import csv
import time
from playwright.sync_api import sync_playwright


def scrape_multiple_tweets_from_timeline(url: str, max_tweets: int = 100) -> list:
    """
    Scrape multiple tweets from a user's timeline e.g.: https://x.com/Scrapfly_dev
    """
    _xhr_calls = []
    all_tweets = []

    def intercept_response(response):
        """capture all background requests and save them"""
        # we can extract details from background requests
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # enable background request intercepting:
        page.on("response", intercept_response)
        # go to url and wait for the page to load
        page.goto(url)
        page.wait_for_selector("[data-testid='primaryColumn']")
        
        # Wait a bit more for tweets to load
        page.wait_for_timeout(3000)
        
        # Scroll to load more tweets
        scroll_count = 0
        max_scrolls = 10  # Limit scrolls to avoid infinite loop
        
        while len(all_tweets) < max_tweets and scroll_count < max_scrolls:
            # Process current tweets
            timeline_calls = [f for f in _xhr_calls if "UserTweets" in f.url or "UserMedia" in f.url]
            
            for xhr in timeline_calls:
                try:
                    data = xhr.json()
                    print(f"Procesando URL: {xhr.url[:100]}...")  # Shortened URL for readability
                    
                    # Navigate through the response structure to find tweets
                    if 'data' in data and 'user' in data['data']:
                        user_result = data['data']['user']['result']
                        
                        # Try different timeline structures
                        timeline = None
                        if 'timeline_v2' in user_result:
                            timeline = user_result['timeline_v2']['timeline']
                        elif 'timeline' in user_result:
                            timeline_outer = user_result['timeline']
                            
                            # Check if there's a nested timeline
                            if 'timeline' in timeline_outer:
                                timeline = timeline_outer['timeline']
                            else:
                                timeline = timeline_outer
                        
                        if timeline and 'instructions' in timeline:
                            instructions = timeline.get('instructions', [])
                            
                            for instruction in instructions:
                                if instruction.get('type') == 'TimelineAddEntries':
                                    entries = instruction.get('entries', [])
                                    
                                    # Look for tweet entries
                                    for entry in entries:
                                        if entry.get('content', {}).get('entryType') == 'TimelineTimelineItem':
                                            item_content = entry['content'].get('itemContent', {})
                                            if 'tweet_results' in item_content:
                                                tweet_result = item_content['tweet_results']['result']
                                                if 'legacy' in tweet_result:
                                                    tweet_data = {
                                                        'tweet_id': tweet_result['legacy'].get('id_str', ''),
                                                        'tweet_text': tweet_result['legacy'].get('full_text', ''),
                                                        'created_at': tweet_result['legacy'].get('created_at', ''),
                                                        'retweet_count': tweet_result['legacy'].get('retweet_count', 0),
                                                        'favorite_count': tweet_result['legacy'].get('favorite_count', 0),
                                                        'reply_count': tweet_result['legacy'].get('reply_count', 0),
                                                        'username': url.split('/')[-1],
                                                        'tweet_url': f"https://x.com/{url.split('/')[-1]}/status/{tweet_result['legacy'].get('id_str', '')}"
                                                    }
                                                    
                                                    # Check if tweet is not already in our list
                                                    if not any(tweet['tweet_id'] == tweet_data['tweet_id'] for tweet in all_tweets):
                                                        all_tweets.append(tweet_data)
                                                        print(f"Tweet {len(all_tweets)}: {tweet_data['tweet_text'][:50]}...")
                                                        
                                                        if len(all_tweets) >= max_tweets:
                                                            return all_tweets
                                
                except Exception as e:
                    print(f"Error parsing timeline data: {e}")
                    continue
            
            # Scroll down to load more tweets
            if len(all_tweets) < max_tweets:
                print(f"Scroll {scroll_count + 1}: Tweets encontrados hasta ahora: {len(all_tweets)}")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)  # Wait for new tweets to load
                scroll_count += 1
        
        return all_tweets


def save_tweets_to_csv(tweets: list, filename: str = "tweets.csv"):
    """
    Save tweets to a CSV file
    """
    if not tweets:
        print("No hay tweets para guardar")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['tweet_id', 'username', 'tweet_text', 'created_at', 'retweet_count', 'favorite_count', 'reply_count', 'tweet_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for tweet in tweets:
            writer.writerow(tweet)
    
    print(f"✅ {len(tweets)} tweets guardados en {filename}")


if __name__ == "__main__":
    # Extraer los primeros 100 tweets del timeline de un usuario
    user_url = "https://x.com/petrogustavo"  # Cambia por el usuario que quieras
    max_tweets = 100  # Número de tweets a extraer
    
    print(f"Extrayendo hasta {max_tweets} tweets de {user_url}...")
    tweets = scrape_multiple_tweets_from_timeline(user_url, max_tweets)
    
    if tweets:
        print(f"\n📊 Resumen:")
        print(f"Total de tweets extraídos: {len(tweets)}")
        print(f"Primer tweet: {tweets[0]['tweet_text'][:100]}...")
        print(f"Último tweet: {tweets[-1]['tweet_text'][:100]}...")
        
        # Guardar en CSV
        filename = f"tweets_{user_url.split('/')[-1]}_{len(tweets)}.csv"
        save_tweets_to_csv(tweets, filename)
        
        # Mostrar algunos tweets de ejemplo
        print(f"\n🐦 Primeros 3 tweets:")
        for i, tweet in enumerate(tweets[:3]):
            print(f"{i+1}. {tweet['tweet_text'][:150]}...")
            print(f"   📅 {tweet['created_at']} | 🔄 {tweet['retweet_count']} | ❤️ {tweet['favorite_count']}")
            print(f"   🔗 {tweet['tweet_url']}\n")
    else:
        print("❌ No se pudieron extraer tweets")

    # Avoid web scraping detection: https://scrapfly.io/blog/how-to-scrape-without-getting-blocked-tutorial/#anti-scraping-protection-services
    # Other ideas: https://github.com/vladkens/twscrape/ | https://github.com/d60/twikit