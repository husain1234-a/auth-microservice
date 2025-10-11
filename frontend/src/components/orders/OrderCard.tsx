'use client';

import { Order, OrderStatus } from '@/types/order';
import { useOrder } from '@/contexts/OrderContext';
import { useUser } from '@/contexts/UserContext';
import R2Image from '@/components/ui/R2Image';

interface OrderCardProps {
    order: Order;
    onViewDetails?: (order: Order) => void;
}

export default function OrderCard({ order, onViewDetails }: OrderCardProps) {
    const { updateOrderStatus, cancelOrder, assignDeliveryPartner } = useOrder();
    const { hasRole, user } = useUser();

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

    const canCancel = (status: OrderStatus) => {
        return [OrderStatus.PENDING, OrderStatus.CONFIRMED].includes(status);
    };

    const canUpdateStatus = (status: OrderStatus) => {
        return hasRole(['admin', 'owner', 'delivery_partner']) &&
            ![OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.REFUNDED].includes(status);
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

    const handleAssignDelivery = async () => {
        const partnerId = prompt('Enter Delivery Partner ID:');
        if (partnerId) {
            try {
                await assignDeliveryPartner(order.id, partnerId);
            } catch (error) {
                console.error('Failed to assign delivery partner:', error);
            }
        }
    };

    const handleRejectDelivery = async () => {
        if (window.confirm('Are you sure you want to reject this delivery assignment?')) {
            try {
                // Remove delivery partner assignment and set back to confirmed
                await assignDeliveryPartner(order.id, '');
                await updateOrderStatus(order.id, OrderStatus.CONFIRMED);
            } catch (error) {
                console.error('Failed to reject delivery:', error);
            }
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            {/* Order Header */}
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                        Order #{order.id}
                    </h3>
                    <p className="text-sm text-gray-500">
                        {formatDate(order.created_at)}
                    </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                    {getStatusText(order.status)}
                </span>
            </div>

            {/* Order Items Preview */}
            <div className="mb-4">
                <div className="flex items-center space-x-3 mb-2">
                    {order.items.slice(0, 3).map((item, index) => (
                        <div key={item.id} className="flex items-center space-x-2">
                            {item.product?.image_url && (
                                <R2Image
                                    src={item.product.image_url}
                                    alt={item.product.name}
                                    className="w-10 h-10 rounded object-cover"
                                />
                            )}
                            <div className="text-sm">
                                <p className="font-medium">{item.product?.name}</p>
                                <p className="text-gray-500">Qty: {item.quantity}</p>
                            </div>
                        </div>
                    ))}
                    {order.items.length > 3 && (
                        <span className="text-sm text-gray-500">
                            +{order.items.length - 3} more items
                        </span>
                    )}
                </div>
            </div>

            {/* Order Details */}
            <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div>
                    <p className="text-gray-500">Total Amount</p>
                    <p className="font-semibold">₹{order.total_amount.toFixed(2)}</p>
                </div>
                <div>
                    <p className="text-gray-500">Delivery Fee</p>
                    <p className="font-semibold">₹{order.delivery_fee.toFixed(2)}</p>
                </div>
            </div>

            {/* Delivery Address */}
            <div className="mb-4">
                <p className="text-sm text-gray-500">Delivery Address</p>
                <p className="text-sm font-medium">{order.delivery_address}</p>
            </div>

            {/* Estimated Delivery Time */}
            {order.estimated_delivery_time && (
                <div className="mb-4">
                    <p className="text-sm text-gray-500">Estimated Delivery</p>
                    <p className="text-sm font-medium">
                        {formatDate(order.estimated_delivery_time)}
                    </p>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-2">
                <button
                    onClick={() => onViewDetails?.(order)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                >
                    View Details
                </button>

                {canCancel(order.status) && (
                    <button
                        onClick={handleCancel}
                        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
                    >
                        Cancel Order
                    </button>
                )}

                {/* Admin/Owner Actions */}
                {hasRole(['admin', 'owner']) && (
                    <div className="flex flex-wrap gap-2">
                        {order.status === OrderStatus.PENDING && (
                            <>
                                <button
                                    onClick={() => handleStatusUpdate(OrderStatus.CONFIRMED)}
                                    className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                                >
                                    ✓ Approve Order
                                </button>
                                <button
                                    onClick={() => handleStatusUpdate(OrderStatus.CANCELLED)}
                                    className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
                                >
                                    ✗ Reject Order
                                </button>
                            </>
                        )}

                        {order.status === OrderStatus.CONFIRMED && (
                            <>
                                <button
                                    onClick={() => handleStatusUpdate(OrderStatus.PREPARING)}
                                    className="px-3 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors text-sm"
                                >
                                    👨‍🍳 Mark Preparing
                                </button>
                                <button
                                    onClick={() => handleAssignDelivery()}
                                    className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                                >
                                    🚚 Assign Delivery
                                </button>
                            </>
                        )}

                        {order.status === OrderStatus.PREPARING && (
                            <button
                                onClick={() => handleStatusUpdate(OrderStatus.OUT_FOR_DELIVERY)}
                                className="px-3 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors text-sm"
                            >
                                🚛 Out for Delivery
                            </button>
                        )}

                        {order.status === OrderStatus.OUT_FOR_DELIVERY && (
                            <button
                                onClick={() => handleStatusUpdate(OrderStatus.DELIVERED)}
                                className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                            >
                                ✅ Mark Delivered
                            </button>
                        )}
                    </div>
                )}

                {/* Delivery Partner Actions */}
                {hasRole(['delivery_partner']) && order.delivery_partner_id === user?.uid && (
                    <div className="flex gap-2">
                        {order.status === OrderStatus.CONFIRMED && (
                            <>
                                <button
                                    onClick={() => handleStatusUpdate(OrderStatus.PREPARING)}
                                    className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                                >
                                    ✓ Accept Delivery
                                </button>
                                <button
                                    onClick={() => handleRejectDelivery()}
                                    className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
                                >
                                    ✗ Reject Delivery
                                </button>
                            </>
                        )}

                        {order.status === OrderStatus.PREPARING && (
                            <button
                                onClick={() => handleStatusUpdate(OrderStatus.OUT_FOR_DELIVERY)}
                                className="px-3 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors text-sm"
                            >
                                🚛 Start Delivery
                            </button>
                        )}

                        {order.status === OrderStatus.OUT_FOR_DELIVERY && (
                            <button
                                onClick={() => handleStatusUpdate(OrderStatus.DELIVERED)}
                                className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                            >
                                ✅ Mark Delivered
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}