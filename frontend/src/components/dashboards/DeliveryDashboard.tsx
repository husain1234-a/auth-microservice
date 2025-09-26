'use client';

import { useEffect, useState } from 'react';
import SkeletonLoader from '@/components/SkeletonLoader';
import R2Image from '@/components/ui/R2Image';

interface User {
    uid: string;
    email?: string;
    phone_number?: string;
    display_name?: string;
    photo_url?: string;
    role: string;
}

interface DeliveryDashboardProps {
    user: User;
    onLogout: () => void;
}

interface Delivery {
    id: number;
    order_id: string;
    customer_name: string;
    customer_address: string;
    customer_phone: string;
    items: string[];
    total_amount: number;
    status: 'pending' | 'picked' | 'in_transit' | 'delivered' | 'cancelled';
    pickup_time?: string;
    delivery_time?: string;
    distance: string;
    estimated_time: string;
}

export default function DeliveryDashboard({ user, onLogout }: DeliveryDashboardProps) {
    const [deliveries, setDeliveries] = useState<Delivery[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'available' | 'my_deliveries' | 'completed' | 'stats'>('available');
    const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month'>('week');

    // Mock data - replace with actual API calls
    useEffect(() => {
        const mockDeliveries: Delivery[] = [
            {
                id: 1,
                order_id: 'ORD-001',
                customer_name: 'John Doe',
                customer_address: '123 Main St, Sector 15, Gurgaon',
                customer_phone: '+91 9876543210',
                items: ['Apples 1kg', 'Milk 1L', 'Bread'],
                total_amount: 250,
                status: 'pending',
                distance: '2.5 km',
                estimated_time: '15 mins'
            },
            {
                id: 2,
                order_id: 'ORD-002',
                customer_name: 'Jane Smith',
                customer_address: '456 Park Ave, Sector 22, Gurgaon',
                customer_phone: '+91 9876543211',
                items: ['Rice 5kg', 'Dal 1kg', 'Oil 1L'],
                total_amount: 450,
                status: 'pending',
                distance: '3.2 km',
                estimated_time: '20 mins'
            },
            {
                id: 3,
                order_id: 'ORD-003',
                customer_name: 'Mike Johnson',
                customer_address: '789 Oak St, Sector 18, Gurgaon',
                customer_phone: '+91 9876543212',
                items: ['Vegetables Mix', 'Fruits Mix'],
                total_amount: 180,
                status: 'picked',
                pickup_time: '2024-01-15 10:30',
                distance: '1.8 km',
                estimated_time: '12 mins'
            },
            {
                id: 4,
                order_id: 'ORD-004',
                customer_name: 'Sarah Wilson',
                customer_address: '321 Pine St, Sector 25, Gurgaon',
                customer_phone: '+91 9876543213',
                items: ['Chicken 1kg', 'Eggs 12pcs'],
                total_amount: 320,
                status: 'delivered',
                pickup_time: '2024-01-15 09:00',
                delivery_time: '2024-01-15 09:25',
                distance: '2.1 km',
                estimated_time: '18 mins'
            }
        ];

        setTimeout(() => {
            setDeliveries(mockDeliveries);
            setLoading(false);
        }, 1000);
    }, []);

    const handlePickDelivery = (deliveryId: number) => {
        setDeliveries(prev => prev.map(d =>
            d.id === deliveryId
                ? { ...d, status: 'picked', pickup_time: new Date().toISOString() }
                : d
        ));
    };

    const handleCompleteDelivery = (deliveryId: number) => {
        setDeliveries(prev => prev.map(d =>
            d.id === deliveryId
                ? { ...d, status: 'delivered', delivery_time: new Date().toISOString() }
                : d
        ));
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50">
                {/* Header Skeleton */}
                <div className="bg-white shadow sticky top-0 z-50">
                    <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
                        <div className="flex items-center space-x-4">
                            <SkeletonLoader type="text" className="h-6 w-48" />
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <div className="w-8 h-8 rounded-full skeleton-loader"></div>
                                <SkeletonLoader type="text" className="h-4 w-32" />
                            </div>
                            <div className="w-20 h-10 skeleton-loader rounded-lg"></div>
                        </div>
                    </div>

                    {/* Navigation Tabs Skeleton */}
                    <div className="border-t border-gray-200">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex space-x-8 py-4">
                                {[...Array(4)].map((_, i) => (
                                    <div key={i} className="py-4">
                                        <SkeletonLoader type="text" className="h-4 w-24" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                    {/* Content Skeleton */}
                    <div className="mb-6">
                        <SkeletonLoader type="text" className="h-7 w-64 mb-2" />
                        <SkeletonLoader type="text" className="h-5 w-80" />
                    </div>

                    <div className="grid gap-6">
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <SkeletonLoader type="text" className="h-5 w-32 mb-2" />
                                        <SkeletonLoader type="text" className="h-4 w-40" />
                                    </div>
                                    <div className="text-right">
                                        <SkeletonLoader type="text" className="h-6 w-20 mb-2" />
                                        <SkeletonLoader type="text" className="h-4 w-24" />
                                    </div>
                                </div>

                                <div className="grid md:grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <SkeletonLoader type="text" className="h-5 w-32 mb-2" />
                                        <SkeletonLoader type="text" className="h-4 w-full mb-1" />
                                        <SkeletonLoader type="text" className="h-4 w-48" />
                                    </div>
                                    <div>
                                        <SkeletonLoader type="text" className="h-5 w-32 mb-2" />
                                        <div className="space-y-1">
                                            {[...Array(3)].map((_, j) => (
                                                <SkeletonLoader key={j} type="text" className="h-4 w-full" />
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <SkeletonLoader type="text" className="h-4 w-16" />
                                        <SkeletonLoader type="text" className="h-4 w-20" />
                                    </div>
                                    <div className="w-24 h-10 skeleton-loader rounded-lg"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </main>
            </div>
        );
    }

    const availableDeliveries = deliveries.filter(d => d.status === 'pending');
    const myDeliveries = deliveries.filter(d => d.status === 'picked' || d.status === 'in_transit');
    const completedDeliveries = deliveries.filter(d => d.status === 'delivered');
    const todayDeliveries = completedDeliveries.filter(d => {
        const today = new Date().toDateString();
        return d.delivery_time && new Date(d.delivery_time).toDateString() === today;
    });

    const totalEarnings = completedDeliveries.reduce((sum, d) => sum + (d.total_amount * 0.1), 0); // 10% commission
    const avgRating = 4.7; // Mock rating

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    <div className="flex items-center space-x-4">
                        <h1 className="text-2xl font-bold text-gray-900">🚚 Delivery Dashboard</h1>
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            {user.photo_url && (
                                <R2Image
                                    src={user.photo_url}
                                    alt="Profile"
                                    className="w-8 h-8 rounded-full"
                                />
                            )}
                            <span className="text-gray-700">Welcome, {user.display_name || user.email}</span>
                        </div>
                        <button
                            onClick={onLogout}
                            className="bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                </div>

                {/* Navigation Tabs */}
                <div className="border-t border-gray-200">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <nav className="flex space-x-8">
                            <button
                                onClick={() => setActiveTab('available')}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'available'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                Available ({availableDeliveries.length})
                            </button>
                            <button
                                onClick={() => setActiveTab('my_deliveries')}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'my_deliveries'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                My Deliveries ({myDeliveries.length})
                            </button>
                            <button
                                onClick={() => setActiveTab('completed')}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'completed'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                Completed ({completedDeliveries.length})
                            </button>
                            <button
                                onClick={() => setActiveTab('stats')}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'stats'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                Statistics
                            </button>
                        </nav>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                {/* Available Deliveries Tab */}
                {activeTab === 'available' && (
                    <div>
                        <div className="mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Available Deliveries</h2>
                            <p className="text-gray-600">Pick up deliveries that are ready for pickup</p>
                        </div>

                        <div className="grid gap-6">
                            {availableDeliveries.map((delivery) => (
                                <div key={delivery.id} className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">Order #{delivery.order_id}</h3>
                                            <p className="text-gray-600">{delivery.customer_name}</p>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-lg font-bold text-green-600">₹{delivery.total_amount}</div>
                                            <div className="text-sm text-gray-500">Earn: ₹{(delivery.total_amount * 0.1).toFixed(0)}</div>
                                        </div>
                                    </div>

                                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <h4 className="font-medium text-gray-900 mb-2">Delivery Address</h4>
                                            <p className="text-gray-600 text-sm">{delivery.customer_address}</p>
                                            <p className="text-gray-600 text-sm mt-1">📞 {delivery.customer_phone}</p>
                                        </div>
                                        <div>
                                            <h4 className="font-medium text-gray-900 mb-2">Items ({delivery.items.length})</h4>
                                            <ul className="text-gray-600 text-sm space-y-1">
                                                {delivery.items.map((item, index) => (
                                                    <li key={index}>• {item}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                                            <span>📍 {delivery.distance}</span>
                                            <span>⏱️ {delivery.estimated_time}</span>
                                        </div>
                                        <button
                                            onClick={() => handlePickDelivery(delivery.id)}
                                            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                                        >
                                            Pick Up
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {availableDeliveries.length === 0 && (
                            <div className="text-center py-12">
                                <div className="text-6xl mb-4">📦</div>
                                <h3 className="text-lg font-medium text-gray-900 mb-2">No deliveries available</h3>
                                <p className="text-gray-500">Check back later for new delivery opportunities</p>
                            </div>
                        )}
                    </div>
                )}

                {/* My Deliveries Tab */}
                {activeTab === 'my_deliveries' && (
                    <div>
                        <div className="mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">My Active Deliveries</h2>
                            <p className="text-gray-600">Deliveries you've picked up and need to complete</p>
                        </div>

                        <div className="grid gap-6">
                            {myDeliveries.map((delivery) => (
                                <div key={delivery.id} className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">Order #{delivery.order_id}</h3>
                                            <p className="text-gray-600">{delivery.customer_name}</p>
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 mt-2">
                                                {delivery.status === 'picked' ? 'Ready for Delivery' : 'In Transit'}
                                            </span>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-lg font-bold text-green-600">₹{delivery.total_amount}</div>
                                            <div className="text-sm text-gray-500">You earn: ₹{(delivery.total_amount * 0.1).toFixed(0)}</div>
                                        </div>
                                    </div>

                                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <h4 className="font-medium text-gray-900 mb-2">Delivery Address</h4>
                                            <p className="text-gray-600 text-sm">{delivery.customer_address}</p>
                                            <p className="text-gray-600 text-sm mt-1">📞 {delivery.customer_phone}</p>
                                        </div>
                                        <div>
                                            <h4 className="font-medium text-gray-900 mb-2">Pickup Details</h4>
                                            <p className="text-gray-600 text-sm">
                                                Picked up: {delivery.pickup_time ? new Date(delivery.pickup_time).toLocaleString() : 'N/A'}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                                            <span>📍 {delivery.distance}</span>
                                            <span>⏱️ {delivery.estimated_time}</span>
                                        </div>
                                        <button
                                            onClick={() => handleCompleteDelivery(delivery.id)}
                                            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                                        >
                                            Mark Delivered
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {myDeliveries.length === 0 && (
                            <div className="text-center py-12">
                                <div className="text-6xl mb-4">🚚</div>
                                <h3 className="text-lg font-medium text-gray-900 mb-2">No active deliveries</h3>
                                <p className="text-gray-500">Pick up some deliveries from the Available tab</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Completed Tab */}
                {activeTab === 'completed' && (
                    <div>
                        <div className="mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Completed Deliveries</h2>
                            <p className="text-gray-600">Your delivery history and earnings</p>
                        </div>

                        <div className="grid gap-4">
                            {completedDeliveries.map((delivery) => (
                                <div key={delivery.id} className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
                                    <div className="flex justify-between items-center">
                                        <div>
                                            <h3 className="font-semibold text-gray-900">Order #{delivery.order_id}</h3>
                                            <p className="text-gray-600 text-sm">{delivery.customer_name}</p>
                                            <p className="text-gray-500 text-xs mt-1">
                                                Delivered: {delivery.delivery_time ? new Date(delivery.delivery_time).toLocaleString() : 'N/A'}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <div className="font-bold text-green-600">+₹{(delivery.total_amount * 0.1).toFixed(0)}</div>
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                Completed
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {completedDeliveries.length === 0 && (
                            <div className="text-center py-12">
                                <div className="text-6xl mb-4">📋</div>
                                <h3 className="text-lg font-medium text-gray-900 mb-2">No completed deliveries</h3>
                                <p className="text-gray-500">Complete some deliveries to see your history here</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Statistics Tab */}
                {activeTab === 'stats' && (
                    <div>
                        <div className="mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Statistics</h2>
                            <div className="flex space-x-4">
                                <button
                                    onClick={() => setSelectedPeriod('day')}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedPeriod === 'day'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                        }`}
                                >
                                    Today
                                </button>
                                <button
                                    onClick={() => setSelectedPeriod('week')}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedPeriod === 'week'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                        }`}
                                >
                                    This Week
                                </button>
                                <button
                                    onClick={() => setSelectedPeriod('month')}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedPeriod === 'month'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                        }`}
                                >
                                    This Month
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">₹</span>
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Total Earnings</dt>
                                                <dd className="text-2xl font-bold text-gray-900">₹{totalEarnings.toFixed(0)}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">📦</span>
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Deliveries</dt>
                                                <dd className="text-2xl font-bold text-gray-900">{completedDeliveries.length}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">⭐</span>
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Rating</dt>
                                                <dd className="text-2xl font-bold text-gray-900">{avgRating}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">📅</span>
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Today</dt>
                                                <dd className="text-2xl font-bold text-gray-900">{todayDeliveries.length}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Overview</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Average delivery time</span>
                                    <span className="font-medium">18 minutes</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Success rate</span>
                                    <span className="font-medium text-green-600">98%</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Customer satisfaction</span>
                                    <span className="font-medium text-green-600">4.7/5.0</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Total distance covered</span>
                                    <span className="font-medium">45.2 km</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}