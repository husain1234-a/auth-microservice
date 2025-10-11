'use client';

import { useState, useEffect } from 'react';
import { useUser } from '@/contexts/UserContext';
import { useOrder } from '@/contexts/OrderContext';
import { Order, OrderStatus } from '@/types/order';
import Link from 'next/link';
import SkeletonLoader from '@/components/SkeletonLoader';
import R2Image from '@/components/ui/R2Image';

export default function OwnerOrderDetailPage({ params }: { params: { id: string } }) {
    const { user, loading: userLoading, hasRole } = useUser();
    const { state, fetchOrder, updateOrderStatus } = useOrder();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadOrder = async () => {
            if (!user || !params.id) return;

            try {
                setLoading(true);
                await fetchOrder(parseInt(params.id));
            } catch (err) {
                console.error('Failed to fetch order:', err);
                setError('Failed to load order details. Please try again later.');
            } finally {
                setLoading(false);
            }
        };

        if (user && hasRole(['owner'])) {
            loadOrder();
        }
    }, [user, params.id, fetchOrder, hasRole]);

    const handleStatusUpdate = async (newStatus: OrderStatus) => {
        if (!state.currentOrder) return;

        try {
            setLoading(true);
            await updateOrderStatus(state.currentOrder.id, newStatus);
        } catch (err) {
            console.error('Failed to update order status:', err);
            setError('Failed to update order status. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    if (userLoading) {
        return (
            <div className="min-h-screen bg-gray-50 p-4">
                <div className="max-w-7xl mx-auto">
                    <SkeletonLoader type="text" className="h-8 w-64 mb-6" />
                    <SkeletonLoader type="profile" />
                </div>
            </div>
        );
    }

    if (!user || !hasRole(['owner'])) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl mb-4">🔒</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
                    <p className="text-gray-600">You need owner privileges to view order details.</p>
                    <Link href="/" className="mt-4 inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        Go to Login
                    </Link>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl mb-4">⚠️</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Order</h1>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    if (loading && !state.currentOrder) {
        return (
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <SkeletonLoader type="text" className="h-8 w-64 mb-6" />
                <SkeletonLoader type="profile" />
            </div>
        );
    }

    if (!state.currentOrder) {
        return (
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="text-center py-12">
                    <div className="text-6xl mb-4">❓</div>
                    <h3 className="text-xl font-medium text-gray-900 mb-2">Order Not Found</h3>
                    <p className="text-gray-500 mb-6">The order you're looking for doesn't exist or you don't have permission to view it.</p>
                    <Link
                        href="/dashboard/owner/orders/list"
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Back to Orders
                    </Link>
                </div>
            </div>
        );
    }

    const order = state.currentOrder;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-6">
                <Link
                    href="/dashboard/owner/orders/list"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-4"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                    </svg>
                    Back to Orders
                </Link>
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Order #{order.id}</h1>
                        <p className="mt-1 text-gray-600">Placed on {new Date(order.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="mt-2 md:mt-0">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${order.status === OrderStatus.DELIVERED ? 'bg-green-100 text-green-800' :
                                order.status === OrderStatus.CANCELLED ? 'bg-red-100 text-red-800' :
                                    'bg-yellow-100 text-yellow-800'
                            }`}>
                            {order.status.replace('_', ' ')}
                        </span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                        <div className="px-4 py-5 sm:px-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900">Order Items</h3>
                        </div>
                        <div className="border-t border-gray-200">
                            <ul className="divide-y divide-gray-200">
                                {order.items.map((item) => (
                                    <li key={item.id} className="px-4 py-6 sm:px-6">
                                        <div className="flex items-center">
                                            {item.product?.image_url ? (
                                                <div className="flex-shrink-0 w-20 h-20 rounded-md overflow-hidden">
                                                    <R2Image
                                                        src={item.product.image_url}
                                                        alt={item.product.name}
                                                        className="w-full h-full object-cover"
                                                        fallbackText={item.product.name}
                                                    />
                                                </div>
                                            ) : (
                                                <div className="flex-shrink-0 w-20 h-20 bg-gray-200 rounded-md flex items-center justify-center">
                                                    <span className="text-gray-500 text-xs">No Image</span>
                                                </div>
                                            )}
                                            <div className="ml-4 flex-1">
                                                <div className="flex justify-between">
                                                    <div>
                                                        <h4 className="text-sm font-medium text-gray-900">
                                                            {item.product?.name || `Product #${item.product_id}`}
                                                        </h4>
                                                        <p className="mt-1 text-sm text-gray-500">
                                                            Quantity: {item.quantity}
                                                        </p>
                                                    </div>
                                                    <p className="text-sm font-medium text-gray-900">
                                                        ₹{item.price * item.quantity}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                            <div className="border-t border-gray-200 px-4 py-6 sm:px-6">
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <dt className="text-sm text-gray-600">Subtotal</dt>
                                        <dd className="text-sm font-medium text-gray-900">₹{order.total_amount - order.delivery_fee}</dd>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <dt className="text-sm text-gray-600">Delivery Fee</dt>
                                        <dd className="text-sm font-medium text-gray-900">₹{order.delivery_fee}</dd>
                                    </div>
                                    <div className="flex items-center justify-between border-t border-gray-200 pt-4">
                                        <dt className="text-base font-medium text-gray-900">Order Total</dt>
                                        <dd className="text-base font-medium text-gray-900">₹{order.total_amount}</dd>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div>
                    <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
                        <div className="px-4 py-5 sm:px-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900">Order Management</h3>
                        </div>
                        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Update Status
                                    </label>
                                    <div className="grid grid-cols-2 gap-2">
                                        {Object.values(OrderStatus).map((status) => (
                                            <button
                                                key={status}
                                                onClick={() => handleStatusUpdate(status)}
                                                disabled={loading}
                                                className={`px-3 py-2 text-xs rounded-md ${order.status === status
                                                        ? 'bg-blue-100 text-blue-800'
                                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                                    }`}
                                            >
                                                {status.replace('_', ' ')}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                        <div className="px-4 py-5 sm:px-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900">Delivery Information</h3>
                        </div>
                        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
                            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                                <div className="sm:col-span-2">
                                    <dt className="text-sm font-medium text-gray-500">Delivery Address</dt>
                                    <dd className="mt-1 text-sm text-gray-900">
                                        {order.delivery_address}
                                    </dd>
                                </div>
                                <div className="sm:col-span-1">
                                    <dt className="text-sm font-medium text-gray-500">Estimated Delivery</dt>
                                    <dd className="mt-1 text-sm text-gray-900">
                                        {order.estimated_delivery_time
                                            ? new Date(order.estimated_delivery_time).toLocaleDateString()
                                            : 'Not specified'}
                                    </dd>
                                </div>
                                <div className="sm:col-span-1">
                                    <dt className="text-sm font-medium text-gray-500">Delivered At</dt>
                                    <dd className="mt-1 text-sm text-gray-900">
                                        {order.delivered_at
                                            ? new Date(order.delivered_at).toLocaleDateString()
                                            : 'Not yet delivered'}
                                    </dd>
                                </div>
                                <div className="sm:col-span-2">
                                    <dt className="text-sm font-medium text-gray-500">Delivery Partner</dt>
                                    <dd className="mt-1 text-sm text-gray-900">
                                        {order.delivery_partner_id || 'Not assigned'}
                                    </dd>
                                </div>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}