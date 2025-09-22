'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';

interface User {
  uid: string;
  email?: string;
  phone_number?: string;
  display_name?: string;
  photo_url?: string;
}

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    console.log('🏠 Dashboard loaded, fetching current user...');

    const fetchUser = async () => {
      try {
        console.log('📡 Calling /auth/me endpoint...');
        const response = await authAPI.getCurrentUser();
        console.log('✅ User data received:', response.data);
        setUser(response.data);
      } catch (error: any) {
        console.error('❌ Failed to fetch user:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data
        });
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
      console.log('🔄 Redirecting to login page...');
      router.push('/');
    } catch (error: any) {
      console.error('❌ Logout error:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      // Still redirect even if logout fails
      router.push('/');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Dashboard</h1>

          {user?.photo_url && (
            <img
              src={user.photo_url}
              alt="Profile"
              className="w-20 h-20 rounded-full mx-auto mb-4"
            />
          )}

          <div className="space-y-2 text-left">
            <p><strong>UID:</strong> {user?.uid}</p>
            {user?.display_name && (
              <p><strong>Name:</strong> {user.display_name}</p>
            )}
            {user?.email && (
              <p><strong>Email:</strong> {user.email}</p>
            )}
            {user?.phone_number && (
              <p><strong>Phone:</strong> {user.phone_number}</p>
            )}
          </div>

          <button
            onClick={handleLogout}
            className="mt-6 w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}