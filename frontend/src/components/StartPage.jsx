import React, { useState, useEffect } from 'react';
import './StartPage.css';
import { useNavigate } from "react-router-dom";
import backgroundImage from '../assets/Background.png';
import HousingChat from './HousingChat.jsx';

function StartPage({ apiKey }) {
  const navigate = useNavigate();

  const [latestBotMessage, setLatestBotMessage] = useState('');
  const [userQuery, setUserQuery] = useState('');
  const [showChatBot, setShowChatBot] = useState(false);
  const [showBubbles, setShowBubbles] = useState(true); // ✅ state to control bubble visibility

  useEffect(() => {
  if (latestBotMessage.includes("We'll start searching!")) {
    const match = latestBotMessage.match(/\?(.*)$/); // safely extract query string
    if (match) {
      const query = match[1];
      const timer = setTimeout(() => {
        navigate(`/map?${query}`);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }
}, [latestBotMessage, navigate]);

  const handleSearchClick = () => {
    setShowChatBot(true);
  };

  return (
    <div className="start-page-container">
      <header>
        <div className="header-left">Google Realtor</div>
      </header>

      <div className="map-background" style={{ backgroundImage: `url(${backgroundImage})` }}></div>

      {/* ✅ Conditional rendering of bubbles */}
      {showBubbles && (
        <div className="bubbles">
          <div className="pop-bubble" style={{ animationDelay: "0s", top: "100px", left: "400px" }}>
            <div className="query-example">
              "I want a rustic-style residential home with three bedrooms and two bathrooms within 10 miles from the Google Office."
            </div>
          </div>
          <div className="pop-bubble" style={{ animationDelay: "0.3s", top: "650px", left: "1200px" }}>
            <div className="query-example">
              "I'm interested in a craftsman style single-family home with a large backyard and at least two bedrooms."
            </div>
          </div>
          <div className="pop-bubble" style={{ animationDelay: "0.6s", top: "175px", left: "950px" }}>
            <div className="query-example">
              "Looking for a contemporary style house with four bedrooms and at least two bathrooms."
            </div>
          </div>
          <div className="pop-bubble" style={{ animationDelay: "0.9s", top: "650px", left: "200px" }}>
            <div className="query-example">
              "I want a rustic-style residential home with three bedrooms and two bathrooms in Hillsborough, NC."
            </div>
          </div>
          <div className="pop-bubble" style={{ animationDelay: "1.2s", top: "300px", left: "1400px" }}>
            <div className="query-example">
              "Looking for a newly built home with energy-efficient features under 500K."
            </div>
          </div>
          <div className="pop-bubble" style={{ animationDelay: "1.2s", top: "850px", left: "800px" }}>
            <div className="query-example">
              "I need a home in Durham with 4 bd, 3 bth, and under 700,000."
            </div>
          </div>
          <div className="pop-bubble" style={{ animationDelay: "1.2s", top: "400px", left: "90px" }}>
            <div className="query-example">
              "I want a nice 3 bedroom house in Morrisville that is under 400K."
            </div>
          </div>
        </div>
      )}

      {!showChatBot && (
        <div className="search-container center-absolute">
          <div className="google-search-box" onClick={handleSearchClick}>
            <input
              type="text"
              className="search-input"
              placeholder="Search your dream home"
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearchClick()}
            />
            <button className="search-button">
              <span className="material-symbols-outlined">search</span>
            </button>
          </div>
        </div>
      )}

      {showChatBot && (
        <div className="chat-bot center-absolute">
          <HousingChat
            onUserTyping={() => setShowBubbles(false)}
            apiKey={apiKey}
            initialMessage={userQuery}
            onNewBotMessage={setLatestBotMessage} 
          />
        </div>
      )}
    </div>
  );
}

export default StartPage;