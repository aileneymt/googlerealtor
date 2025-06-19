from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
from src import stats
from src import gemini
from src import maps
from src import places
from src import model

from src import grounding
from src.description import get_property_description

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

# Removed the regex extraction function
# Flask setup
app = Flask(__name__)
CORS(app)

load_dotenv()

MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE=os.getenv("MYSQL_DATABASE")
DB_HOST=os.getenv("DB_HOST")

#sql alchemy stuff
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{DB_HOST}/{MYSQL_DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class DurhamCounty(db.Model):
    __tablename__ = 'durham-county'

    ID = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    PROPERTY_TYPE = db.Column('PROPERTY TYPE', db.Text, nullable=True)
    ADDRESS = db.Column('ADDRESS', db.Text, nullable=True)
    CITY = db.Column('CITY', db.Text, nullable=True)
    STATE_OR_PROVINCE = db.Column('STATE OR PROVINCE', db.Text, nullable=True)
    ZIP_OR_POSTAL_CODE = db.Column('ZIP OR POSTAL CODE', db.BigInteger, nullable=True)
    PRICE = db.Column('PRICE', db.BigInteger, nullable=True)
    BEDS = db.Column('BEDS', db.BigInteger, nullable=True)
    BATHS = db.Column('BATHS', db.Float, nullable=True)
    LOCATION = db.Column('LOCATION', db.Text, nullable=True)
    SQUARE_FEET = db.Column('SQUARE FEET', db.BigInteger, nullable=True)
    LOT_SIZE = db.Column('LOT SIZE', db.BigInteger, nullable=True)
    YEAR_BUILT = db.Column('YEAR BUILT', db.BigInteger, nullable=True)
    DAYS_ON_MARKET = db.Column('DAYS ON MARKET', db.BigInteger, nullable=True)
    DOLLAR_PER_SQUARE_FEET = db.Column('DOLLAR PER SQUARE FEET', db.BigInteger, nullable=True)
    HOA_PER_MONTH = db.Column('HOA PER MONTH', db.BigInteger, nullable=True)
    URL = db.Column('URL', db.Text, nullable=True)
    LATITUDE = db.Column('LATITUDE', db.Float, nullable=True)
    LONGITUDE = db.Column('LONGITUDE', db.Float, nullable=True)


@app.route('/housing-chat', methods=['POST'])
def housing_chat():
    # Check if the Gemini model was initialized successfully
    data = request.get_json()

    result = gemini.processUserResponse(data)
    if "error" in result:
        return jsonify(result), 400
    else:
        return jsonify(result)
    
@app.route('/get-description', methods=['POST'])
def get_description():
    data = request.get_json()
    address = data.get("address")  # 🔥 FIXED: This must be a string key

    if not address:
        return jsonify({"description": "No address provided"}), 400

    try:
        desc = get_property_description(address)
        return jsonify({"description": desc})
    except Exception as e:
        return jsonify({"description": "Error generating description", "error": str(e)}), 500
    

@app.route('/')
def home():
    return "✅ Gemini Smart Housing Bot is live!"

#work on this area
@app.route("/predictions/sales")
def getPrediction():
    beds = request.args.get('beds')
    baths = request.args.get('baths')
    square_feet = request.args.get('square_feet')
    lot_size = request.args.get('lot_size')
    year_built = request.args.get('year_built')
    property_type = request.args.get('property_type')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    zipcode = request.args.get('zipcode')


    if not beds or not baths or not square_feet or not lot_size or not year_built or not property_type or not latitude or not longitude or not zipcode:
        return jsonify({"error": "missing parameters"}), 400
    try:
        df = model.load_data(beds, baths, square_feet, lot_size, year_built, property_type, latitude, longitude, zipcode, 2025, 5)
        predicted_price = model.prediction(df)
        projected_price = model.project(df)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    projected_price26 = str(round(projected_price[0], 2))
    projected_price27 = str(round(projected_price[1], 2))
    projected_price28 = str(round(projected_price[2], 2))
    projected_price29 = str(round(projected_price[3], 2))
    projected_price30 = str(round(projected_price[4], 2))
    predicted_price = str(predicted_price)

    fig = model.generate_plot(projected_price)
    #return send_file(fig, mimetype='image/png', )

    return jsonify({"predicted 2025": predicted_price, "projected 2026": projected_price26, "projected 2027": projected_price27,  
                    "projected 2028": projected_price28, "projected 2029": projected_price29, "projected 2030": projected_price30})


@app.route("/graph")
def getGraph():
    beds = request.args.get('beds')
    baths = request.args.get('baths')
    square_feet = request.args.get('square_feet')
    lot_size = request.args.get('lot_size')
    year_built = request.args.get('year_built')
    property_type = request.args.get('property_type')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    zipcode = request.args.get('zipcode')

    if not square_feet:
        if lot_size:
            square_feet = lot_size * 0.15
    if not lot_size:
        if square_feet:
            lot_size = square_feet * 1/0.15
            
    if not beds or not baths or not square_feet or not lot_size or not year_built or not property_type or not latitude or not longitude or not zipcode:
        return jsonify({"error": "missing parameters"}), 400
    try:
        df = model.load_data(beds, baths, square_feet, lot_size, year_built, property_type, latitude, longitude, zipcode, 2025, 5)
        predicted_price = model.prediction(df)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    fig = model.project(predicted_price, int(zipcode))
    return send_file(fig, mimetype='image/png', )
    
@app.route("/list")
def getList():
    beds = request.args.get('beds')
    baths = request.args.get('baths')
    square_feet = request.args.get('square_feet')
    lot_size = request.args.get('lot_size')
    year_built = request.args.get('year_built')
    property_type = request.args.get('property_type')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    zipcode = request.args.get('zipcode')


    if not beds or not baths or not square_feet or not lot_size or not year_built or not property_type or not latitude or not longitude or not zipcode:
        return jsonify({"error": "missing parameters"}), 400
    try:
        df = model.load_data(beds, baths, square_feet, lot_size, year_built, property_type, latitude, longitude, zipcode, 2025, 5)
        predicted_price = model.prediction(df)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    mytable = model.get_list(predicted_price, int(zipcode))
    return send_file(mytable, mimetype='image/png', )

@app.route("/stats/sales")
def getSaleStats():
    zipcode = request.args.get('zipcode')
    years = request.args.get('years')
    if zipcode and years:
        df = stats.load_data()
        future_price = stats.predict_and_plot_zipcode(df, int(zipcode), int(years))
        return jsonify({"future_price": future_price})
    else:
        return jsonify({"error": "Zipcode and years parameter are required"}), 400
'''
@app.route("/search")
def getHouses():
    city = request.args.get('city')
    price = request.args.get('price') # in 100k, so it'd be like 550
    beds = request.args.get('beds')
    baths = request.args.get('baths')
    if price and beds and baths:
        houses = maps.get_houses(price, beds, baths, city)
        return jsonify({"houses": houses})
    else:
        return jsonify({"error": "Price, bedrooms, and bathrooms are required"})
'''

@app.route("/search")
def getHouses():
    city = request.args.get('city')
    price = request.args.get('price') # in 100k, so it'd be like 550
    beds = request.args.get('beds')
    baths = request.args.get('baths')
    if price and beds and baths:
        try:
            price = int(price)
            beds = int(beds)
            baths = float(baths)
        except (ValueError, TypeError):
            return jsonify({"error": "Price, beds, and baths must be numeric"}), 400
        
        query = db.session.query(DurhamCounty)

        filters = [
            DurhamCounty.PRICE <= price,
            DurhamCounty.BEDS >= beds,
            DurhamCounty.BATHS >= baths,
        ]

        if city:
            filters.append(DurhamCounty.CITY == city)
        
        
        results = query.filter(and_(*filters)).order_by(DurhamCounty.PRICE).all()

        houses = [r.__dict__ for r in results]
        for house in houses:
            house.pop('_sa_instance_state', None)  # remove SQLAlchemy internal key
        return jsonify({"houses": houses})
    else:
        return jsonify({"error": "Price, bedrooms, and bathrooms are required"})

@app.route("/places")
def getPlacesNearby():
    keyword = request.args.get("type")
    lat = request.args.get("lat")
    long = request.args.get("long")
    if keyword and lat and long:
        result = places.get_places_nearby(float(lat), float(long), keyword)
        if "error" in result:
            return jsonify(result), 503
        else:
            return jsonify(result)# returns array of json objects, the array doesnt have a name
    else:
        return jsonify({"error": "Latitude, longitude, and the keyword must be provided"}), 400
    

@app.route("/search/places", methods=['POST'])
def extractKeyword():
    data = request.get_json()
    lat = request.args.get("lat")
    long = request.args.get("long")
    if not lat or not long:
        return jsonify({"error": "Latitude and longitude must be provided."}), 400

    response = grounding.processNearbyLocationRequest(data)
    print("grounding complete")
    if "keyword" not in response: # couldn't determine a location
        return ({"message": response["bot"]})
    else:
        locations = places.get_places_nearby(float(lat), float(long), response["keyword"])
        return jsonify({"type": response["location"], "locations": locations})


if __name__ == '__main__':
    # Ensure the app runs in debug mode for development to see logs
    # In production, set debug=False
    app.run(host='0.0.0.0', port=5000, debug=True) # Changed port back to 5000