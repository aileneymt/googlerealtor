import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Demographics = ({ zip }) => {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

const fetchDemographics = async () => {
  try {
    const response = await axios.get(
      `https://api.census.gov/data/2023/acs/acs5`,
      {
        params: {
          get: `NAME,B01003_001E,B19013_001E,B01002_001E,B02001_002E,B02001_003E,B02001_004E,B02001_005E,B02001_006E,B02001_007E,B02001_008E`,
          for: `zip code tabulation area:${zip}`,
          key: '2df3d37139f46bbb5d20365dcc0138d4e9a6091d'
        }
      }
    );
    const [headers, values] = response.data;
    const result = Object.fromEntries(headers.map((h, i) => [h, values[i]]));
    setData(result);
    setError('');
  } catch (err) {
    console.error('Census API error:', err); // <-- Add for debugging
    setError('Failed to fetch data. Please check the ZIP code or try again.');
    setData(null);
  }
};

useEffect(() => {
  console.log("ZIP received in Demographics:", zip); // 🔍 Debug line
  if (zip && zip.length === 5) {
    fetchDemographics();
  }
}, [zip]);

  return (
    <div className="demographics">
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {data && (
        <div>
          <p><strong>Total Population:</strong> {Number(data.B01003_001E).toLocaleString()}</p>
          <p><strong>Median Household Income:</strong> ${Number(data.B19013_001E).toLocaleString()}</p>
          <p><strong>Median Age:</strong> {data.B01002_001E}</p>

        <h4>Race Breakdown (as % of population)</h4>
        <ul>
            <li><strong>White:</strong> {(+data.B02001_002E / +data.B01003_001E * 100).toFixed(2)}%</li>
            <li><strong>Black or African American:</strong> {(+data.B02001_003E / +data.B01003_001E * 100).toFixed(2)}%</li>
            <li><strong>American Indian/Alaska Native:</strong> {(+data.B02001_004E / +data.B01003_001E * 100).toFixed(2)}%</li>
            <li><strong>Asian:</strong> {(+data.B02001_005E / +data.B01003_001E * 100).toFixed(2)}%</li>
            <li><strong>Native Hawaiian/Pacific Islander:</strong> {(+data.B02001_006E / +data.B01003_001E * 100).toFixed(2)}%</li>
            <li><strong>Other race:</strong> {(+data.B02001_007E / +data.B01003_001E * 100).toFixed(2)}%</li>
            <li><strong>Two or more races:</strong> {(+data.B02001_008E / +data.B01003_001E * 100).toFixed(2)}%</li>
            </ul>
        </div>
      )}
    </div>
  );
};

export default Demographics;