import { useEffect, useState } from 'react';
import '../styles/PropertyCard.css';
import { useSearchParams, useNavigate } from 'react-router-dom';
import MiniHouseView from './MiniHouseView.jsx';

function HousesList({ houses, initialBeds, initialBaths, initialCity, initialPrice, setSelectedHouse }) {
  const navigate = useNavigate();
  const bedOpts = [1, 2, 3, 4, 5, 6];
  const bathOpts = [1, 2, 3, 4, 5];
  const priceOpts = [200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1250000, 1500000];
  const [search] = useSearchParams();

  const getInitialNumber = (param, fallback) => {
    const val = search.get(param);
    return val !== null && !isNaN(Number(val)) ? Number(val) : fallback;
  };

  const [beds, setBeds] = useState(getInitialNumber('beds', initialBeds || 2));
  const [baths, setBaths] = useState(getInitialNumber('baths', initialBaths || 2));
  const [price, setPrice] = useState(getInitialNumber('price', initialPrice || 600000));
  const [city, setCity] = useState(initialCity || '');

  const updateSearch = () => {
    if (city) {
      navigate(`/map?price=${price}&beds=${beds}&baths=${baths}&city=${city}`);
    } else {
      navigate(`/map?price=${price}&beds=${beds}&baths=${baths}`);
    }
  };

  return (
    <div className="house-list-card">
      <div className="search-options">
        <div className="toggles">
          <div className="option">
            <label> Beds: </label>
            <select value={beds} onChange={(e) => setBeds(Number(e.target.value))}>
              {bedOpts.map((num) => (
                <option key={num} value={num}>{num}+</option>
              ))}
            </select>
          </div>
          <div className="option">
            <label> Baths: </label>
            <select value={baths} onChange={(e) => setBaths(Number(e.target.value))}>
              {bathOpts.map((num) => (
                <option key={num} value={num}>{num}+</option>
              ))}
            </select>
          </div>
          <div className="option">
            <label> Max price: </label>
            <select value={price} onChange={(e) => setPrice(Number(e.target.value))}>
              {priceOpts.map((num) => (
                <option key={num} value={num}>${num.toLocaleString()}</option>
              ))}
            </select>
          </div>
          <div className="option">
            <label> City: </label>
            <input type="text" placeholder='Enter a city' value={city} onChange={(e) => setCity(e.target.value)} />
          </div>
          <button id="search-button" className="material-symbols-outlined" onClick={updateSearch}>search</button>
        </div>
      </div>

      <h3>All Results</h3>
      <div className="results-view">
        {houses && houses.map((house, index) => (
        <MiniHouseView
            key={house.ID || index}
            house={house}
            index={index}  // Pass the index
            setSelectedHouse={setSelectedHouse}
        />
        ))}
    </div>
    </div>
  );
}

export default HousesList;
