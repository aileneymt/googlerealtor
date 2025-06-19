import React from "react";
import '../styles/MiniHouseView.css';
import home from '../assets/HousePicture.webp';

import home1 from '../assets/house1.png';
import home2 from '../assets/house2.png';
import home3 from '../assets/house3.png';
import home4 from '../assets/house4.png';
import home5 from '../assets/house5.png';

const MiniHouseView = ({ house, index, setSelectedHouse }) => {
    if (!house) return null;

    const handleShowMore = () => {
        setSelectedHouse(house);
    };

    const homeImages = [home1, home2, home3, home4, home5];
    const imageToShow = index < homeImages.length ? homeImages[index] : home; // fallback to default

    return (
        <div className='mini-house-view'>
            <h2 className='address'>
                {house.ADDRESS}, {house.ZIP_OR_POSTAL_CODE}, {house.CITY}, {house.STATE_OR_PROVINCE}
            </h2>
            <img src={imageToShow} alt={`Home ${index + 1}`} />
            <h1 className='price'>
                ${house.PRICE.toLocaleString()}
            </h1>
            {house.LOT_SIZE ? (
                <h3 className="property-details">
                    {house.BEDS} bed • {house.BATHS} bath • {house.SQUARE_FEET.toLocaleString()} sq ft • {house.LOT_SIZE.toLocaleString()} sq ft lot size
                </h3>
            ) : (
                <h3 className="property-details">
                    {house.BEDS} bed • {house.BATHS} bath • {house.SQUARE_FEET} sq ft
                </h3>
            )}
            <button className="more-button" onClick={handleShowMore}>
                Show More
            </button>
        </div>
    );
};

export default MiniHouseView;
