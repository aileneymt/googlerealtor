import google.generativeai as genai
import logging
import json
import os

api_key=os.getenv("GEMINI_API_KEY")


# Configure logging
logging.basicConfig(level=logging.DEBUG)



# Check if API key is loaded
if not api_key:
    logging.error("GOOGLE_API_KEY environment variable not set.")
    # In a production environment, you might want to exit or raise a more critical error here
    # import sys
    # sys.exit("Error: GOOGLE_API_KEY environment variable not set.")
else:
    logging.info("GOOGLE_API_KEY loaded successfully.")


model = None
# Use the API key obtained from the environment variable
    # Ensure api_key is not None before configuring
genai.configure(api_key=api_key)
# Attempt to initialize a model
try:
    # Using gemini-1.5-flash as you were using it
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.2})
    logging.info("Gemini API client and model initialized successfully.")
except Exception as model_e:
    logging.error(f"Could not initialize Gemini model: {model_e}. Cannot use Gemini for extraction.")
    model = None # Ensure model is None if initialization fails



# Define places api keyword options
place_types = [
    "accounting",
    "airport",
    "amusement_park",
    "aquarium",
    "art_gallery",
    "atm",
    "bakery",
    "bank",
    "bar",
    "beauty_salon",
    "bicycle_store",
    "book_store",
    "bowling_alley",
    "bus_station",
    "cafe",
    "campground",
    "car_dealer",
    "car_rental",
    "car_repair",
    "car_wash",
    "casino",
    "cemetery",
    "clothing_store",
    "convenience_store",
    "courthouse",
    "dentist",
    "department_store",
    "doctor",
    "drugstore",
    "electronics_store",
    "embassy",
    "finance",
    "fire_station",
    "florist",
    "funeral_home",
    "furniture_store",
    "gas_station",
    "general_contractor",
    "grocery_store",
    "hair_care",
    "hardware_store",
    "health",
    "hindu_temple",
    "home_goods_store",
    "hospital",
    "insurance_agency",
    "jewelry_store",
    "laundry",
    "lawyer",
    "library",
    "light_rail_station",
    "liquor_store",
    "local_government_office",
    "locksmith",
    "lodging",
    "meal_delivery",
    "meal_takeaway",
    "mosque",
    "movie_rental",
    "movie_theater",
    "moving_company",
    "museum",
    "night_club",
    "painter",
    "park",
    "parking",
    "pet_store",
    "pharmacy",
    "physiotherapist",
    "plumber",
    "police",
    "post_office",
    "real_estate_agency",
    "restaurant",
    "roofing_contractor",
    "rv_park",
    "school",
    "shoe_store",
    "shopping_mall",
    "spa",
    "stadium",
    "storage",
    "store",
    "subway_station",
    "supermarket",
    "synagogue",
    "taxi_stand",
    "tourist_attraction",
    "train_station",
    "transit_station",
    "travel_agency",
    "university",
    "veterinarian",
    "zoo",
    "administrative_area_level_1",
    "administrative_area_level_2",
    "administrative_area_level_3",
    "administrative_area_level_4",
    "administrative_area_level_5",
    "colloquial_area",
    "country",
    "floor",
    "geocode",
    "intersection",
    "locality",
    "natural_feature",
    "neighborhood",
    "plus_code",
    "political",
    "point_of_interest",
    "post_box",
    "postal_code",
    "postal_code_prefix",
    "postal_code_suffix",
    "postal_town",
    "premise",
    "room",
    "route",
    "street_address",
    "street_number",
    "sublocality",
    "sublocality_level_1",
    "sublocality_level_2",
    "sublocality_level_3",
    "sublocality_level_4",
    "sublocality_level_5",
    "subpremise"
]

