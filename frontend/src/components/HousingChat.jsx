import React, { useState, useEffect, useRef } from 'react'; // Make sure useRef is imported

const API_URL = '/api/housing-chat';

function HousingChat({ initialMessage = '', onUserTyping = () => {}, onNewBotMessage = () => {}}) {
  const [messages, setMessages] = useState([]);
  const [partialData, setPartialData] = useState({});
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasSentInitial, setHasSentInitial] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null); // <--- THIS LINE WAS MISSING IN THE PREVIOUS CODE BLOCK!

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
    if (!loading && inputRef.current) { 
      inputRef.current.focus();
    }
  }, [messages]);

  useEffect(() => {
    if (initialMessage && !hasSentInitial) {
      setHasSentInitial(true);
      sendMessage(initialMessage);
      setInputMessage('');
    } else if (!initialMessage && messages.length === 0) {
      setMessages([{ type: 'bot', text: "🏠 Welcome to Google Realtor!\nWhat kind of home can I help you find today?" }]);
    }

    if (inputRef.current) {
      inputRef.current.focus();
    }

  }, [initialMessage, hasSentInitial]); // initialMessage and hasSentInitial are dependencies for the first part of this effect.

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    setMessages(prev => [...prev, { type: 'user', text: messageText }]);
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText, partial_data: partialData })
      });

      const data = await response.json();

      if (response.ok) {
        if (data.bot) {
          setMessages(prev => [...prev, { type: 'bot', text: data.bot }]);
        }
        if (data.partial_data) setPartialData(data.partial_data);

        if (data.final_data) {
          const { bedrooms, bathrooms, price, city } = data.final_data;
          let queryString = `?beds=${bedrooms}&baths=${bathrooms}&price=${price}`;
          if (city) {
            queryString += `&city=${city}`
          }

          if (typeof onNewBotMessage === 'function') {
            onNewBotMessage(`We'll start searching!${queryString}`);
          }
        }

      } else {
        setMessages(prev => [...prev, { type: 'bot', text: 'Oops! Something went wrong.' }]);
      }

    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { type: 'bot', text: 'Network error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      sendMessage(inputMessage.trim());
      setInputMessage('');
      // Optionally re-focus after sending a message for continuous typing
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  const handleInputChange = (e) => {
    if (e.target.value.length === 1) {
      onUserTyping();
    }
    setInputMessage(e.target.value);
  };

  return (
    <div className="flex flex-col w-full h-full">
      <div className="bg-white p-2 font-bold">
        🏡 Google Realtor
      </div>

      <div className="chat-messages-container">
        {messages.map((msg, i) => (
          <div key={i} className={`message-bubble ${msg.type}`}>
            {msg.text}
          </div>
        ))}
        {loading && (
          <div className="message-bubble bot typing-indicator">
            typing...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>


{/* centers the search bar. */}
      <div className="chat-input-wrapper flex justify-center p-3">
        <form onSubmit={handleSubmit} className="chat-input-form flex w-full max-w-lg items-center">
          <input
            type="text"
            ref={inputRef}
            className="flex-1 h-14 px-4 py-3 text-base border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-gray-300"
            placeholder="Search your dream home"
            value={inputMessage}
            onChange={handleInputChange}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !inputMessage.trim()}
            className="h-14 px-6 bg-blue-500 text-white font-semibold rounded-r-lg hover:bg-blue-600 disabled:opacity-50 flex items-center justify-center"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default HousingChat;