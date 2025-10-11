'use client';

import { useState, useEffect } from 'react';
import { OrderTemplate, OrderTemplateCreate, OrderCreate } from '@/types/order';
import { useOrder } from '@/contexts/OrderContext';
import { useCart } from '@/contexts/CartContext';
import SkeletonLoader from '@/components/SkeletonLoader';

interface OrderTemplatesProps {
    onOrderCreated?: (orderId: number) => void;
}

export default function OrderTemplates({ onOrderCreated }: OrderTemplatesProps) {
    const { state, fetchTemplates, createTemplate, deleteTemplate, createOrderFromTemplate, clearError } = useOrder();
    const { state: cartState } = useCart();
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [showOrderForm, setShowOrderForm] = useState<OrderTemplate | null>(null);
    const [templateForm, setTemplateForm] = useState<OrderTemplateCreate>({
        name: '',
        items: []
    });
    const [orderForm, setOrderForm] = useState<OrderCreate>({
        delivery_address: '',
        delivery_latitude: '',
        delivery_longitude: ''
    });

    useEffect(() => {
        fetchTemplates();
    }, []);

    useEffect(() => {
        if (state.error) {
            const timer = setTimeout(() => {
                clearError();
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [state.error, clearError]);

    const handleCreateTemplate = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!cartState.cart || cartState.cart.items.length === 0) {
            alert('Your cart is empty. Please add items before creating a template.');
            return;
        }

        try {
            const templateData: OrderTemplateCreate = {
                name: templateForm.name,
                items: cartState.cart.items.map(item => ({
                    product_id: item.product_id,
                    quantity: item.quantity
                }))
            };

            await createTemplate(templateData);
            setTemplateForm({ name: '', items: [] });
            setShowCreateForm(false);
        } catch (error) {
            console.error('Failed to create template:', error);
        }
    };

    const handleDeleteTemplate = async (templateId: number) => {
        if (window.confirm('Are you sure you want to delete this template?')) {
            try {
                await deleteTemplate(templateId);
            } catch (error) {
                console.error('Failed to delete template:', error);
            }
        }
    };

    const handleCreateOrderFromTemplate = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!showOrderForm) return;

        try {
            const order = await createOrderFromTemplate(showOrderForm.id, orderForm);
            setShowOrderForm(null);
            setOrderForm({
                delivery_address: '',
                delivery_latitude: '',
                delivery_longitude: ''
            });
            onOrderCreated?.(order.id);
        } catch (error) {
            console.error('Failed to create order from template:', error);
        }
    };

    const getCurrentLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setOrderForm(prev => ({
                        ...prev,
                        delivery_latitude: position.coords.latitude.toString(),
                        delivery_longitude: position.coords.longitude.toString()
                    }));
                },
                (error) => {
                    console.error('Error getting location:', error);
                    alert('Unable to get your current location. Please enter coordinates manually.');
                }
            );
        } else {
            alert('Geolocation is not supported by this browser.');
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Order Templates</h2>
                <button
                    onClick={() => setShowCreateForm(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                    Create Template
                </button>
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

            {/* Create Template Form */}
            {showCreateForm && (
                <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-lg font-semibold mb-4">Create New Template</h3>
                    <form onSubmit={handleCreateTemplate} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Template Name
                            </label>
                            <input
                                type="text"
                                value={templateForm.name}
                                onChange={(e) => setTemplateForm(prev => ({ ...prev, name: e.target.value }))}
                                required
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="e.g., Weekly Grocery Pack"
                            />
                        </div>

                        {/* Cart Items Preview */}
                        {cartState.cart && cartState.cart.items.length > 0 && (
                            <div>
                                <p className="text-sm font-medium text-gray-700 mb-2">
                                    Items from your cart ({cartState.cart.items.length} items):
                                </p>
                                <div className="max-h-32 overflow-y-auto space-y-1">
                                    {cartState.cart.items.map((item, index) => (
                                        <div key={index} className="text-sm text-gray-600 flex justify-between">
                                            <span>{item.product.name}</span>
                                            <span>Qty: {item.quantity}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="flex gap-3">
                            <button
                                type="submit"
                                disabled={state.loading || !templateForm.name}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                            >
                                {state.loading ? 'Creating...' : 'Create Template'}
                            </button>
                            <button
                                type="button"
                                onClick={() => setShowCreateForm(false)}
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Templates List */}
            {state.loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[...Array(3)].map((_, index) => (
                        <SkeletonLoader key={index} />
                    ))}
                </div>
            ) : (
                <>
                    {state.templates.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {state.templates.map((template) => (
                                <div key={template.id} className="bg-white p-6 rounded-lg shadow-md border">
                                    <div className="flex justify-between items-start mb-4">
                                        <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                                        <button
                                            onClick={() => handleDeleteTemplate(template.id)}
                                            className="text-red-400 hover:text-red-600"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>

                                    <div className="mb-4">
                                        <p className="text-sm text-gray-500 mb-2">
                                            {template.items.length} items
                                        </p>
                                        <p className="text-xs text-gray-400">
                                            Created: {new Date(template.created_at).toLocaleDateString()}
                                        </p>
                                    </div>

                                    <button
                                        onClick={() => setShowOrderForm(template)}
                                        className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                                    >
                                        Create Order
                                    </button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4">📋</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
                            <p className="text-gray-500">Create your first order template to quickly reorder your favorite items.</p>
                        </div>
                    )}
                </>
            )}

            {/* Create Order from Template Modal */}
            {showOrderForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-md w-full p-6">
                        <h3 className="text-lg font-semibold mb-4">
                            Create Order from "{showOrderForm.name}"
                        </h3>

                        <form onSubmit={handleCreateOrderFromTemplate} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Delivery Address *
                                </label>
                                <textarea
                                    value={orderForm.delivery_address}
                                    onChange={(e) => setOrderForm(prev => ({ ...prev, delivery_address: e.target.value }))}
                                    required
                                    rows={3}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Enter your complete delivery address..."
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Latitude
                                    </label>
                                    <input
                                        type="text"
                                        value={orderForm.delivery_latitude}
                                        onChange={(e) => setOrderForm(prev => ({ ...prev, delivery_latitude: e.target.value }))}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="40.7128"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Longitude
                                    </label>
                                    <input
                                        type="text"
                                        value={orderForm.delivery_longitude}
                                        onChange={(e) => setOrderForm(prev => ({ ...prev, delivery_longitude: e.target.value }))}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="-74.0060"
                                    />
                                </div>
                            </div>

                            <button
                                type="button"
                                onClick={getCurrentLocation}
                                className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                            >
                                Use Current Location
                            </button>

                            <div className="flex gap-3">
                                <button
                                    type="submit"
                                    disabled={state.loading || !orderForm.delivery_address}
                                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                                >
                                    {state.loading ? 'Creating...' : 'Create Order'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowOrderForm(null)}
                                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}