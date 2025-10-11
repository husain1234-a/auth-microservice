'use client';

import { useState } from 'react';
import { OrderCreate } from '@/types/order';
import { useOrder } from '@/contexts/OrderContext';
import { useCart } from '@/contexts/CartContext';

interface CreateOrderFormProps {
    onSuccess?: (orderId: number) => void;
    onCancel?: () => void;
}

export default function CreateOrderForm({ onSuccess, onCancel }: CreateOrderFormProps) {
    const { createOrder, createScheduledOrder, state: orderState } = useOrder();
    const { state: cartState } = useCart();
    const [formData, setFormData] = useState<OrderCreate>({
        delivery_address: '',
        delivery_latitude: '',
        delivery_longitude: '',
        scheduled_for: ''
    });
    const [isScheduled, setIsScheduled] = useState(false);
    const [useCurrentLocation, setUseCurrentLocation] = useState(false);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const getCurrentLocation = () => {
        if (navigator.geolocation) {
            setUseCurrentLocation(true);
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setFormData(prev => ({
                        ...prev,
                        delivery_latitude: position.coords.latitude.toString(),
                        delivery_longitude: position.coords.longitude.toString()
                    }));
                    setUseCurrentLocation(false);
                },
                (error) => {
                    console.error('Error getting location:', error);
                    setUseCurrentLocation(false);
                    alert('Unable to get your current location. Please enter coordinates manually.');
                }
            );
        } else {
            alert('Geolocation is not supported by this browser.');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!cartState.cart || cartState.cart.items.length === 0) {
            alert('Your cart is empty. Please add items before placing an order.');
            return;
        }

        try {
            const orderData: OrderCreate = {
                delivery_address: formData.delivery_address,
                delivery_latitude: formData.delivery_latitude || undefined,
                delivery_longitude: formData.delivery_longitude || undefined,
                scheduled_for: isScheduled && formData.scheduled_for ? formData.scheduled_for : undefined
            };

            const order = isScheduled
                ? await createScheduledOrder(orderData)
                : await createOrder(orderData);

            onSuccess?.(order.id);
        } catch (error) {
            console.error('Failed to create order:', error);
        }
    };

    const minDateTime = new Date();
    minDateTime.setHours(minDateTime.getHours() + 1); // Minimum 1 hour from now
    const minDateTimeString = minDateTime.toISOString().slice(0, 16);

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Order</h2>

            {/* Cart Summary */}
            {cartState.cart && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-semibold mb-2">Order Summary</h3>
                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span>Items ({cartState.cart.total_items})</span>
                            <span>₹{cartState.cart.total_amount.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Delivery Fee</span>
                            <span>₹50.00</span>
                        </div>
                        <div className="border-t pt-2">
                            <div className="flex justify-between font-semibold">
                                <span>Total</span>
                                <span>₹{(cartState.cart.total_amount + 50.00).toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Delivery Address */}
                <div>
                    <label htmlFor="delivery_address" className="block text-sm font-medium text-gray-700 mb-2">
                        Delivery Address *
                    </label>
                    <textarea
                        id="delivery_address"
                        name="delivery_address"
                        value={formData.delivery_address}
                        onChange={handleInputChange}
                        required
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter your complete delivery address..."
                    />
                </div>

                {/* Location Coordinates */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="delivery_latitude" className="block text-sm font-medium text-gray-700 mb-2">
                            Latitude (Optional)
                        </label>
                        <input
                            type="text"
                            id="delivery_latitude"
                            name="delivery_latitude"
                            value={formData.delivery_latitude}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="e.g., 40.7128"
                        />
                    </div>
                    <div>
                        <label htmlFor="delivery_longitude" className="block text-sm font-medium text-gray-700 mb-2">
                            Longitude (Optional)
                        </label>
                        <input
                            type="text"
                            id="delivery_longitude"
                            name="delivery_longitude"
                            value={formData.delivery_longitude}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="e.g., -74.0060"
                        />
                    </div>
                </div>

                {/* Get Current Location Button */}
                <div>
                    <button
                        type="button"
                        onClick={getCurrentLocation}
                        disabled={useCurrentLocation}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-400"
                    >
                        {useCurrentLocation ? 'Getting Location...' : 'Use Current Location'}
                    </button>
                </div>

                {/* Scheduled Delivery */}
                <div>
                    <div className="flex items-center mb-3">
                        <input
                            type="checkbox"
                            id="scheduled"
                            checked={isScheduled}
                            onChange={(e) => setIsScheduled(e.target.checked)}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor="scheduled" className="ml-2 text-sm font-medium text-gray-700">
                            Schedule delivery for later
                        </label>
                    </div>

                    {isScheduled && (
                        <div>
                            <label htmlFor="scheduled_for" className="block text-sm font-medium text-gray-700 mb-2">
                                Scheduled Delivery Time
                            </label>
                            <input
                                type="datetime-local"
                                id="scheduled_for"
                                name="scheduled_for"
                                value={formData.scheduled_for}
                                onChange={handleInputChange}
                                min={minDateTimeString}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                    )}
                </div>

                {/* Error Display */}
                {orderState.error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-red-600 text-sm">{orderState.error}</p>
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-4">
                    <button
                        type="submit"
                        disabled={orderState.loading || !formData.delivery_address}
                        className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400 font-medium"
                    >
                        {orderState.loading ? 'Creating Order...' : (isScheduled ? 'Schedule Order' : 'Place Order')}
                    </button>

                    {onCancel && (
                        <button
                            type="button"
                            onClick={onCancel}
                            className="px-6 py-3 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors font-medium"
                        >
                            Cancel
                        </button>
                    )}
                </div>
            </form>
        </div>
    );
}