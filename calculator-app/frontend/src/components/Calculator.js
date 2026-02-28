import React, { useState } from 'react';
import '../styles/Calculator.css'; // Create this file for calculator specific styles

function Calculator({ onNewCalculation, apiBaseUrl }) {
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');

  const handleClick = (value) => {
    if (value === '=') {
      calculateResult();
    } else if (value === 'C') {
      clearInput();
    } else {
      setInput((prevInput) => prevInput + value);
    }
  };

  const calculateResult = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ expression: input }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data.result);
      setInput(data.result); // Set input to result for chained operations
      onNewCalculation(); // Notify App.js to refresh history
    } catch (error) {
      console.error("Error calculating:", error);
      setResult(`Error: ${error.message}`);
      setInput(''); // Clear input on error
    }
  };

  const clearInput = () => {
    setInput('');
    setResult('');
  };

  const buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', '.', '=', '+',
    'C'
  ];

  return (
    <div className="calculator-container">
      <div className="calculator-display">
        <div className="calculator-input">{input || '0'}</div>
        <div className="calculator-result">{result}</div>
      </div>
      <div className="calculator-buttons">
        {buttons.map((btn) => (
          <button
            key={btn}
            onClick={() => handleClick(btn)}
            className={`button ${['+', '-', '*', '/', '=', 'C'].includes(btn) ? 'operator' : ''}`}
          >
            {btn}
          </button>
        ))}
      </div>
    </div>
  );
}

export default Calculator;
