'use client';

import { useState, useEffect } from 'react';
import { Order, OrderStatus } from '@/types/order';
import { useOrder } from '@/contexts/OrderContext';
import { useUser } from '@/contexts/UserContext';
import OrderCard from './OrderCard';
import OrderDetails from './OrderDetails';
import SkeletonLoader from '@/components/SkeletonLoader';

interface OrderListProps {
    showAllOrders?: boolean; // For admin view
}

export default function OrderList({ showAllOrders = false }: OrderListProps) {
    const { state, fetchMyOrders, fetchAllOrders, clearError } = useOrder();
    const { hasRole } = useUser();
    const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
    const [filters, setFilters] = useState({
        status: '',
        user_id: '',
        limit: 20,
        offset: 0
    });
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        loadOrders();
    }, [filters, showAllOrders]);

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
            if (showAllOrders && hasRole(['admin', 'owner'])) {
                await fetchAllOrders(filters);
            } else {
                await fetchMyOrders({ limit: filters.limit, offset: filters.offset });
            }
        } catch (error) {
            console.error('Failed to load orders:', error);
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

    const filteredOrders = state.orders.filter(order => {
        if (searchTerm) {
            const searchLower = searchTerm.toLowerCase();
            return (
                order.id.toString().includes(searchLower) ||
                order.delivery_address.toLowerCase().includes(searchLower) ||
                order.items.some(item =>
                    item.product?.name.toLowerCase().includes(searchLower)
                )
            );
        }
        return true;
    });

    const statusOptions = [
        { value: '', label: 'All Orders' },
        { value: OrderStatus.PENDING, label: 'Pending' },
        { value: OrderStatus.CONFIRMED, label: 'Confirmed' },
        { value: OrderStatus.PREPARING, label: 'Preparing' },
        { value: OrderStatus.OUT_FOR_DELIVERY, label: 'Out for Delivery' },
        { value: OrderStatus.DELIVERED, label: 'Delivered' },
        { value: OrderStatus.CANCELLED, label: 'Cancelled' }
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h1 className="text-2xl font-bold text-gray-900">
                    {showAllOrders ? 'All Orders' : 'My Orders'}
                </h1>

                {/* Search */}
                <div className="w-full sm:w-auto">
                    <input
                        type="text"
                        placeholder="Search orders..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full sm:w-64 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            </div>

            {/* Filters */}
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

            {/* Additional Filters for Admin */}
            {showAllOrders && hasRole(['admin', 'owner']) && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            User ID
                        </label>
                        <input
                            type="text"
                            placeholder="Filter by user ID..."
                            value={filters.user_id}
                            onChange={(e) => setFilters(prev => ({ ...prev, user_id: e.target.value, offset: 0 }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Items per page
                        </label>
                        <select
                            value={filters.limit}
                            onChange={(e) => setFilters(prev => ({ ...prev, limit: Number(e.target.value), offset: 0 }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value={10}>10</option>
                            <option value={20}>20</option>
                            <option value={50}>50</option>
                        </select>
                    </div>
                </div>
            )}

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
                    {filteredOrders.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {filteredOrders.map((order) => (
                                <OrderCard
                                    key={order.id}
                                    order={order}
                                    onViewDetails={setSelectedOrder}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4">📦</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">No orders found</h3>
                            <p className="text-gray-500">
                                {searchTerm || filters.status
                                    ? 'Try adjusting your search or filters'
                                    : showAllOrders
                                        ? 'No orders have been placed yet'
                                        : "You haven't placed any orders yet"
                                }
                            </p>
                        </div>
                    )}

                    {/* Load More Button */}
                    {filteredOrders.length >= filters.limit && (
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