import React from 'react';
import { ChatProvider } from './context/ChatContext';
import ChatWindow from './components/ChatWindow';
import HistoryPanel from './components/HistoryPanel';
import './App.css';

function App() {
  return (
    <ChatProvider>
      <div className="App">
        <HistoryPanel />
        <ChatWindow />
      </div>
    </ChatProvider>
  );
}

export default App;