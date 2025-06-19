import React, { useEffect, useState, useRef } from 'react';
import '../styles/PropertyCard.css';
import {getPrediction} from '../services/MapService.js' //import map service
import {getList} from '../services/MapService.js'
import houseImg from '../assets/HousePicture.webp'; // import image of house
import mockGraph from '../assets/mock-graph.jpg'; // placeholder mock graph for now
import RedfinLink from './RedfinLink.jsx';

import { GoogleMap, Marker, LoadScript, StreetViewPanorama, InfoWindow } from '@react-google-maps/api';
import { getPlacesNearby } from '../services/GroundingService';
import Demographics from './Demographics.jsx';
import { getSolarData } from '../services/SolarServices';
// Define the API endpoint for getting property descriptions
const GET_DESCRIPTION_API_URL = '/api/get-description'; // Ensure this matches your Flask backend

function PropertyCard({mapRef, house, markersRef, placesNearby}) {
    const containerStyle = {
        width: '100%',
        height: '250px',
    };

    const center = {
        lat: house.LATITUDE,
        lng: house.LONGITUDE,
    };

    const [panoPos, setPanoPos] = useState(null);
    const [heading, setHeading] = useState(0);
    const [hasStreetView, setHasStreetView] = useState(false);
    const [botMessage, setBotMessage] = useState("");
    const [search, setSearch] = useState("");
    const [hoveredPlace, setHoveredPlace] = useState(null);
    const [infoWindowPos, setInfoWindowPos] = useState(null);
    const infoWindowRef = useRef(null);
    const [solarData, setSolarData] = useState(null);
    const [graphUrl, setGraphUrl] = useState(null);

    const [propertyDescription, setPropertyDescription] = useState("Loading property description...");

    const [buttonText, setButtonText] = useState("Switch Format");

     

    // This function seems to be a prop setter, but it's defined locally.
    // If placesNearby is meant to be updated in the parent, this should be a prop function.
    // For now, it's not directly affecting the rendering of places in this component.
    const setPlacesNearby = (places) => {
        // This function is not updating the placesNearby prop directly.
        // It's likely intended to update a state in the parent component.
        // For local display, you might need a useState for placesNearby inside PropertyCard too.
        // For this example, we'll assume the markersRef handles the map display.
        console.log("setPlacesNearby called with:", places);
    };

    const handleClick = () => {
        if(buttonText == "Switch Back") {
            getPrediction(house.BEDS, house.BATHS, house.SQUARE_FEET, house.LOT_SIZE, house.YEAR_BUILT, house.PROPERTY_TYPE, house.LATITUDE, house.LONGITUDE, house.ZIP_OR_POSTAL_CODE)
            .then(imgURL => {
                setGraphUrl(imgURL)
            })
            setButtonText("Switch Format")
        }
        else {
            getList(house.BEDS, house.BATHS, house.SQUARE_FEET, house.LOT_SIZE, house.YEAR_BUILT, house.PROPERTY_TYPE, house.LATITUDE, house.LONGITUDE, house.ZIP_OR_POSTAL_CODE)
            .then(imgURL => {
                setGraphUrl(imgURL)
            })
            setButtonText("Switch Back")
        }
    };
    
    

    function computeHeading(fromLat, fromLng, toLat, toLng) {
        const dLng = (toLng - fromLng) * Math.PI / 180;
        const fromLatRad = fromLat * Math.PI / 180;
        const toLatRad = toLat * Math.PI / 180;
    
        const y = Math.sin(dLng) * Math.cos(toLatRad);
        const x = Math.cos(fromLatRad) * Math.sin(toLatRad) -
                  Math.sin(fromLatRad) * Math.cos(toLatRad) * Math.cos(dLng);
        let heading = Math.atan2(y, x) * 180 / Math.PI;
        return (heading + 360) % 360;
    }

    // Effect to fetch prediction graph and property description when house changes
    useEffect(() => {
        // Clear existing markers and messages when house changes
        markersRef.current.forEach(marker => marker.setMap(null));
        markersRef.current = [];

        setBotMessage("");
        setPropertyDescription("Loading property description..."); // Reset description on new house

        // Fetch prediction graph
       
        if(buttonText == "Switch Format") {
            getPrediction(house.BEDS, house.BATHS, house.SQUARE_FEET, house.LOT_SIZE, house.YEAR_BUILT, house.PROPERTY_TYPE, house.LATITUDE, house.LONGITUDE, house.ZIP_OR_POSTAL_CODE)

            .then(imgURL => {
                setGraphUrl(imgURL);
            })
            .catch(error => {
                console.error("Error fetching prediction graph:", error);
                setGraphUrl(mockGraph); // Fallback to mock graph on error
            });
        }
        else {
            getList(house.BEDS, house.BATHS, house.SQUARE_FEET, house.LOT_SIZE, house.YEAR_BUILT, house.PROPERTY_TYPE, house.LATITUDE, house.LONGITUDE, house.ZIP_OR_POSTAL_CODE)
            .then(imgURL => {
                setGraphUrl(imgURL)
            })
        }

        // Fetch dynamic property description
        const fetchPropertyDescription = async () => {
            const address = `${house.ADDRESS}, ${house.CITY}, ${house.STATE_OR_PROVINCE}`;
            try {
                const response = await fetch(GET_DESCRIPTION_API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ address: address })
                });
                const data = await response.json();
                if (response.ok && data.description) {
                    setPropertyDescription(data.description);
                } else {
                    console.error("Failed to get description:", data.error || "Unknown error");
                    setPropertyDescription("Description not available. This property offers a unique opportunity in a great neighborhood!");
                }
            } catch (error) {
                console.error("Network error fetching description:", error);
                setPropertyDescription("Description not available. This property offers a unique opportunity in a great neighborhood!");
            }
        };

        fetchPropertyDescription();

    }, [house]); // Re-run this effect whenever the 'house' prop changes

    useEffect(() => {
        if (window.google && !infoWindowRef.current) {
            infoWindowRef.current = new window.google.maps.InfoWindow();
        }
    }, []);

    useEffect(() => {
        if (!window.google) return;

        const streetViewService = new window.google.maps.StreetViewService();

        streetViewService.getPanorama(
            { location: { lat: center.lat, lng: center.lng }, radius: 300 },
            (data, status) => {
                if (status === window.google.maps.StreetViewStatus.OK) {
                    const panoLat = data.location.latLng.lat();
                    const panoLng = data.location.latLng.lng();
                    setHasStreetView(true);
                    setPanoPos({ lat: panoLat, lng: panoLng });
                    setHeading(computeHeading(panoLat, panoLng, center.lat, center.lng));
                } else {
                    console.log("No Street View panorama found nearby.");
                    setHasStreetView(false); // Explicitly set to false if not found
                    setPanoPos({ lat: center.lat, lng: center.lng }); // Fallback position
                    setHeading(0);
                }
            }
        );
    }, [center.lat, center.lng]);

    useEffect(() => {
        async function fetchSolar() {
            const data = await getSolarData(house.LATITUDE, house.LONGITUDE);
            console.log("🔆 Solar API Response:", data);
            if (data) {
                setSolarData(data);
            } else {
                console.log("No solar data available.");
            }
        }

        fetchSolar();
    }, [house.LATITUDE, house.LONGITUDE]);

    const handleNearbySearch = (searchKeyword) => { // Renamed 'search' to 'searchKeyword' to avoid conflict with state
        setPlacesNearby([]); // This clears the parent's placesNearby if it's a state setter
        markersRef.current.forEach(marker => marker.setMap(null));
        markersRef.current = [];
        console.log("Searching for places nearby:", searchKeyword);
        getPlacesNearby(searchKeyword, house.LATITUDE, house.LONGITUDE).then(response => {
            if (response.data.message) {
                setBotMessage(response.data.message)
                return
            }

            if (response.data.locations.length == 0) {
                setBotMessage(`No ${response.data.type} were found near you.`)
            }
            else  {
                setBotMessage(`Found ${response.data.locations.length} ${response.data.type} nearby!`)
                
            }
            setPlacesNearby(response.data.locations)
            


            console.log(placesNearby)
            console.log("mapRef.current: ")
            console.log(mapRef)
            if (mapRef.current) {
                
                response.data.locations.forEach(loc => {
                    const marker = new window.google.maps.Marker({
                        position: { lat: loc.geometry.location.lat, lng: loc.geometry.location.lng},
                        map: mapRef.current,
                        title: loc.name || searchKeyword,
                        icon: {
                            url: 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png', // A generic blue dot icon
                        }
                    });

                    marker.addListener("mouseover", () => {
                        const content = `
                            <div>
                                <strong>${loc.name}</strong><br/>
                                Rating: ${loc.rating ?? "N/A"}<i class="material-icons" style="color: #FFC107; vertical-align: middle; font-size: 16px">star</i>
                            </div>
                        `;
                        infoWindowRef.current.setContent(content);
                        infoWindowRef.current.open(mapRef.current, marker);
                    });

                    marker.addListener("mouseout", () => {
                        infoWindowRef.current.close();
                    });
                    markersRef.current.push(marker);
                });
                mapRef.current.setZoom(14);
            }
        }).catch(err => {
            console.log("Failed to fetch nearby", search)
            setBotMessage("Unable to find locations nearby that meet your search.")
        })
    }

    return (
        <div className="property-card">
            <h1 className="property-address">{house.ADDRESS}, {house["ZIP_OR_POSTAL_CODE"]}, {house.CITY}, {house["STATE_OR_PROVINCE"]}</h1>
            <div className="container">
                {hasStreetView ? (
                    <GoogleMap className="street-view" mapContainerStyle={containerStyle} center={center} zoom={14}>
                        <StreetViewPanorama position={panoPos}
                            visible={true}
                            options={{
                                pov: { heading, pitch: 0 },
                                zoom: 1,
                                panControl: true,
                                zoomControl: true,
                                addressControl: false,
                                disableDefaultUI: true,
                                linksControl: false,
                                enableCloseButton: false
                            }}
                            style={containerStyle}
                        />
                    </GoogleMap>
                ) : (
                    <div>
                        No street view available.
                    </div>
                )}
            </div>

            <h1 className="property-price">${house.PRICE.toLocaleString()}</h1>

            {
                house["LOT_SIZE"] && <h3 className="property-details">{house.BEDS} bed • {house.BATHS} bath • {house["SQUARE_FEET"].toLocaleString()} sq ft • {house["LOT_SIZE"].toLocaleString()} sq ft lot size</h3>
            }
            {
                house["LOT_SIZE"] == null && <h3 className="property-details">{house.BEDS} bed • {house.BATHS} bath • {house["SQUARE_FEET"]} sq ft </h3>
            }
            {/* Dynamic Property Description */}
            <p className="property-desc">{propertyDescription}</p>

            <div className="property-icons">
                <p>🏠 {house["PROPERTY_TYPE"]}</p>
                {house["HOA_PER_MONTH"] &&
                    <p>💲${house["HOA_PER_MONTH"]}/month HOA</p>
                }
            </div>

            <div className="nearby-search">
                <h2 className="subsection">Search Nearby</h2>
                <div className="search-input">
                    <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search for places near you" />
                    <button onClick={() => { handleNearbySearch(search); setSearch(""); }}>🔍</button>
                </div>
                <div>{botMessage}</div>
                <div className="tag-grid">
                    {[
                        "Schools", "Parks", "Restaurants", "Malls", "Bars",
                        "Hospitals", "Libraries", "Grocery Stores", "daycares"
                    ].map((tag) => (
                        <button className="placesButton" key={tag} onClick={() => handleNearbySearch(tag)}>
                            {tag}
                        </button>
                    ))}
                </div>
            </div>
            <div className="future-predictions">
                <h2 className="subsection">Future Predictions</h2>
                <h3>Projected Value of Home in 5 Years</h3>
                <img className="graph" src={graphUrl || mockGraph} alt="Price Prediction Graph"></img> {/* Added alt text and fallback */}
            </div>
            
    
            <div className = "tag-grid button" style={{ justifyContent: 'center', alignItems: 'center'}}>
                <button className = "temp" onClick={handleClick}>
                    {buttonText}
                </button>
            </div> 

            <div className="demographics-section">
                <h2 className="subsection">Demographics for ZIP Code: {house["ZIP_OR_POSTAL_CODE"]}</h2>
                <Demographics zip={house["ZIP_OR_POSTAL_CODE"]?.toString().padStart(5, '0')} />
            </div>
            
    
            <div className="solar-info">
                <h2 className="subsection">Solar Potential</h2>
                    {solarData?.solarPotential ? (
                <>
                <p><strong>Solar Panel Area:</strong> {solarData.solarPotential.maxArrayAreaMeters2?.toFixed(2) ?? "N/A"} m²</p>
                <p><strong>Max Sunshine Hours/Year:</strong> {solarData.solarPotential.maxSunshineHoursPerYear ?? "N/A"} hrs</p>
                <p><strong>Carbon Offset:</strong> {solarData.solarPotential.carbonOffsetFactorKgPerMwh ?? "N/A"} kg CO₂/MWh</p>

                <h3>💸 Financial Analysis</h3>
                {solarData.solarPotential.financialAnalyses?.length > 0 ? (() => {
                const middleIndex = Math.floor(solarData.solarPotential.financialAnalyses.length / 2);
                const entry = solarData.solarPotential.financialAnalyses[middleIndex];

        return (
            <div style={{ border: "1px solid #ccc", marginBottom: "12px", padding: "8px", borderRadius: "6px" }}>
                <p><strong>Bill: </strong>${entry.monthlyBill?.units ?? "?"}/mo</p>

                {entry.financialDetails && (
                <>
                    <p><strong>Solar % Offset:</strong> {entry.financialDetails.solarPercentage?.toFixed(2) ?? "?"}%</p>
                    <p>
                        <strong>Annual Electricity Cost (No Solar):</strong> $
                        {entry.financialDetails.costOfElectricityWithoutSolar?.units
                            ? (entry.financialDetails.costOfElectricityWithoutSolar.units / 20).toFixed(2)
                            : "N/A"}
                    </p>
                    <p><strong>Remaining Utility Bill (w/ Solar):</strong> ${entry.financialDetails.remainingLifetimeUtilityBill?.units ?? "N/A"}</p>
                </>
                )}

                {entry.cashPurchaseSavings && (
                <>
                    <p><strong>💵 Cash Savings:</strong></p>
                    <ul>
                        <li><strong>Upfront Cost:</strong> ${entry.cashPurchaseSavings.upfrontCost?.units ?? "?"}</li>
                        <li><strong>Year 1 Savings:</strong> ${entry.cashPurchaseSavings.savings?.savingsYear1?.units ?? "?"}</li>
                        <li><strong>Lifetime Savings:</strong> ${entry.cashPurchaseSavings.savings?.savingsLifetime?.units ?? "?"}</li>
                        <li><strong>Payback Years:</strong> {entry.cashPurchaseSavings.paybackYears ?? "?"}</li>
                    </ul>
                </>
                )}
                </div>
        );
            })() : (
                <p>No financial analysis available for this property.</p>
            )}
            </>
            ) : (
                <p>Loading solar data...</p>
            )}
            </div>

            <div className="redfin-section">
                <h2 className="subsection">Interested in Buying?</h2>
                <RedfinLink house={house} />
            </div>
            <div className="durham-events"> 
                <h2 className="subsection">Events in the Area</h2>
                <a href="https://downtowndurham.com/downtown-events/" target="_blank">Downtown Durham →</a>
                <br></br>
                <a href="https://www.discoverdurham.com/events/annual-events/" target="_blank">Discover Durham →</a>

            </div>
            <h2>____</h2>
    </div>
    );
}

export default PropertyCard;
