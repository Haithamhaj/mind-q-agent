import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './shared/Sidebar';
import Header from './shared/Header';

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-white">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-auto bg-white relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;