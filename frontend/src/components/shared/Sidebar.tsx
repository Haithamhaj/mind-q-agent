import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, Folder, Search, Network, Settings, Box, X } from 'lucide-react';
import { cn } from '../../lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navItems = [
    { icon: MessageSquare, label: 'Chat', path: '/' },
    { icon: Folder, label: 'Library', path: '/documents' },
    { icon: Search, label: 'Search', path: '/search' },
    { icon: Network, label: 'Graph', path: '/graph' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Content */}
      <aside
        className={cn(
          "bg-zinc-50 border-r border-zinc-200 flex flex-col h-screen transition-transform duration-300 ease-in-out z-50",
          "fixed inset-y-0 left-0 w-64 md:relative md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="h-16 flex items-center justify-between px-6 border-b border-zinc-200 bg-white">
          <div className="flex items-center">
            <Box className="w-6 h-6 text-blue-600 mr-2" />
            <span className="text-lg font-bold text-zinc-900 tracking-tight">Mind-Q</span>
          </div>
          <button onClick={onClose} className="md:hidden text-zinc-500 hover:bg-zinc-100 p-1 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => {
                // Close sidebar on navigation on mobile
                if (window.innerWidth < 768) {
                  onClose();
                }
              }}
              className={({ isActive }) =>
                cn(
                  "flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors group",
                  isActive
                    ? "bg-blue-50 text-blue-700"
                    : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                )
              }
            >
              <item.icon className={cn("w-5 h-5 mr-3 opacity-70 group-hover:opacity-100")} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-zinc-200 bg-zinc-50">
          <div className="bg-white p-3 rounded-lg border border-zinc-200 shadow-sm">
            <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">Storage Used</p>
            <div className="w-full bg-zinc-100 rounded-full h-1.5 mb-2">
              <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: '35%' }}></div>
            </div>
            <p className="text-xs text-zinc-400">1.2 GB of 5 GB</p>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;