def processNearbyLocationRequest(data):
    if model is None:
        logging.error("Gemini model not initialized. Cannot process request using Gemini.")
        # Return a 503 Service Unavailable error if the backend service isn't ready
        return {"error": "Backend AI service unavailable. Please try again later."}

    try:
        logging.debug(f"Received JSON data: {data}")

        # Ensure data is not None and has the 'message' key
        if data is None or 'message' not in data:
             logging.error("Invalid or missing JSON data in request body.")
             return {"error": "Invalid request payload. Expected JSON with 'message' key and optionally 'partial_data'."}

        user_message = data.get("message", "").strip()
        results = {}

        logging.info(f"User message: '{user_message}'")


        if not user_message:
            logging.debug("No user message, sending initial greeting.")
            return {"bot": "Hi there, ask me about any places nearby you're curious about! I can show you nearby schools, cafes, and more!"}

        # --- Use Gemini for Extraction ---
        # Refined prompt to handle incremental information
        # Emphasize preserving existing data unless explicitly updated
        prompt = f"""You are serving as a middleman between a user and the Google Places API.
            The user is looking for places nearby their current location, and will ask you something like show me hospitals nearby.
            What you will do is extract the specific places the user is looking for, correlate it with a keyword the Places API is capable
            of searching for, and return that keyword. If no match or correlation can be made, return null. It's possible that the user will slightly mispell what they're looking for, but still be able to understand what they're asking for.
            If the user's response has multiple locations of interest, just return the first one.
            Return ONLY a JSON object with the keys "keyword" and the corresponding keyword location. This should always be in string format if valid, otherwise this value will be null if no match can be made between the users message and valid place types in the Places API. 
            
            Include another property "location" with the location the user requested in plural format. For example, if they request for a post office you would return "post offices", and if they requested coffee shops you would return "coffee shops". This is just so its easy to print out
            what location the user is looking for since the places array typically has underscores in its keywords. This is basically just a property that repeats what the user said (make sure to not have any spelling/grammatical mistakes inside this property). 
            It should make grammatical sense in the sentence "Searching for nearby [locations]." This will also be null/None if the user's input isn't understandable.
            Ensure the JSON object is the *only* content in the response.

            User's latest message: '{user_message}'
            Use this array to find the closest match to what the user is looking for: [{place_types}] ...

            Combined and Updated JSON Output:
            """


        try:
            logging.debug(f"Attempting to call generate_content. Current model state: {model}")
            response = model.generate_content(prompt)
            # Access the text content of the response
            # Strip whitespace and potentially markdown code block indicators
            parsed_text = response.text.strip()
            if parsed_text.startswith("```json") and parsed_text.endswith("```"):
                 parsed_text = parsed_text[len("```json"): -len("```")].strip()
            elif parsed_text.startswith("```") and parsed_text.endswith("```"):
                 # Handle generic code blocks too
                 parsed_text = parsed_text[len("```"): -len("```")].strip()

            logging.debug(f"Gemini Raw Response Text (after stripping): '{parsed_text}'")

            # Attempt to parse the JSON response
            # Replace single quotes with double quotes just in case
            parsed_text = parsed_text.replace("'", '"')
            results = json.loads(parsed_text)
            logging.debug(f"Parsed Updated Extracted Data from Gemini: {results}")

        except json.JSONDecodeError as e:
            logging.warning(f"Could not parse Gemini response as JSON: '{parsed_text}', Error: {e}")
            # Return a specific message indicating a parsing issue and include the partial data
            return {
                "bot": "Sorry, I had trouble understanding the AI's response. Could you please try rephrasing your message?",
            }
        except Exception as e:
            # Catching other potential errors during content generation
            logging.error(f"Error during Gemini content generation or parsing: {e}")
            return {
                 "error": "An error occurred while processing your request. Please try again."
            }

       
        if results["keyword"] is None:
            # Construct a follow-up question for missing fields
            # Only include extracted info that is not None or empty string in the follow-up
            
            follow_up_question = "Sorry, I'm not sure what you're looking for, could you please try again?"

            # Return the follow-up question and the final updated partial data
            return {
                "bot": follow_up_question,
               
            }

        # If all required fields are present, save and confirm
        # All info gathered, send confirmation and potentially reset partial data on the client side
        logging.debug(f'Completed parsing. keyword: {results.get("keyword")}')
        return {
            "bot": f"Searching for nearby {results.get('location', 'N/A')}, check out the map!",
            "keyword": results.get("keyword", None),
            "location": results.get("location", None),
        }

    except Exception as e:
        logging.exception("An unexpected error occurred in grounding.py:")
        # Return the existing partial data even in case of unexpected errors
        return {
            "error": str(e)
        }
