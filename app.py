import streamlit as st
import pandas as pd
import requests
from google import genai

# --- 1. AI SETUP ---
# This looks for the key in your Streamlit Cloud "Secrets" settings
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"AI Key Error: {e}")
    client = None 

# --- 2. FETCH DATA (Now at the top!) ---
headers = {'User-Agent': 'OSRS_AI_Project - @YourHandle'}

# We fetch the data BEFORE we try to use it
try:
    prices_raw = requests.get("https://prices.runescape.wiki/api/v1/osrs/latest", headers=headers).json()
    prices = prices_raw['data']
    mapping = requests.get("https://prices.runescape.wiki/api/v1/osrs/mapping", headers=headers).json()
except Exception as e:
    st.error(f"Wiki API Error: {e}")
    st.stop() # Stops the app if the internet/Wiki is down

# --- 3. PROCESS DATA ---
df_prices = pd.DataFrame.from_dict(prices, orient='index')
df_prices['id'] = df_prices.index.astype(int)
df_items = pd.DataFrame(mapping)[['id', 'name']]

# Merge items and prices
df = pd.merge(df_items, df_prices, on='id').dropna()

# 1% Tax (Old OSRS tax was 1%, capped at 5m) & Profit Logic
# Note: Most flippers calculate 1% tax, though you mentioned 2% earlier. 
# Standard OSRS GE tax is 1%.
df['tax'] = df['high'].apply(lambda x: min(int(x * 0.01), 5000000) if x >= 100 else 0)
df['true_profit'] = (df['high'] - df['tax']) - df['low']

# --- 4. DISPLAY TABLE ---
st.title("⚔️ OSRS AI Flipper")
st.subheader("Live Market Opportunities")

top_flips = df[['name', 'high', 'low', 'true_profit']].sort_values(by='true_profit', ascending=False).head(10)
st.dataframe(top_flips, use_container_width=True)

# --- 5. AI ADVISOR ---
st.divider()
st.subheader("🤖 AI Flip Consultant")

if st.button("Analyze Current Market"):
    if client is None:
        st.error("Cannot run analysis: AI Client not initialized.")
    else:
        with st.spinner("Calculating risks and rewards..."):
            prompt = f"I am an OSRS flipper. Analyze these top 10 flips: {top_flips.to_string()}. Which 3 are the best for a quick profit and why?"
            
            # Using Gemini 3 Flash
            response = client.models.generate_content(
                model="gemini-3-flash", 
                contents=prompt
            )
            st.write(response.text)