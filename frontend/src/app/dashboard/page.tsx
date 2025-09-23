'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import { userStorage } from '@/utils/secureStorage';
import CustomerDashboard from '@/components/dashboards/CustomerDashboard';
import DeliveryDashboard from '@/components/dashboards/DeliveryDashboard';
import OwnerDashboard from '@/components/dashboards/OwnerDashboard';
import AdminDashboard from '@/components/dashboards/AdminDashboard';

interface User {
  uid: string;
  email?: string;
  phone_number?: string;
  display_name?: string;
  photo_url?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    console.log('🏠 Dashboard loaded, fetching current user...');

    const fetchUser = async () => {
      try {
        // Try to get user from secure storage first
        const cachedUser = userStorage.getUser();
        if (cachedUser) {
          console.log('📦 Using cached user data:', cachedUser);
          setUser(cachedUser);
        }

        console.log('📡 Calling /auth/me endpoint...');
        const response = await authAPI.getCurrentUser();
        console.log('✅ User data received:', response.data);

        // Store user data securely
        userStorage.setUser(response.data);
        setUser(response.data);
      } catch (error: any) {
        console.error('❌ Failed to fetch user:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data
        });

        // Clear any cached user data
        userStorage.removeUser();

        console.log('🔄 Redirecting to login page...');
        router.push('/');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = async () => {
    try {
      console.log('🚀 Starting logout process...');
      const response = await authAPI.logout();
      console.log('✅ Logout successful:', response.data);

      // Clear all secure storage
      userStorage.removeUser();

      console.log('🔄 Redirecting to login page...');
      router.push('/');
    } catch (error: any) {
      console.error('❌ Logout error:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });

      // Clear storage even if logout fails
      userStorage.removeUser();

      // Still redirect even if logout fails
      router.push('/');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-xl text-gray-600">Loading your dashboard...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-xl text-red-600 mb-4">Unable to load user data</div>
          <button
            onClick={() => router.push('/')}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Return to Login
          </button>
        </div>
      </div>
    );
  }

  // Role-based dashboard rendering
  const renderDashboard = () => {
    console.log('🎭 Rendering dashboard for role:', user.role);

    switch (user.role.toLowerCase()) {
      case 'customer':
        return <CustomerDashboard user={user} onLogout={handleLogout} />;

      case 'delivery_guy':
        return <DeliveryDashboard user={user} onLogout={handleLogout} />;

      case 'owner':
        return <OwnerDashboard user={user} onLogout={handleLogout} />;

      case 'admin':
        return <AdminDashboard user={user} onLogout={handleLogout} />;

      default:
        console.warn('⚠️ Unknown user role:', user.role);
        // Default to customer dashboard for unknown roles
        return <CustomerDashboard user={user} onLogout={handleLogout} />;
    }
  };

  return renderDashboard();
}