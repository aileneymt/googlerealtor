import axios from "axios"

/** Base URL for the MakeRecipe API - Correspond to methods in Backend's MakeRecipeController. */
const REST_API_BASE_URL = "/api"

/** POST MakeRecipe - makes the given recipe with the given payment. Returns the change. */
export const getHouses = (beds, baths, price, city) => axios.get(REST_API_BASE_URL + "/search", {
    params: {
        beds: beds,
        baths: baths,
        price: price,
        city: city
    },
    headers: { 
        'Content-Type' : 'application/json' 
    }
})

export const getPrediction = async (
  beds, baths, square_feet, lot_size,
  year_built, property_type, latitude,
  longitude, zipcode
) => {
  try {
    const response = await axios.get(REST_API_BASE_URL + "/graph", {
      params: {
        beds,
        baths,
        square_feet,
        lot_size,
        year_built,
        property_type,
        latitude,
        longitude,
        zipcode
      },
      responseType: 'blob', // handle image data
    });

    // Create a temporary URL for the image blob
    const imageUrl = URL.createObjectURL(response.data);
    return imageUrl; //  use this as the src in an <img>
  } catch (error) {
    console.error("Prediction error:", error);
    throw error;
  }
};

export const getList = async (
   beds, baths, square_feet, lot_size,
  year_built, property_type, latitude,
  longitude, zipcode
) => {
  try {
    const response = await axios.get(REST_API_BASE_URL + "/list", {
      params: {
        beds,
        baths,
        square_feet,
        lot_size,
        year_built,
        property_type,
        latitude,
        longitude,
        zipcode
      },
      responseType: 'blob', // handle image data
    });
    // Create a temporary URL for the image blob
    const imageUrl = URL.createObjectURL(response.data);
    return imageUrl; //  use this as the src in an <img>
  } catch (error) {
    console.error("Prediction error:", error);
    throw error;
  }
};

