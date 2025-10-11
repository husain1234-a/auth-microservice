'use client';

import { useState, useEffect } from 'react';
import { Order, OrderStatus } from '@/types/order';
import { useOrder } from '@/contexts/OrderContext';
import { useUser } from '@/contexts/UserContext';
import OrderCard from './OrderCard';
import OrderDetails from './OrderDetails';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function DeliveryOrderList() {
    const { state, fetchAllOrders, clearError } = useOrder();
    const { user } = useUser();
    const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
    const [filters, setFilters] = useState({
        status: '',
        limit: 20,
        offset: 0
    });

    useEffect(() => {
        loadOrders();
    }, [filters]);

    useEffect(() => {
        if (state.error) {
            const timer = setTimeout(() => {
                clearError();
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [state.error, clearError]);

    const loadOrders = async () => {
        try {
            // For delivery partners, we might want to filter by assigned orders
            // This would require backend support to filter by delivery_partner_id
            await fetchAllOrders({
                ...filters,
                // delivery_partner_id: user?.uid // This would need backend support
            });
        } catch (error) {
            console.error('Failed to load delivery orders:', error);
        }
    };

    const handleStatusFilter = (status: string) => {
        setFilters(prev => ({
            ...prev,
            status: status === prev.status ? '' : status,
            offset: 0
        }));
    };

    const handleLoadMore = () => {
        setFilters(prev => ({
            ...prev,
            offset: prev.offset + prev.limit
        }));
    };

    // Filter orders that are relevant for delivery partners
    const deliveryRelevantOrders = state.orders.filter(order => {
        // Show orders that are in delivery-relevant statuses
        const relevantStatuses = [
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
            OrderStatus.OUT_FOR_DELIVERY,
            OrderStatus.DELIVERED
        ];
        return relevantStatuses.includes(order.status);
    });

    const statusOptions = [
        { value: '', label: 'All Orders' },
        { value: OrderStatus.CONFIRMED, label: 'Ready for Pickup' },
        { value: OrderStatus.PREPARING, label: 'Being Prepared' },
        { value: OrderStatus.OUT_FOR_DELIVERY, label: 'Out for Delivery' },
        { value: OrderStatus.DELIVERED, label: 'Delivered' }
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">My Delivery Orders</h1>
                    <p className="text-gray-600">Orders assigned to you for delivery</p>
                </div>
            </div>

            {/* Status Filters */}
            <div className="flex flex-wrap gap-2">
                {statusOptions.map((option) => (
                    <button
                        key={option.value}
                        onClick={() => handleStatusFilter(option.value)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${filters.status === option.value
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        {option.label}
                    </button>
                ))}
            </div>

            {/* Error Display */}
            {state.error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                    <div className="flex justify-between items-center">
                        <p className="text-red-600 text-sm">{state.error}</p>
                        <button
                            onClick={clearError}
                            className="text-red-400 hover:text-red-600"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
            )}

            {/* Loading State */}
            {state.loading && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[...Array(6)].map((_, index) => (
                        <SkeletonLoader key={index} />
                    ))}
                </div>
            )}

            {/* Orders Grid */}
            {!state.loading && (
                <>
                    {deliveryRelevantOrders.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {deliveryRelevantOrders.map((order) => (
                                <OrderCard
                                    key={order.id}
                                    order={order}
                                    onViewDetails={setSelectedOrder}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4">🚚</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">No delivery orders found</h3>
                            <p className="text-gray-500">
                                {filters.status
                                    ? 'No orders match the selected status'
                                    : 'No orders are currently assigned for delivery'
                                }
                            </p>
                        </div>
                    )}

                    {/* Load More Button */}
                    {deliveryRelevantOrders.length >= filters.limit && (
                        <div className="text-center">
                            <button
                                onClick={handleLoadMore}
                                disabled={state.loading}
                                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                            >
                                {state.loading ? 'Loading...' : 'Load More'}
                            </button>
                        </div>
                    )}
                </>
            )}

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