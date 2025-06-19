import google.generativeai as genai
from dotenv import load_dotenv
import logging
import json
import os

load_dotenv()

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
try:
    # Use the API key obtained from the environment variable
    # Ensure api_key is not None before configuring
    if api_key:
        # Pass api_key as a keyword argument
        genai.configure(api_key=api_key)
        # Attempt to initialize a model
        try:
             # Using gemini-1.5-flash as you were using it
             model = genai.GenerativeModel('gemini-1.5-flash')
             logging.info("Gemini API client and model initialized successfully.")
        except Exception as model_e:
             logging.error(f"Could not initialize Gemini model: {model_e}. Cannot use Gemini for extraction.")
             model = None # Ensure model is None if initialization fails
    else:
        logging.error("API key is missing. Cannot initialize Gemini model for extraction.")


except Exception as e:
    logging.error(f"Error during initial Gemini configuration: {e}. Cannot use Gemini for extraction.")
    model = None # Ensure model is None if configuration fails



# Define required fields for extraction
required_fields = ["bedrooms", "bathrooms", "price"]


def processUserResponse(data):
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
        # Get existing partial data from the request, default to empty if not provided
        partial_data = data.get("partial_data", {})
        # Ensure partial_data is a dictionary
        if not isinstance(partial_data, dict):
             logging.error("Invalid 'partial_data' format. Expected a dictionary.")
             return {"error": "Invalid 'partial_data' format. Expected a dictionary."}


        logging.info(f"User message: '{user_message}'")
        logging.debug(f"Received partial data: {partial_data}")


        if not user_message and not partial_data:
            logging.debug("No user message or partial data provided, sending initial greeting.")
            return {"bot": "Hi there! 👋 What kind of home are you looking for? (e.g., 2 bed 1 bath under $2000)"}

        # --- Use Gemini for Extraction ---
        # Refined prompt to handle incremental information
        # Emphasize preserving existing data unless explicitly updated
        prompt = f"""You are a helpful assistant extracting housing preferences.
The user has provided a new message. You also have some previously extracted information.
Your task is to extract any new or updated information from the user's latest message
and combine it with the existing information.

IMPORTANT: Preserve the previously extracted information unless the user's latest message
explicitly provides a DIFFERENT value for a field. If the latest message doesn't mention
a field that was previously extracted, keep the old value.

Return ONLY a JSON object with the keys 'bedrooms', 'bathrooms', 'price', and optionally 'city' and/or 'zipcode' if it is mentioned. Make sure
to extract the city as just the name of the city, not the state or country, and make sure it's a valid city name. It is a valid
city name if its part of the following list -- Hillsborough, Bahama, Chapel Hill, Morrisville, Rougemont, 
Raleigh, Durham. Capitalize the first letter of the city name. For the zipcode, make sure it's a valid 5-digit zipcode number.
If the city or zipcode is not mentioned, omit it from the JSON object. 
Also be able to understand if bedroom or bathrooms are spelled slightly differently.
If a specific piece of information is not mentioned in the latest message or previous data, set its value to null (except for 'city', which can be omitted if unknown).
Ensure the JSON object is the *only* content in the response.

Previously extracted information (as JSON): {json.dumps(partial_data)}
User's latest message: '{user_message}'

Combined and Updated JSON Output:
"""

        logging.debug(f"Gemini Extraction Prompt: {prompt}")

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
            updated_extracted_from_gemini = json.loads(parsed_text)
            logging.debug(f"Parsed Updated Extracted Data from Gemini: {updated_extracted_from_gemini}")

        except json.JSONDecodeError as e:
            logging.warning(f"Could not parse Gemini response as JSON: '{parsed_text}', Error: {e}")
            # Return a specific message indicating a parsing issue and include the partial data
            return {
                "bot": "Sorry, I had trouble understanding the AI's response. Could you please try rephrasing your message?",
                "partial_data": partial_data # Return existing partial data
            }
        except Exception as e:
            # Catching other potential errors during content generation
            logging.error(f"Error during Gemini content generation or parsing: {e}")
            return {
                 "error": "An error occurred while processing your request. Please try again.",
                 "partial_data": partial_data # Return existing partial data
            }

        # --- Manual Merge Logic ---
        # Create the final updated_extracted data by merging original partial_data and Gemini's output
        final_updated_extracted = {}
        # Start with original partial data
        for key, value in partial_data.items():
            # Keep the original value if it's not None/empty string
            if value is not None and (not isinstance(value, str) or value.strip() != ""):
                 final_updated_extracted[key] = value

        # Now merge in the data from Gemini's output
        for key, value in updated_extracted_from_gemini.items():
            # If Gemini provided a non-null/non-empty value, use it (overrides original if exists)
            if value is not None and (not isinstance(value, str) or value.strip() != ""):
                final_updated_extracted[key] = value
            # If Gemini returned null or empty, but the key was in original partial_data,
            # the logic above already kept the original non-null value.
            # If the key wasn't in original partial_data and Gemini returned null/empty,
            # it won't be added to final_updated_extracted, which is correct.


        logging.debug(f"Final Merged Updated Extracted Data: {final_updated_extracted}")


        # Check for missing required fields based on the final merged data
        missing = [field for field in required_fields if not final_updated_extracted.get(field) or final_updated_extracted.get(field) is None or (isinstance(final_updated_extracted.get(field), str) and final_updated_extracted.get(field).strip() == "")]
        logging.debug(f"Missing required fields after final merge: {missing}")

        if missing:
            # Construct a follow-up question for missing fields
            # Only include extracted info that is not None or empty string in the follow-up
            partial_info_for_display = {k: v for k, v in final_updated_extracted.items() if v is not None and (not isinstance(v, str) or v.strip() != "")}
            
            # Map fields to conversational phrases
            field_phrases = {
                "bedrooms": lambda v: f"{v} bedroom{'s' if str(v) != '1' else ''}",
                "bathrooms": lambda v: f"{v} bathroom{'s' if str(v) != '1' else ''}",
                "price": lambda v: f"under ${v}",
                "city": lambda v: f"in {v}"
            }

            # Build human-readable phrases for what we already have
            phrases = [field_phrases[k](v) for k, v in final_updated_extracted.items()
                if v is not None and (not isinstance(v, str) or v.strip() != "") and k in field_phrases]
            if phrases:
                follow_up_question = "Okay! I have " + " and ".join(phrases) + " so far."
            else:
                follow_up_question = "Okay, I need a little more information."

            # Ask for the missing fields
            follow_up_question += f" Could you please tell me the {' and '.join(missing)}?"

            # Return the follow-up question and the final updated partial data
            return {
                "bot": follow_up_question,
                "partial_data": final_updated_extracted # Return the final updated partial data
            }

        # If all required fields are present, save and confirm
        try:
            # Ensure the directory exists if you plan to save files
            # os.makedirs(os.path.dirname("user_preferences.json"), exist_ok=True)
            with open("user_preferences.json", "w") as f:
                json.dump(final_updated_extracted, f, indent=4)
            logging.info(f"Saved user preferences: {final_updated_extracted}")
        except IOError as e:
            logging.error(f"Error saving user preferences file: {e}")
            # Decide how to handle file saving errors - maybe just log and continue?


        # All info gathered, send confirmation and potentially reset partial data on the client side
        return {
            "bot": f"Awesome! You're looking for a {final_updated_extracted.get('bedrooms', 'N/A')} bed, {final_updated_extracted.get('bathrooms', 'N/A')} bath home under ${final_updated_extracted.get('price', 'N/A')}. We'll start searching!",
            "final_data": final_updated_extracted, # Use 'final_data' key to indicate completion
            "partial_data": {} # Suggest the client clears partial data for a new search
        }

    except Exception as e:
        logging.exception("An unexpected error occurred in housing_chat:")
        # Return the existing partial data even in case of unexpected errors
        return {
            "error": str(e),
            "partial_data": partial_data # Return existing partial data
        }
