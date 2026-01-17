import React from 'react';
import { View } from '../types';
import { 
  Home, 
  BookOpen, 
  PieChart, 
  Gift, 
  Calendar, 
  LogOut 
} from 'lucide-react';

interface NavBarProps {
  currentView: View;
  onChangeView: (view: View) => void;
  onLogout: () => void;
}

export const BottomNav: React.FC<NavBarProps> = ({ currentView, onChangeView }) => {
  const navItems = [
    { view: View.HOME, icon: Home, label: 'Home' },
    { view: View.LEARN, icon: BookOpen, label: 'Learn' },
    { view: View.REWARDS, icon: Gift, label: 'Rewards' },
    { view: View.EVENTS, icon: Calendar, label: 'Events' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2 flex justify-between items-center z-50 shadow-lg pb-safe">
      {navItems.map((item) => (
        <button
          key={item.label}
          onClick={() => onChangeView(item.view)}
          className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
            currentView === item.view 
              ? 'text-teal-600 font-semibold' 
              : 'text-gray-400 hover:text-gray-600'
          }`}
        >
          <item.icon size={24} strokeWidth={currentView === item.view ? 2.5 : 2} />
          <span className="text-[10px] mt-1">{item.label}</span>
        </button>
      ))}
    </div>
  );
};

export const Header: React.FC<{ username: string; kDollars: number; onLogout: () => void }> = ({ username, kDollars, onLogout }) => (
  <header className="bg-teal-600 text-white p-4 sticky top-0 z-40 shadow-md">
    <div className="flex justify-between items-center max-w mx-auto">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 lg:w-12 lg:h-12 bg-white/20 rounded-full flex items-center justify-center font-bold">
          {username.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-sm lg:text-base xl:text-xl opacity-90">CTFLife Student</h1>
          <p className="font-bold text-lg lg:text-2xl xl:text-2xl leading-none">{username}</p>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="bg-white/10 px-3 py-1 lg:px-6 lg:py-2 rounded-full flex items-center gap-2 border border-white/20">
          <span className="text-yellow-300 font-bold text-sm lg:text-xl">K$</span>
          <span className="font-bold font-mono text-sm lg:text-xl">{kDollars}</span>
        </div>
        <button onClick={onLogout} className="text-white/80 hover:text-white">
          <LogOut size={20} />
        </button>
      </div>
    </div>
  </header>
);
