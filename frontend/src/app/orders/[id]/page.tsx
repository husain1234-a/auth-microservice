'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import { useOrder } from '@/contexts/OrderContext';
import { Order } from '@/types/order';
import OrderDetailsPage from '@/components/orders/OrderDetailsPage';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function OrderDetailPage() {
    const { user, loading: userLoading } = useUser();
    const { state, fetchOrder } = useOrder();
    const params = useParams();
    const router = useRouter();
    const [order, setOrder] = useState<Order | null>(null);

    const orderId = params.id ? parseInt(params.id as string) : null;

    useEffect(() => {
        if (orderId && user) {
            loadOrder();
        }
    }, [orderId, user]);

    useEffect(() => {
        if (state.currentOrder) {
            setOrder(state.currentOrder);
        }
    }, [state.currentOrder]);

    const loadOrder = async () => {
        if (!orderId) return;

        try {
            await fetchOrder(orderId);
        } catch (error) {
            console.error('Failed to load order:', error);
        }
    };

    const handleClose = () => {
        router.push('/orders');
    };

    if (userLoading || state.loading) {
        return (
            <div className="min-h-screen bg-gray-50 p-4">
                <div className="max-w-4xl mx-auto">
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
                    <p className="text-gray-600">Please log in to view order details.</p>
                </div>
            </div>
        );
    }

    if (!orderId) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl mb-4">❌</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Invalid Order</h1>
                    <p className="text-gray-600">The order ID is not valid.</p>
                    <button
                        onClick={() => router.push('/orders')}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                        Back to Orders
                    </button>
                </div>
            </div>
        );
    }

    if (state.error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl mb-4">⚠️</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Order</h1>
                    <p className="text-gray-600 mb-4">{state.error}</p>
                    <div className="space-x-4">
                        <button
                            onClick={loadOrder}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                            Try Again
                        </button>
                        <button
                            onClick={() => router.push('/orders')}
                            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                        >
                            Back to Orders
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl mb-4">📦</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Order Not Found</h1>
                    <p className="text-gray-600">The requested order could not be found.</p>
                    <button
                        onClick={() => router.push('/orders')}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                        Back to Orders
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-6">
                <button
                    onClick={handleClose}
                    className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
                >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Orders
                </button>
            </div>

            <div className="bg-white rounded-lg shadow-md">
                <OrderDetailsPage order={order} />
            </div>
        </div>
    );
}