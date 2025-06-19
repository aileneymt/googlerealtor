

import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import MapComponent from "./components/MapComponent.jsx"
import HousingChat from './components/HousingChat.jsx';
import StartPage from "./components/StartPage.jsx"
import React from 'react';
import {BrowserRouter as Router, Routes, Route} from "react-router-dom"

function App() {
  const apiKey = import.meta.env.VITE_API_KEY
  return (
    // We'll use a flex container to arrange the map and chat side-by-side or stacked

    
    <Router> 
      <div className="app-main-layout">
        <Routes> 
          <Route path="/" element={<StartPage apiKey={apiKey} />} />
          <Route path="/map" element={<MapComponent apiKey={apiKey} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;