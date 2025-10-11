'use client';

import { useState, useEffect } from 'react';
import { Order, OrderStatus } from '@/types/order';
import { useOrder } from '@/contexts/OrderContext';
import { useUser } from '@/contexts/UserContext';
import OrderCard from './OrderCard';
import OrderDetails from './OrderDetails';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function AdminOrderManagement() {
    const { state, fetchAllOrders, updateOrderStatus, assignDeliveryPartner, clearError } = useOrder();
    const { hasRole } = useUser();
    const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
    const [filters, setFilters] = useState({
        status: '',
        user_id: '',
        limit: 20,
        offset: 0
    });
    const [selectedOrders, setSelectedOrders] = useState<number[]>([]);
    const [bulkAction, setBulkAction] = useState('');

    useEffect(() => {
        if (hasRole(['admin', 'owner'])) {
            loadOrders();
        }
    }, [filters]);

    const loadOrders = async () => {
        try {
            await fetchAllOrders(filters);
        } catch (error) {
            console.error('Failed to load orders:', error);
        }
    };

    const handleBulkAction = async () => {
        if (selectedOrders.length === 0 || !bulkAction) return;

        const confirmMessage = `Are you sure you want to ${bulkAction} ${selectedOrders.length} orders?`;
        if (!window.confirm(confirmMessage)) return;

        try {
            for (const orderId of selectedOrders) {
                if (bulkAction === 'approve') {
                    await updateOrderStatus(orderId, OrderStatus.CONFIRMED);
                } else if (bulkAction === 'reject') {
                    await updateOrderStatus(orderId, OrderStatus.CANCELLED);
                } else if (bulkAction === 'preparing') {
                    await updateOrderStatus(orderId, OrderStatus.PREPARING);
                }
            }
            setSelectedOrders([]);
            setBulkAction('');
            await loadOrders();
        } catch (error) {
            console.error('Failed to perform bulk action:', error);
        }
    };

    const handleOrderSelect = (orderId: number, selected: boolean) => {
        if (selected) {
            setSelectedOrders(prev => [...prev, orderId]);
        } else {
            setSelectedOrders(prev => prev.filter(id => id !== orderId));
        }
    };

    const handleSelectAll = (selected: boolean) => {
        if (selected) {
            setSelectedOrders(state.orders.map(order => order.id));
        } else {
            setSelectedOrders([]);
        }
    };

    const pendingOrders = state.orders.filter(order => order.status === OrderStatus.PENDING);
    const activeOrders = state.orders.filter(order =>
        [OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.OUT_FOR_DELIVERY].includes(order.status)
    );
    const completedOrders = state.orders.filter(order =>
        [OrderStatus.DELIVERED, OrderStatus.CANCELLED].includes(order.status)
    );

    if (!hasRole(['admin', 'owner'])) {
        return (
            <div className="text-center py-12">
                <div className="text-6xl mb-4">🔒</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
                <p className="text-gray-500">You need admin or owner privileges to access this page.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header with Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                    <div className="flex items-center">
                        <div className="p-2 bg-yellow-100 rounded-lg">
                            <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-yellow-600">Pending Approval</p>
                            <p className="text-2xl font-bold text-yellow-900">{pendingOrders.length}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <div className="flex items-center">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-blue-600">Active Orders</p>
                            <p className="text-2xl font-bold text-blue-900">{activeOrders.length}</p>
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

                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="flex items-center">
                        <div className="p-2 bg-gray-100 rounded-lg">
                            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Total Orders</p>
                            <p className="text-2xl font-bold text-gray-900">{state.orders.length}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bulk Actions */}
            {selectedOrders.length > 0 && (
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-medium text-blue-900">
                                {selectedOrders.length} orders selected
                            </span>
                            <select
                                value={bulkAction}
                                onChange={(e) => setBulkAction(e.target.value)}
                                className="px-3 py-1 border border-blue-300 rounded-md text-sm"
                            >
                                <option value="">Select Action</option>
                                <option value="approve">Approve Orders</option>
                                <option value="reject">Reject Orders</option>
                                <option value="preparing">Mark as Preparing</option>
                            </select>
                            <button
                                onClick={handleBulkAction}
                                disabled={!bulkAction}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 text-sm"
                            >
                                Apply Action
                            </button>
                        </div>
                        <button
                            onClick={() => setSelectedOrders([])}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                            Clear Selection
                        </button>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                        <select
                            value={filters.status}
                            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value, offset: 0 }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="">All Statuses</option>
                            <option value={OrderStatus.PENDING}>Pending Approval</option>
                            <option value={OrderStatus.CONFIRMED}>Confirmed</option>
                            <option value={OrderStatus.PREPARING}>Preparing</option>
                            <option value={OrderStatus.OUT_FOR_DELIVERY}>Out for Delivery</option>
                            <option value={OrderStatus.DELIVERED}>Delivered</option>
                            <option value={OrderStatus.CANCELLED}>Cancelled</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">User ID</label>
                        <input
                            type="text"
                            value={filters.user_id}
                            onChange={(e) => setFilters(prev => ({ ...prev, user_id: e.target.value, offset: 0 }))}
                            placeholder="Filter by user ID..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Items per page</label>
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
                    <div className="flex items-end">
                        <button
                            onClick={loadOrders}
                            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                            Refresh
                        </button>
                    </div>
                </div>
            </div>

            {/* Select All Checkbox */}
            <div className="flex items-center space-x-2">
                <input
                    type="checkbox"
                    id="selectAll"
                    checked={selectedOrders.length === state.orders.length && state.orders.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="selectAll" className="text-sm font-medium text-gray-700">
                    Select All Orders
                </label>
            </div>

            {/* Orders Grid */}
            {state.loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[...Array(6)].map((_, index) => (
                        <SkeletonLoader key={index} />
                    ))}
                </div>
            ) : (
                <div className="space-y-4">
                    {state.orders.map((order) => (
                        <div key={order.id} className="flex items-start space-x-4 bg-white p-4 rounded-lg shadow-sm border">
                            <input
                                type="checkbox"
                                checked={selectedOrders.includes(order.id)}
                                onChange={(e) => handleOrderSelect(order.id, e.target.checked)}
                                className="mt-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <div className="flex-1">
                                <OrderCard
                                    order={order}
                                    onViewDetails={setSelectedOrder}
                                />
                            </div>
                        </div>
                    ))}
                </div>
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