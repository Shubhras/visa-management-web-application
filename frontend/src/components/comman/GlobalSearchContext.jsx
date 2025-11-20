import React, { createContext, useContext, useState } from 'react';

const GlobalSearchContext = createContext();

export const useGlobalSearch = () => {
  const context = useContext(GlobalSearchContext);
  if (!context) {
    throw new Error('useGlobalSearch must be used within GlobalSearchProvider');
  }
  return context;
};

export const GlobalSearchProvider = ({ children }) => {
  const [globalSearch, setGlobalSearch] = useState('');

  // Optional: clear on route change (if needed)
  // useEffect(() => {
  //   setGlobalSearch('');
  // }, [location.pathname]);

  return (
    <GlobalSearchContext.Provider value={{ globalSearch, setGlobalSearch }}>
      {children}
    </GlobalSearchContext.Provider>
  );
};