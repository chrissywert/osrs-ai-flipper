import streamlit as st
import pandas as pd     # <--- This MUST be at the top
import requests
from google import genai

# Now do the AI setup
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"API Key not found. Please check your Secrets settings! Details: {e}")
    # We create a dummy client so the rest of the app doesn't crash
    client = None 

# Now the rest of your app logic starts...
df_prices = pd.DataFrame.from_dict(prices, orient='index')
# --- 2. FETCH DATA ---
headers = {'User-Agent': 'OSRS_AI_Project - @YourHandle'}
prices = requests.get("https://prices.runescape.wiki/api/v1/osrs/latest", headers=headers).json()['data']
mapping = requests.get("https://prices.runescape.wiki/api/v1/osrs/mapping", headers=headers).json()

# --- 3. PROCESS ---
df_prices = pd.DataFrame.from_dict(prices, orient='index')
df_prices['id'] = df_prices.index.astype(int)
df_items = pd.DataFrame(mapping)[['id', 'name']]
df = pd.merge(df_items, df_prices, on='id').dropna()

# 2% Tax & Profit Logic
df['tax'] = df['high'].apply(lambda x: min(int(x * 0.02), 5000000) if x >= 100 else 0)
df['true_profit'] = (df['high'] - df['tax']) - df['low']

# --- 4. DISPLAY TABLE ---
st.subheader("Live Market Opportunities")
top_flips = df[['name', 'high', 'low', 'true_profit']].sort_values(by='true_profit', ascending=False).head(10)
st.dataframe(top_flips, use_container_width=True)

# --- 5. AI ADVISOR ---
st.divider()
st.subheader("🤖 AI Flip Consultant")

if st.button("Analyze Current Market"):
    with st.spinner("Calculating risks and rewards..."):
        # We send the table to Gemini 3
        prompt = f"I am an OSRS flipper. Current tax is 2%. Analyze these top flips: {top_flips.to_string()}. Which is best for a quick profit?"
        
        response = client.models.generate_content(
            model="gemini-3-flash", 
            contents=prompt
        )
        st.write(response.text)