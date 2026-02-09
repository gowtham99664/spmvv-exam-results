import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FaUserCircle, FaBell, FaUsers } from 'react-icons/fa';
import NotificationBell from './NotificationBell';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!user) return null;

  const getDashboardLink = () => {
    switch(user.role) {
      case 'admin': return '/admin/dashboard';
      case 'principal': return '/principal/dashboard';
      case 'hod': return '/hod/dashboard';
      default: return '/student/dashboard';
    }
  };

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to={getDashboardLink()} className="flex items-center">
              <span className="text-xl font-bold text-primary-600">SPMVV Exam Results</span>
            </Link>

          </div>

          <div className="flex items-center space-x-4">
            {user.role === 'student' && <NotificationBell />}
            
            <div className="flex items-center space-x-2">
              <FaUserCircle className="text-gray-600 text-2xl" />
              <div className="hidden md:block">
                <p className="text-sm font-medium text-gray-700">
                  {user.role === 'admin' ? user.username : user.hall_ticket_number || user.username}
                </p>
                <p className="text-xs text-gray-500 capitalize">{user.role}</p>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="btn-secondary text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
