import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import ToastContainer from '../ToastContainer';
import { useSimulation } from '../../hooks/useSimulation';

export default function Layout() {
  useSimulation(); // drives live data updates

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <Header />
        <div className="page-content">
          <Outlet />
        </div>
      </div>
      <ToastContainer />
    </div>
  );
}
