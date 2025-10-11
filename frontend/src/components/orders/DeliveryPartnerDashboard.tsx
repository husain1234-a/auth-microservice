'use client';

import { useState, useEffect } from 'react';
import { Order, OrderStatus } from '@/types/order';
import { useOrder } from '@/contexts/OrderContext';
import { useUser } from '@/contexts/UserContext';
import OrderCard from './OrderCard';
import OrderDetails from './OrderDetails';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function DeliveryPartnerDashboard() {
    const { state, fetchAllOrders, updateOrderStatus, clearError } = useOrder();
    const { hasRole, user } = useUser();
    const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
    const [activeTab, setActiveTab] = useState<'available' | 'assigned' | 'completed'>('available');

    useEffect(() => {
        if (hasRole(['delivery_partner'])) {
            loadOrders();
        }
    }, []);

    const loadOrders = async () => {
        try {
            await fetchAllOrders({});
        } catch (error) {
            console.error('Failed to load orders:', error);
        }
    };

    // Filter orders based on delivery partner status
    const availableOrders = state.orders.filter(order =>
        order.status === OrderStatus.CONFIRMED && !order.delivery_partner_id
    );

    const assignedOrders = state.orders.filter(order =>
        order.delivery_partner_id === user?.uid &&
        [OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.OUT_FOR_DELIVERY].includes(order.status)
    );

    const completedOrders = state.orders.filter(order =>
        order.delivery_partner_id === user?.uid &&
        [OrderStatus.DELIVERED, OrderStatus.CANCELLED].includes(order.status)
    );

    const handleAcceptDelivery = async (orderId: number) => {
        if (window.confirm('Accept this delivery assignment?')) {
            try {
                // This would need a backend endpoint to assign delivery partner
                // For now, we'll use the existing assign delivery partner function
                // In a real implementation, this would be a separate endpoint
                console.log('Accepting delivery for order:', orderId);
                await loadOrders();
            } catch (error) {
                console.error('Failed to accept delivery:', error);
            }
        }
    };

    if (!hasRole(['delivery_partner'])) {
        return (
            <div className="text-center py-12">
                <div className="text-6xl mb-4">🚚</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
                <p className="text-gray-500">You need delivery partner privileges to access this page.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header with Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <div className="flex items-center">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-blue-600">Available Orders</p>
                            <p className="text-2xl font-bold text-blue-900">{availableOrders.length}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                    <div className="flex items-center">
                        <div className="p-2 bg-orange-100 rounded-lg">
                            <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-orange-600">My Deliveries</p>
                            <p className="text-2xl font-bold text-orange-900">{assignedOrders.length}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <div className="flex items-center">
                        <div className="p-2 bg-green-100 rounded-lg">
                            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-green-600">Completed</p>
                            <p className="text-2xl font-bold text-green-900">{completedOrders.length}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab('available')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'available'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Available Orders ({availableOrders.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('assigned')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'assigned'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        My Deliveries ({assignedOrders.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('completed')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === 'completed'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Completed ({completedOrders.length})
                    </button>
                </nav>
            </div>

            {/* Tab Content */}
            <div className="space-y-4">
                {state.loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(6)].map((_, index) => (
                            <SkeletonLoader key={index} />
                        ))}
                    </div>
                ) : (
                    <>
                        {/* Available Orders Tab */}
                        {activeTab === 'available' && (
                            <div className="space-y-4">
                                {availableOrders.length > 0 ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {availableOrders.map((order) => (
                                            <div key={order.id} className="relative">
                                                <OrderCard
                                                    order={order}
                                                    onViewDetails={setSelectedOrder}
                                                />
                                                <div className="mt-3 flex gap-2">
                                                    <button
                                                        onClick={() => handleAcceptDelivery(order.id)}
                                                        className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                                                    >
                                                        ✓ Accept Delivery
                                                    </button>
                                                    <button
                                                        onClick={() => setSelectedOrder(order)}
                                                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                                                    >
                                                        View Details
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-12">
                                        <div className="text-6xl mb-4">📦</div>
                                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Available Orders</h3>
                                        <p className="text-gray-500">Check back later for new delivery opportunities.</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Assigned Orders Tab */}
                        {activeTab === 'assigned' && (
                            <div className="space-y-4">
                                {assignedOrders.length > 0 ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {assignedOrders.map((order) => (
                                            <OrderCard
                                                key={order.id}
                                                order={order}
                                                onViewDetails={setSelectedOrder}
                                            />
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-12">
                                        <div className="text-6xl mb-4">🚛</div>
                                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Deliveries</h3>
                                        <p className="text-gray-500">You don't have any active delivery assignments.</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Completed Orders Tab */}
                        {activeTab === 'completed' && (
                            <div className="space-y-4">
                                {completedOrders.length > 0 ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {completedOrders.map((order) => (
                                            <OrderCard
                                                key={order.id}
                                                order={order}
                                                onViewDetails={setSelectedOrder}
                                            />
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-12">
                                        <div className="text-6xl mb-4">✅</div>
                                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Completed Deliveries</h3>
                                        <p className="text-gray-500">Your completed deliveries will appear here.</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Order Details Modal */}
            {selectedOrder && (
                <OrderDetails
                    order={selectedOrder}
                    onClose={() => setSelectedOrder(null)}
                    isModal={true}
                />
            )}
        </div>
    );
}