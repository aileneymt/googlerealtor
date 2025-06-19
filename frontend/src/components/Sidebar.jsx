import { useState, useEffect } from 'react';
import axios from 'axios';
import PropertyCard from './PropertyCard.jsx';

function Sidebar() {
    const [houses, setHouses] = useState([]);

    useEffect(() => {
        axios.get('/api/search', {
            // change this later so that it directly takes in the returned json string from gemini
            params: {
                city: 'Durham',
                price: 600,
                beds: 4,
                baths: 2
            }
        })
        .then(res =>{
            setHouses(res.data.houses);
        })
        .catch(err => console.error(err));
    }, []);
    return (
        <div style={{ overflowY: 'scroll', maxHeight: '100vh' }}>
      {houses.map((house, i) => (
        <PropertyCard key={i} property={house} />
      ))}
    </div>
    );
}

export default Sidebar;