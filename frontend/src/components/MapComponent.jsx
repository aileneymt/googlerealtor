import React, { useEffect, useState, useCallback, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import {getHouses} from "../services/MapService.js";
import { GoogleMap, Marker, useJsApiLoader , InfoWindow, HeatmapLayerF} from "@react-google-maps/api";

import "../styles/MapComponent.css";
import PropertyCard from "./PropertyCard.jsx";
import HousesList from "./HousesListComponent.jsx";

const containerStyle = {
  width: "100%",
  height: "100%",
};

const MapComponent = ({
  apiKey,
  initialLat = 35.9940,
  initialLng = -78.8986,
}) => {
  const [houses, setHouses] = useState([]);
  const [search] = useSearchParams();
  const beds = Number(search.get("beds")) || 2;
  const baths = Number(search.get("baths")) || 2;
  const price = Number(search.get("price")) || 600000;
  const city = search.get("city");

  const [showHeatmap, setShowHeatmap] = useState(false);
  


  const [selectedHouse, setSelectedHouse] = useState(null);
  const [zoom, setZoom] = useState(13);
  const [center, setCenter] = useState({ lat: initialLat, lng: initialLng });

  const [boundedZoom, setBoundedZoom] = useState(13);
  const [boundedCenter, setBoundedCenter] = useState({ lat: initialLat, lng: initialLng });

  
  const [placesNearby, setPlacesNearby] = useState([])
  
  const markersRef = useRef([])

  const [hoveredHouse, setHoveredHouse] = useState(null);
  const hoverTimerRef = useRef(null)

const [heatmap, setHeatmap] = useState(null);
  const [geoData, setGeoData] = useState(null);
  const redGradient = [
  "rgba(0, 255, 0, 0)",     // Bright green
  "rgba(255, 255, 0, 0.4)",    // Bright yellow (lowest intensity)
  "rgba(255, 200, 0, 0.6)",    // Yellow-orange
  "rgba(255, 150, 0, 0.8)",    // Orange
  "rgba(255, 100, 0, 0.9)",    // Orange-red
  "rgba(255, 50, 0, 1)",       // Red-orange
  "rgba(255, 0, 0, 1)"      // Bright red
];

  
  const mapRef = useRef(null)

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: apiKey,
    libraries:['visualization']
  });

  useEffect(() => {
  if (!isLoaded || !mapRef.current || !geoData) return;

  if (showHeatmap) {
    const newHeatmap = new window.google.maps.visualization.HeatmapLayer({
      data: geoData,
      map: mapRef.current,
      radius: 30,
      opacity: 0.8,
      gradient: redGradient,
      maxIntensity: 70,
      dissipating: true
    });
    setHeatmap(newHeatmap);
  } else {
    if (heatmap) {
      heatmap.setMap(null);
      setHeatmap(null);
    }
  }

  return () => {
    if (heatmap) {
      heatmap.setMap(null);
    }
  };
}, [showHeatmap, isLoaded, geoData]);

  useEffect(() => {
    const cached = localStorage.getItem("geoData")
    if (cached && isLoaded) {
        setGeoData(JSON.parse(cached).map(
        coords => new window.google.maps.LatLng(coords.lat, coords.lng)
      ));
      return;
    }

    const fetchGeoJSON = async () => {
      try {
        const response = await fetch("DPD_Violent_Crime2025Geocoded.geojson")
        const data = await response.json()
        const points = data.features
          .map((feature) => {
            const coords = feature.geometry?.coordinates;
            if (coords && coords.length === 2) {
              return new window.google.maps.LatLng(coords[1], coords[0]); // [lat, lng]
            }
            return null;
          })
          .filter(Boolean);
        localStorage.setItem("geoData", JSON.stringify(
          points.map(p => ({ lat: p.lat(), lng: p.lng() }))
        ));
        setGeoData(points);
      } catch (err) {
        console.error("Can't load GeoJSON", err)
      }
    }
    if (isLoaded) {
      fetchGeoJSON()
    }
  }, [isLoaded])

  useEffect(() => {
    if (mapRef.current && houses?.length > 0) {
      const bounds = new window.google.maps.LatLngBounds();

      houses.forEach(house => {
        bounds.extend({
          lat: Number(house.LATITUDE),
          lng: Number(house.LONGITUDE),
        })
      })

      mapRef.current.fitBounds(bounds); 
      window.google.maps.event.addListenerOnce(mapRef.current, "idle", () => {
        const center = mapRef.current.getCenter();
        const zoom = mapRef.current.getZoom() < 12 ? 11.5 : mapRef.current.getZoom();

        const updatedCenter = {
          lat: center.lat(),
          lng: center.lng(),
        };

        setBoundedCenter(updatedCenter);
        setBoundedZoom(zoom);

        // Optional: update current view too
        setCenter(updatedCenter);
        setZoom(zoom);

        console.log("New boundedCenter after search:", updatedCenter);
        console.log("New boundedZoom after search:", zoom);
    });
    }
  }, [houses])


  useEffect(() => {
    getHouses(beds, baths, price, city)
      .then((response) => {
        setHouses(response.data.houses);
      })
      .catch((err) => {
        console.error("Error fetching houses: " + err.message);
      });
  }, [beds, baths, price, city]);

  const onMarkerClick = useCallback((house) => {
    setSelectedHouse(house);
    setCenter({ lat: Number(house.LATITUDE), lng: Number(house.LONGITUDE) });
    setZoom(17);

  }, []);

  const resetMapDisplay = () => {
    if (mapRef.current) {
      mapRef.current.setZoom(boundedZoom);
      mapRef.current.setCenter(boundedCenter);
    }
    setZoom(boundedZoom)
    setCenter(boundedCenter)

    setSelectedHouse(null)
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];
  }

  if (loadError) return <div>Error loading maps</div>;
  if (!isLoaded) return <div>Loading Map...</div>;

