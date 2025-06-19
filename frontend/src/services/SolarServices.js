// src/services/SolarService.js
import axios from 'axios';

const API_KEY = import.meta.env.VITE_API_KEY;

export async function getSolarData(lat, lng) {
  const url = `https://solar.googleapis.com/v1/buildingInsights:findClosest?location.latitude=${lat}&location.longitude=${lng}&key=${API_KEY}`;

  try {
    const response = await axios.get(url);
    return response.data;
  } catch (err) {
    console.error("Solar API error:", err);
    return null;
  }
}