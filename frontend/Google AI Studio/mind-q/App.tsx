import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';
import SearchPage from './pages/SearchPage';
import GraphPage from './pages/GraphPage';
import SettingsPage from './pages/SettingsPage';

const App: React.FC = () => {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ChatPage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="graph" element={<GraphPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </HashRouter>
  );
};

export default App;