return (
  <div style={{ position: "fixed", width: "100%", height: "100%" }}>
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={center}
      zoom={zoom}
      
      options={{
        zoomControl: true,
        draggable: true,
        scrollwheel: true,
        mapTypeControl: false,
        styles: [
          {
            featureType: "poi",
            stylers: [{ visibility: "off" }]
          },
          {
            featureType: "transit",
            stylers: [{ visibility: "off" }]
          }
        ]
      }}
      
      onClick={() => setSelectedHouse(null)}
      onLoad={map => {
        mapRef.current = map; // store map instance

        if (houses.length === 0) return;

        const bounds = new window.google.maps.LatLngBounds();

        houses.forEach(house => {
          bounds.extend({
            lat: Number(house.LATITUDE),
            lng: Number(house.LONGITUDE),
          });
        });

        map.fitBounds(bounds);

        window.google.maps.event.addListenerOnce(map, "idle", () => {
          const newCenter = map.getCenter();
          const newZoom = map.getZoom();

           const updatedCenter = {
              lat: newCenter.lat(),
              lng: newCenter.lng(),
            };

            setBoundedCenter(updatedCenter);
            setBoundedZoom(newZoom);

            setZoom(newZoom);         
            setCenter(updatedCenter);

            console.log("bounded zoom fr", newZoom,)
            console.log("bounded center fr  :", updatedCenter)
        });
        
      }}
    >
      {/* {geoData?.length> 0 && showHeatmap && (
        <HeatmapLayerF
          ref={heatmapLayerRef}
          data={geoData}
          options={{
            radius: 30,
            opacity: 0.8,
            gradient: redGradient,
            maxIntensity: 70,
            dissipating: true
          }}
        />
      )} */}

      {houses.map((house, index) => (
        <Marker
          key={index}
          position={{
            lat: Number(house.LATITUDE),
            lng: Number(house.LONGITUDE),
          }}
          onClick={() => onMarkerClick(house)}
          onMouseOver={() => {
            clearTimeout(hoverTimerRef.current);
            setHoveredHouse(house);
          }}
          onMouseOut={() => {
            hoverTimerRef.current = setTimeout(() => {
              setHoveredHouse(null);
            }, 300); // slight delay
          }}
          icon={{
            url:
              selectedHouse?.ID === house.ID
                ? "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
                : "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
            scaledSize: new window.google.maps.Size(40, 40),
          }}
        />
      ))}

      {hoveredHouse && (
  <InfoWindow
  
    position={{
      lat: Number(hoveredHouse.LATITUDE),
      lng: Number(hoveredHouse.LONGITUDE),
    }}
    options={{
    pixelOffset: new window.google.maps.Size(0, -40), // 40px above the pin
  }}
    onCloseClick={() => setHoveredHouse(null)}
  >
    <div
      onMouseEnter={() => clearTimeout(hoverTimerRef.current)}
      onMouseLeave={() => {
        hoverTimerRef.current = setTimeout(() => {
          setHoveredHouse(null);
        }, 300);
      }}
    >
      <strong>{hoveredHouse.ADDRESS}</strong>
      <br />
      {hoveredHouse.PRICE && (
        <span>${hoveredHouse.PRICE.toLocaleString()}</span>
      )}
    </div>
  </InfoWindow>
)}
    </GoogleMap>
    <button
        style={{
          position: "absolute",
          top: "50px", // Below the recenter button
          left: "10px",
          zIndex: 10,
          padding: "5px 10px",
          backgroundColor: showHeatmap ? "#ff6b6b" : "#ED9A20",
          color: "white",
          border: "none",
          borderRadius: "10px",
          cursor: "pointer",
          boxShadow: "2px 2px 6px rgba(0, 0, 0, 0.3)",
        }}
        onClick={() => {
          // if (showHeatmap && heatmapLayerRef.current) {
          //   console.log("Hiding heatmap")
          //   heatmapLayerRef.current.setMap(null)
          // }
          // console.log("setting heatmap:", !showHeatmap)
          setShowHeatmap(!showHeatmap)
          
        }}
      >
        {showHeatmap ? "Hide Violent Crime Heatmap" : "Show Violent Crime Heatmap"}
      </button>

    <button
          style={{
            position: "absolute",
            top: "10px",
            left: "10px",
            zIndex: 10,
            padding: "5px 10px",
            backgroundColor: "white",
            borderRadius: "10px",
            cursor: "pointer",
            boxShadow: "2px 2px 6px rgba(0, 0, 0, 0.3)",
          }}
          onClick={() => resetMapDisplay()}
        >
          Recenter Map
        </button>

    {selectedHouse ? (
      <div className="container">
        
        <div className="sidebar">
          <PropertyCard mapRef={mapRef}apiKey={apiKey} house={selectedHouse} markersRef={markersRef} placesNearby={placesNearby} />
        </div>
      </div>
    ) : (
   <div className="container">
      
      <div className="sidebar">
        <HousesList houses={houses} beds={beds} baths={baths} city={city} price={price} setSelectedHouse={onMarkerClick}></HousesList>
      </div>
    </div>
    

    ) 
    }
  </div>
);
};

export default React.memo(MapComponent);
