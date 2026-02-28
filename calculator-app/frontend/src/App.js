import React, { useState, useEffect } from 'react';
import Calculator from './components/Calculator';
import History from './components/History';
import './styles/App.css';

function App() {
  const [history, setHistory] = useState([]);
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/history`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error("Error fetching history:", error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleNewCalculation = () => {
    fetchHistory();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Full-Stack Calculator</h1>
      </header>
      <div className="App-content">
        <Calculator onNewCalculation={handleNewCalculation} apiBaseUrl={API_BASE_URL} />
        <History history={history} />
      </div>
    </div>
  );
}

export default App;
