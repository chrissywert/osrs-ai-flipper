import requests
import pandas as pd
from google import genai

# --- 1. SETUP ---
headers = {'User-Agent': 'Ge_Flipping_Project - @ChrissyWert'}
client = genai.Client(api_key="AIzaSyDHZyCuLrYFVJniNr1XJUC5qJjrMIFmOHA") # PASTE YOUR KEY HERE

# --- 2. FETCH DATA ---
print("Fetching OSRS market data...")
mapping = requests.get("https://prices.runescape.wiki/api/v1/osrs/mapping", headers=headers).json()
prices = requests.get("https://prices.runescape.wiki/api/v1/osrs/latest", headers=headers).json()['data']

# --- 3. ORGANIZE DATA ---
items_df = pd.DataFrame(mapping)[['id', 'name']]
prices_df = pd.DataFrame.from_dict(prices, orient='index')
prices_df['id'] = prices_df.index.astype(int)
df = pd.merge(items_df, prices_df, on='id').dropna()

# Calculate 2% Tax and True Profit
df['tax'] = df['high'].apply(lambda x: min(int(x * 0.02), 5000000) if x >= 100 else 0)
df['true_profit'] = (df['high'] - df['tax']) - df['low']

# Grab the top 5 most profitable items to show the AI
top_5 = df.sort_values(by='true_profit', ascending=False).head(5).to_string(columns=['name', 'true_profit'])

# --- 4. THE AI BRAIN ---
print("Asking the AI for advice...")

prompt = f"""
I am flipping on the OSRS Grand Exchange with a 2% tax. 
Here are the current top 5 profit items:
{top_5}

Which of these is the best flip? Briefly explain why, considering that 
very high profits often mean the item is hard to sell (low volume).
"""

response = client.models.generate_content(
    model="gemini-3-flash-preview", 
    contents=prompt
)

print("\n--- AI FLIPPING ADVISOR ---")
print(response.text)