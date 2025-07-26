import React, { useState } from 'react';

const formStyle = {
  display: 'flex',
  padding: '10px',
  borderTop: '1px solid #ddd',
};

const inputStyle = {
  flex: 1,
  padding: '10px',
  borderRadius: '20px',
  border: '1px solid #ccc',
  marginRight: '10px',
};

const buttonStyle = {
  padding: '10px 20px',
  borderRadius: '20px',
  border: 'none',
  backgroundColor: '#007bff',
  color: 'white',
  cursor: 'pointer',
};

const UserInput = ({ onSendMessage, disabled }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <input
        type="text"
        style={inputStyle}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Type a message..."
        disabled={disabled}
      />
      <button type="submit" style={buttonStyle} disabled={disabled}>
        Send
      </button>
    </form>
  );
};

export default UserInput;