import google.generativeai as genai
from dotenv import load_dotenv
import logging
import os
import pandas as pd

# === Load and Normalize CSV ===
DURHAM_COUNTY_CSV_PATH = "data/durham-county.csv"
redfin_df = pd.read_csv(DURHAM_COUNTY_CSV_PATH)
redfin_df["ADDRESS"] = redfin_df["ADDRESS"].astype(str).str.strip().str.lower()

# === Lookup Function ===
def lookup_property_info(address: str):
    street_only = address.split(",")[0].strip().lower()
    matches = redfin_df[redfin_df["ADDRESS"] == street_only]

    if matches.empty:
        print(f"❌ No match found for: '{street_only}'")
        print("📋 Example addresses from CSV:")
        print("\n".join(redfin_df["ADDRESS"].dropna().unique()[:5]))
        return None

    return matches.iloc[0].to_dict()

# === Load API Key ===
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# === Configure Logging ===
logging.basicConfig(level=logging.DEBUG)

if not api_key:
    logging.error("GEMINI_API_KEY environment variable not set.")
else:
    logging.info("GEMINI_API_KEY loaded successfully.")

# === Initialize Gemini Model ===
model = None
try:
    if api_key:
        genai.configure(api_key=api_key)
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            logging.info("Gemini API client and model initialized successfully.")
        except Exception as model_e:
            logging.error(f"❌ Could not initialize Gemini model: {model_e}")
            model = None
    else:
        logging.error("API key is missing. Cannot initialize Gemini model.")

except Exception as e:
    logging.error(f"🔥 Error during Gemini setup: {e}")
    model = None

# === Description Generator ===
def get_property_description(address: str) -> str:
    print(f"📍 get_property_description() called with address: {address}")
    
    if model is None:
        print("❌ Gemini model is not initialized.")
        return "This property offers a unique opportunity in a great neighborhood!"

    info = lookup_property_info(address)
    if not info:
        return "No detailed information found for this property."

    def safe(val): return str(val) if pd.notna(val) else "N/A"

    prompt = f"""
You are a real estate assistant. Write a clear and honest one-paragraph description for the following home. Do not exaggerate or glamorize it — just summarize the real features plainly, like Redfin or Zillow. Be natural, neutral, and accurate.

Here is the info:
- Property type: {safe(info.get("PROPERTY TYPE"))}
- Address: {safe(info.get("ADDRESS"))}, {safe(info.get("CITY"))}, {safe(info.get("STATE OR PROVINCE"))}, {safe(info.get("ZIP OR POSTAL CODE"))}
- Price: ${safe(info.get("PRICE"))}
- Beds: {safe(info.get("BEDS"))}
- Baths: {safe(info.get("BATHS"))}
- Square feet: {safe(info.get("SQUARE FEET"))}
- Lot size: {safe(info.get("LOT SIZE"))}
- Year built: {safe(info.get("YEAR BUILT"))}
- Neighborhood: {safe(info.get("LOCATION"))}

Make the paragraph useful to someone deciding whether to view this house, and make it sound
natural, like a realtor's posting. Do not mention anything that's "unknown" or make things up.
"""

    try:
        print("🧠 Sending prompt to Gemini...")
        response = model.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        else:
            return "Could not generate description."
    except Exception as e:
        print(f"🔥 Error in Gemini call: {e}")
        return "Could not generate description."