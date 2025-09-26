'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import { userStorage } from '@/utils/secureStorage';
import CustomerDashboard from '@/components/dashboards/CustomerDashboard';
import DeliveryDashboard from '@/components/dashboards/DeliveryDashboard';
import OwnerDashboard from '@/components/dashboards/OwnerDashboard';
import AdminDashboard from '@/components/dashboards/AdminDashboard';
import SkeletonLoader from '@/components/SkeletonLoader';

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
      <div className="min-h-screen bg-gray-50">
        {/* Header Skeleton */}
        <div className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
            <SkeletonLoader type="text" className="h-8 w-64" />
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full skeleton-loader"></div>
                <SkeletonLoader type="text" className="h-4 w-32" />
              </div>
              <div className="w-24 h-10 skeleton-loader rounded"></div>
            </div>
          </div>
        </div>

        <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          {/* Dashboard Content Skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full skeleton-loader"></div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <SkeletonLoader type="text" className="h-4 w-3/4 mb-2" />
                      <SkeletonLoader type="text" className="h-6 w-1/2" />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <SkeletonLoader type="text" className="h-5 w-3/4 mb-4" />
                  <SkeletonLoader type="text" className="h-4 w-full mb-6" />
                  <div className="w-32 h-10 skeleton-loader rounded"></div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <SkeletonLoader type="text" className="h-5 w-48 mb-2" />
              <SkeletonLoader type="text" className="h-4 w-64" />
            </div>
            <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
              <div className="sm:divide-y sm:divide-gray-200">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <SkeletonLoader type="text" className="h-4 w-32" />
                    <div className="mt-1 sm:mt-0 sm:col-span-2">
                      <SkeletonLoader type="text" className="h-4 w-48" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
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