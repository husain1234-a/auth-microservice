'use client';

import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import OrderTemplates from '@/components/orders/OrderTemplates';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function OrderTemplatesPage() {
    const { user, loading } = useUser();
    const router = useRouter();

    const handleOrderCreated = (orderId: number) => {
        router.push(`/orders/${orderId}`);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 p-4">
                <div className="max-w-6xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(3)].map((_, index) => (
                            <SkeletonLoader key={index} />
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl mb-4">🔒</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
                    <p className="text-gray-600">Please log in to view your order templates.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <OrderTemplates onOrderCreated={handleOrderCreated} />
        </div>
    );
}