import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './shared/Sidebar';
import Header from './shared/Header';

const Layout: React.FC = () => {
  return (
    <div className="flex h-screen bg-white">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-auto bg-white relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;