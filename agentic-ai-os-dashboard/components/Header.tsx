import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-cyan-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M12 6V3m0 18v-3m-6.414-9.586a7 7 0 1012.828 0m-12.828 0L3 12m18 0l-2.414-2.414" />
                </svg>
            </div>
            <div className="ml-4">
              <h1 className="text-xl font-bold text-gray-100">Agentic AI OS</h1>
              <p className="text-sm text-gray-400">System Dashboard</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
