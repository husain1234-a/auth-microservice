'use client';

import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import CreateOrderForm from '@/components/orders/CreateOrderForm';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function CreateOrderPage() {
    const { user, loading } = useUser();
    const router = useRouter();

    const handleOrderSuccess = (orderId: number) => {
        router.push(`/orders/${orderId}`);
    };

    const handleCancel = () => {
        router.back();
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 p-4">
                <div className="max-w-2xl mx-auto">
                    <SkeletonLoader />
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
                    <p className="text-gray-600">Please log in to create an order.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <CreateOrderForm
                onSuccess={handleOrderSuccess}
                onCancel={handleCancel}
            />
        </div>
    );
}