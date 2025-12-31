import { Outlet } from 'react-router-dom';
import { AppProvider } from '../../contexts/AppContext';
import Sidebar from './Sidebar';

const MainLayout = () => {
  return (
    <AppProvider>
      <div className="app-layout">
        <Sidebar />
        <div className="main-content">
          <Outlet />
        </div>
      </div>
    </AppProvider>
  );
};

export default MainLayout;

