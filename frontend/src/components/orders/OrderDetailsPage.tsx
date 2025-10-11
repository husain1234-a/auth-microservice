'use client';

import { useState } from 'react';
import { Order, OrderStatus, OrderFeedbackCreate } from '@/types/order';
import { useOrder } from '@/contexts/OrderContext';
import { useUser } from '@/contexts/UserContext';
import R2Image from '@/components/ui/R2Image';

interface OrderDetailsPageProps {
    order: Order;
}

export default function OrderDetailsPage({ order }: OrderDetailsPageProps) {
    const { updateOrderStatus, cancelOrder, requestReturn, submitFeedback } = useOrder();
    const { hasRole } = useUser();
    const [showFeedbackForm, setShowFeedbackForm] = useState(false);
    const [feedbackData, setFeedbackData] = useState<OrderFeedbackCreate>({
        rating: 5,
        comment: ''
    });

    const getStatusColor = (status: OrderStatus) => {
        switch (status) {
            case OrderStatus.PENDING:
                return 'bg-yellow-100 text-yellow-800';
            case OrderStatus.CONFIRMED:
                return 'bg-blue-100 text-blue-800';
            case OrderStatus.PREPARING:
                return 'bg-orange-100 text-orange-800';
            case OrderStatus.OUT_FOR_DELIVERY:
                return 'bg-purple-100 text-purple-800';
            case OrderStatus.DELIVERED:
                return 'bg-green-100 text-green-800';
            case OrderStatus.CANCELLED:
                return 'bg-red-100 text-red-800';
            case OrderStatus.RETURN_REQUESTED:
                return 'bg-gray-100 text-gray-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const getStatusText = (status: OrderStatus) => {
        return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const canCancel = (status: OrderStatus) => {
        return [OrderStatus.PENDING, OrderStatus.CONFIRMED].includes(status);
    };

    const canRequestReturn = (status: OrderStatus) => {
        return status === OrderStatus.DELIVERED;
    };

    const canLeaveFeedback = (status: OrderStatus) => {
        return status === OrderStatus.DELIVERED;
    };

    const handleStatusUpdate = async (newStatus: OrderStatus) => {
        try {
            await updateOrderStatus(order.id, newStatus);
        } catch (error) {
            console.error('Failed to update order status:', error);
        }
    };

    const handleCancel = async () => {
        if (window.confirm('Are you sure you want to cancel this order?')) {
            try {
                await cancelOrder(order.id);
            } catch (error) {
                console.error('Failed to cancel order:', error);
            }
        }
    };

    const handleRequestReturn = async () => {
        if (window.confirm('Are you sure you want to request a return for this order?')) {
            try {
                await requestReturn(order.id);
            } catch (error) {
                console.error('Failed to request return:', error);
            }
        }
    };

    const handleSubmitFeedback = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await submitFeedback(order.id, feedbackData);
            setShowFeedbackForm(false);
            setFeedbackData({ rating: 5, comment: '' });
        } catch (error) {
            console.error('Failed to submit feedback:', error);
        }
    };

    const totalItemsPrice = order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex justify-between items-center mb-6 border-b pb-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Order #{order.id}</h2>
                    <p className="text-gray-500">Placed on {formatDate(order.created_at)}</p>
                </div>
                <div className="flex items-center gap-4">
                    <span className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                        {getStatusText(order.status)}
                    </span>
                </div>
            </div>

            {/* Order Items */}
            <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">Order Items</h3>
                <div className="space-y-4">
                    {order.items.map((item) => (
                        <div key={item.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                            {item.product?.image_url && (
                                <R2Image
                                    src={item.product.image_url}
                                    alt={item.product.name}
                                    className="w-16 h-16 rounded object-cover"
                                />
                            )}
                            <div className="flex-1">
                                <h4 className="font-medium">{item.product?.name}</h4>
                                <p className="text-gray-500 text-sm">{item.product?.description}</p>
                                <p className="text-sm text-gray-500">Unit: {item.product?.unit}</p>
                            </div>
                            <div className="text-right">
                                <p className="font-medium">Qty: {item.quantity}</p>
                                <p className="text-gray-500">₹{item.price.toFixed(2)} each</p>
                                <p className="font-semibold">₹{(item.price * item.quantity).toFixed(2)}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Order Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                {/* Delivery Information */}
                <div>
                    <h3 className="text-lg font-semibold mb-4">Delivery Information</h3>
                    <div className="space-y-3">
                        <div>
                            <p className="text-sm text-gray-500">Delivery Address</p>
                            <p className="font-medium">{order.delivery_address}</p>
                        </div>
                        {order.estimated_delivery_time && (
                            <div>
                                <p className="text-sm text-gray-500">Estimated Delivery</p>
                                <p className="font-medium">{formatDate(order.estimated_delivery_time)}</p>
                            </div>
                        )}
                        {order.delivered_at && (
                            <div>
                                <p className="text-sm text-gray-500">Delivered At</p>
                                <p className="font-medium">{formatDate(order.delivered_at)}</p>
                            </div>
                        )}
                        {order.cancelled_at && (
                            <div>
                                <p className="text-sm text-gray-500">Cancelled At</p>
                                <p className="font-medium">{formatDate(order.cancelled_at)}</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Price Breakdown */}
                <div>
                    <h3 className="text-lg font-semibold mb-4">Price Breakdown</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span>Items Total</span>
                            <span>₹{totalItemsPrice.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Delivery Fee</span>
                            <span>₹{order.delivery_fee.toFixed(2)}</span>
                        </div>
                        <div className="border-t pt-2">
                            <div className="flex justify-between font-semibold text-lg">
                                <span>Total</span>
                                <span>₹{order.total_amount.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 mb-6">
                {canCancel(order.status) && (
                    <button
                        onClick={handleCancel}
                        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                    >
                        Cancel Order
                    </button>
                )}

                {canRequestReturn(order.status) && (
                    <button
                        onClick={handleRequestReturn}
                        className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors"
                    >
                        Request Return
                    </button>
                )}

                {canLeaveFeedback(order.status) && (
                    <button
                        onClick={() => setShowFeedbackForm(true)}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                    >
                        Leave Feedback
                    </button>
                )}

                {hasRole(['admin', 'owner', 'delivery_partner']) && (
                    <div className="flex gap-2">
                        {order.status === OrderStatus.CONFIRMED && (
                            <button
                                onClick={() => handleStatusUpdate(OrderStatus.PREPARING)}
                                className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
                            >
                                Mark Preparing
                            </button>
                        )}
                        {order.status === OrderStatus.PREPARING && (
                            <button
                                onClick={() => handleStatusUpdate(OrderStatus.OUT_FOR_DELIVERY)}
                                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
                            >
                                Out for Delivery
                            </button>
                        )}
                        {order.status === OrderStatus.OUT_FOR_DELIVERY && (
                            <button
                                onClick={() => handleStatusUpdate(OrderStatus.DELIVERED)}
                                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                            >
                                Mark Delivered
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Feedback Form */}
            {showFeedbackForm && (
                <div className="border-t pt-6">
                    <h3 className="text-lg font-semibold mb-4">Leave Feedback</h3>
                    <form onSubmit={handleSubmitFeedback} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Rating
                            </label>
                            <div className="flex space-x-2">
                                {[1, 2, 3, 4, 5].map((rating) => (
                                    <button
                                        key={rating}
                                        type="button"
                                        onClick={() => setFeedbackData(prev => ({ ...prev, rating }))}
                                        className={`text-2xl ${rating <= feedbackData.rating
                                                ? 'text-yellow-400'
                                                : 'text-gray-300'
                                            }`}
                                    >
                                        ★
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Comment (Optional)
                            </label>
                            <textarea
                                value={feedbackData.comment}
                                onChange={(e) => setFeedbackData(prev => ({ ...prev, comment: e.target.value }))}
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Share your experience..."
                            />
                        </div>
                        <div className="flex gap-3">
                            <button
                                type="submit"
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                            >
                                Submit Feedback
                            </button>
                            <button
                                type="button"
                                onClick={() => setShowFeedbackForm(false)}
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </div>
    );
}