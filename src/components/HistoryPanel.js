import React from 'react';
import { useChat } from '../context/ChatContext';

const panelStyle = {
  width: '250px',
  padding: '20px',
  borderRight: '1px solid #ddd',
  backgroundColor: '#f7f7f7',
  display: 'flex',
  flexDirection: 'column',
};

const newChatButtonStyle = {
  padding: '10px',
  backgroundColor: '#28a745',
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
  marginBottom: '20px',
};

const historyItemStyle = {
  padding: '10px',
  cursor: 'pointer',
  borderBottom: '1px solid #eee',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
};

const HistoryPanel = () => {
  const { history, startNewChat, loadChatHistory } = useChat();

  return (
    <div style={panelStyle}>
      <button onClick={startNewChat} style={newChatButtonStyle}>
        + New Chat
      </button>
      <h3 style={{ marginTop: 0 }}>History</h3>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {history.length > 0 ? (
          history.map(chat => (
            <div
              key={chat.id}
              style={historyItemStyle}
              onClick={() => loadChatHistory(chat)}
              title={chat.messages[0]?.text}
            >
              {chat.messages[0]?.text || 'Empty Chat'}
            </div>
          ))
        ) : (
          <p>No past conversations.</p>
        )}
      </div>
    </div>
  );
};

export default HistoryPanel;