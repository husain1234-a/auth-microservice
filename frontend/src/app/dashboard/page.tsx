'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import CustomerDashboard from '@/components/dashboards/CustomerDashboard';
import DeliveryDashboard from '@/components/dashboards/DeliveryDashboard';
import OwnerDashboard from '@/components/dashboards/OwnerDashboard';
import AdminDashboard from '@/components/dashboards/AdminDashboard';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function Dashboard() {
  const { user, loading, logout } = useUser();
  const router = useRouter();

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!loading && !user) {
      router.push('/');
    }
  }, [user, loading, router]);

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
    switch (user.role.toLowerCase()) {
      case 'customer':
        return <CustomerDashboard user={user} onLogout={logout} />;

      case 'delivery_guy':
        return <DeliveryDashboard user={user} onLogout={logout} />;

      case 'owner':
        return <OwnerDashboard user={user} onLogout={logout} />;

      case 'admin':
        return <AdminDashboard user={user} onLogout={logout} />;

      default:
        console.warn('⚠️ Unknown user role:', user.role);
        // Default to customer dashboard for unknown roles
        return <CustomerDashboard user={user} onLogout={logout} />;
    }
  };

  return renderDashboard();
}