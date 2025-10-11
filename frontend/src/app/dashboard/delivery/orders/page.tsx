'use client';

import { useUser } from '@/contexts/UserContext';
import DeliveryOrderList from '@/components/orders/DeliveryOrderList';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function DeliveryDashboardOrdersPage() {
    const { user, loading, hasRole } = useUser();

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 p-4">
                <div className="max-w-7xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(6)].map((_, index) => (
                            <SkeletonLoader key={index} />
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (!user || !hasRole(['delivery_partner'])) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl mb-4">🚚</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
                    <p className="text-gray-600">You need delivery partner privileges to access this page.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900">My Delivery Orders</h1>
                <p className="text-gray-600 mt-2">Manage orders assigned to you for delivery</p>
            </div>
            <DeliveryOrderList />
        </div>
    );
}