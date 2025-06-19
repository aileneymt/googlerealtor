import React from 'react';

function RedfinLink({ house }) {
  if (!house || !house.ADDRESS || !house.CITY || !house.STATE_OR_PROVINCE) {
    return null;
  }

  const formattedAddress = house.ADDRESS
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]/g, '');

  const formattedCity = house.CITY
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-');

  const redfinUrl = `https://www.redfin.com/`;

  return (
    <a
      href={redfinUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="redfin-link"
    >
      View on Redfin →
    </a>
  );
}

export default RedfinLink;
