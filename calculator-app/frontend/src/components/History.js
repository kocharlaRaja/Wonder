import React from 'react';
import '../styles/History.css'; // Create this file for history specific styles

function History({ history }) {
  return (
    <div className="history-container">
      <h2>Calculation History</h2>
      {history.length === 0 ? (
        <p>No calculations yet.</p>
      ) : (
        <ul>
          {history.map((item) => (
            <li key={item.id}>
              <span className="history-timestamp">
                {new Date(item.timestamp).toLocaleString()}
              </span>
              <span className="history-expression">{item.expression}</span>
              <span className="history-equals">=</span>
              <span className="history-result">{item.result}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default History;
