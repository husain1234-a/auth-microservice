'use client';

import { useState, useEffect } from 'react';
import { useOrder } from '@/contexts/OrderContext';
import { useUser } from '@/contexts/UserContext';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function OrderAnalytics() {
    const { state, fetchAnalytics, clearError } = useOrder();
    const { hasRole } = useUser();
    const [dateRange, setDateRange] = useState({
        start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 90 days ago
        end_date: new Date().toISOString().split('T')[0] // today
    });

    useEffect(() => {
        if (hasRole(['admin', 'owner'])) {
            loadAnalytics();
        }
    }, [dateRange]);

    useEffect(() => {
        if (state.error) {
            const timer = setTimeout(() => {
                clearError();
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [state.error, clearError]);

    const loadAnalytics = async () => {
        try {
            console.log('Loading analytics for date range:', dateRange);
            await fetchAnalytics(dateRange.start_date, dateRange.end_date);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    };

    const handleDateChange = (field: 'start_date' | 'end_date', value: string) => {
        setDateRange(prev => ({
            ...prev,
            [field]: value
        }));
    };

    if (!hasRole(['admin', 'owner'])) {
        return (
            <div className="text-center py-12">
                <div className="text-6xl mb-4">🔒</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
                <p className="text-gray-500">You need admin privileges to view analytics.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h2 className="text-2xl font-bold text-gray-900">Order Analytics</h2>

                {/* Date Range Selector */}
                <div className="flex gap-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Start Date
                        </label>
                        <input
                            type="date"
                            value={dateRange.start_date}
                            onChange={(e) => handleDateChange('start_date', e.target.value)}
                            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            End Date
                        </label>
                        <input
                            type="date"
                            value={dateRange.end_date}
                            onChange={(e) => handleDateChange('end_date', e.target.value)}
                            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>
            </div>

            {/* Error Display */}
            {state.error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                    <div className="flex justify-between items-center">
                        <p className="text-red-600 text-sm">
                            {typeof state.error === 'string' ? state.error : 'An error occurred while loading analytics'}
                        </p>
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
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[...Array(4)].map((_, index) => (
                        <SkeletonLoader key={index} />
                    ))}
                </div>
            )}

            {/* Analytics Cards */}
            {!state.loading && state.analytics && (
                <>
                    {/* Key Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {/* Total Revenue */}
                        <div className="bg-white p-6 rounded-lg shadow-md">
                            <div className="flex items-center">
                                <div className="p-2 bg-green-100 rounded-lg">
                                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                                    </svg>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Total Revenue</p>
                                    <p className="text-2xl font-bold text-gray-900">
                                        ₹{state.analytics.revenue.reduce((sum, item) => sum + item.total_revenue, 0).toFixed(2)}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Total Orders */}
                        <div className="bg-white p-6 rounded-lg shadow-md">
                            <div className="flex items-center">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                    </svg>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Total Orders</p>
                                    <p className="text-2xl font-bold text-gray-900">
                                        {state.analytics.revenue.reduce((sum, item) => sum + item.order_count, 0)}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Average Delivery Time */}
                        <div className="bg-white p-6 rounded-lg shadow-md">
                            <div className="flex items-center">
                                <div className="p-2 bg-purple-100 rounded-lg">
                                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Avg Delivery Time</p>
                                    <p className="text-2xl font-bold text-gray-900">
                                        {Math.round(state.analytics.delivery_performance.average_delivery_time)} min
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* On-Time Delivery Rate */}
                        <div className="bg-white p-6 rounded-lg shadow-md">
                            <div className="flex items-center">
                                <div className="p-2 bg-orange-100 rounded-lg">
                                    <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">On-Time Rate</p>
                                    <p className="text-2xl font-bold text-gray-900">
                                        {(state.analytics.delivery_performance.on_time_delivery_rate * 100).toFixed(1)}%
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Revenue Chart */}
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h3 className="text-lg font-semibold mb-4">Revenue Over Time</h3>
                        <div className="space-y-3">
                            {state.analytics.revenue.map((item, index) => (
                                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                    <div>
                                        <p className="font-medium">{new Date(item.date).toLocaleDateString()}</p>
                                        <p className="text-sm text-gray-500">{item.order_count} orders</p>
                                    </div>
                                    <p className="text-lg font-bold text-green-600">
                                        ₹{item.total_revenue.toFixed(2)}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Top Customers */}
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h3 className="text-lg font-semibold mb-4">Top Customers</h3>
                        <div className="space-y-3">
                            {state.analytics.top_customers.map((customer, index) => (
                                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                    <div>
                                        <p className="font-medium">User ID: {customer.user_id}</p>
                                        <p className="text-sm text-gray-500">{customer.total_orders} orders</p>
                                    </div>
                                    <p className="text-lg font-bold text-blue-600">
                                        ₹{customer.total_spent.toFixed(2)}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Cancellation Rate */}
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h3 className="text-lg font-semibold mb-4">Cancellation Analysis</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="text-center p-4 bg-red-50 rounded-lg">
                                <p className="text-2xl font-bold text-red-600">
                                    {(state.analytics.cancellation_rate.cancellation_rate * 100).toFixed(1)}%
                                </p>
                                <p className="text-sm text-gray-500">Cancellation Rate</p>
                            </div>
                            <div className="text-center p-4 bg-gray-50 rounded-lg">
                                <p className="text-2xl font-bold text-gray-900">
                                    {state.analytics.cancellation_rate.cancelled_orders}
                                </p>
                                <p className="text-sm text-gray-500">
                                    of {state.analytics.cancellation_rate.total_orders} orders
                                </p>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Debug State */}
            {process.env.NODE_ENV === 'development' && (
                <div className="bg-gray-100 p-4 rounded mb-4">
                    <h4 className="font-bold">Debug State:</h4>
                    <p>Loading: {state.loading ? 'true' : 'false'}</p>
                    <p>Analytics: {state.analytics ? 'exists' : 'null/undefined'}</p>
                    <p>Error: {state.error ? state.error : 'none'}</p>
                    {state.analytics && (
                        <div>
                            <p>Revenue items: {state.analytics.revenue?.length || 0}</p>
                            <p>Top customers: {state.analytics.top_customers?.length || 0}</p>
                        </div>
                    )}
                </div>
            )}

            {/* No Data State */}
            {!state.loading && !state.analytics && !state.error && (
                <div className="text-center py-12">
                    <div className="text-6xl mb-4">📊</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No analytics data</h3>
                    <p className="text-gray-500">Analytics data will appear here once orders are placed.</p>
                </div>
            )}
        </div>
    );
}