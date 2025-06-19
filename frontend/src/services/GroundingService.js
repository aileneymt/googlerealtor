import axios from "axios";

export const getPlacesNearby = (message, lat, lng) => {
  
  const body = {
    message : message
  };

  return axios.post("/api/search/places", body, {
    params: {
        lat: lat,
        long: lng
    },
    headers: {
      'Content-Type': 'application/json'
    }
  });
};
