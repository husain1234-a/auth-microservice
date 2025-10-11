// Order types based on the backend order service specification

export enum OrderStatus {
    PENDING = "pending",
    CONFIRMED = "confirmed",
    PREPARING = "preparing",
    OUT_FOR_DELIVERY = "out_for_delivery",
    DELIVERED = "delivered",
    CANCELLED = "cancelled",
    RETURN_REQUESTED = "return_requested",
    RETURN_APPROVED = "return_approved",
    PICKED_UP = "picked_up",
    REFUNDED = "refunded"
}

export interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    mrp: number;
    category_id: number;
    image_url: string;
    stock_quantity: number;
    unit: string;
    is_active: boolean;
    created_at: string;
}

export interface OrderItem {
    id: number;
    product_id: number;
    quantity: number;
    price: number;
    product?: Product;
}

export interface Order {
    id: number;
    user_id: string;
    delivery_partner_id?: string;
    total_amount: number;
    delivery_fee: number;
    status: OrderStatus;
    delivery_address: string;
    delivery_latitude?: string;
    delivery_longitude?: string;
    estimated_delivery_time?: string;
    delivered_at?: string;
    cancelled_at?: string;
    scheduled_for?: string;
    created_at: string;
    updated_at?: string;
    items: OrderItem[];
}

export interface OrderCreate {
    delivery_address: string;
    delivery_latitude?: string;
    delivery_longitude?: string;
    scheduled_for?: string;
}

export interface OrderStatusUpdate {
    status: OrderStatus;
}

export interface AssignDeliveryPartnerRequest {
    delivery_partner_id: string;
}

export interface OrderCancelResponse {
    success: boolean;
    message: string;
    refund_initiated: boolean;
}

export interface OrderItemsUpdate {
    items: Array<{
        product_id: number;
        quantity: number;
    }>;
}

export interface OrderTemplate {
    id: number;
    user_id: string;
    name: string;
    items: Array<{
        product_id: number;
        quantity: number;
    }>;
    created_at: string;
    updated_at: string;
}

export interface OrderTemplateCreate {
    name: string;
    items: Array<{
        product_id: number;
        quantity: number;
    }>;
}

export interface BulkStatusUpdate {
    order_ids: number[];
    status: OrderStatus;
}

export interface BulkAssignDelivery {
    order_ids: number[];
    delivery_partner_id: string;
}

export interface OrderFeedbackCreate {
    rating: number;
    comment?: string;
}

export interface OrderFeedbackResponse {
    id: number;
    order_id: number;
    rating: number;
    comment?: string;
    created_at: string;
}

export interface DeliveryLocation {
    order_id: number;
    latitude: string;
    longitude: string;
    last_updated: string;
}

export interface OrderAnalytics {
    revenue: Array<{
        date: string;
        total_revenue: number;
        order_count: number;
        average_delivery_time?: number;
    }>;
    delivery_performance: {
        average_delivery_time: number;
        on_time_delivery_rate: number;
        total_deliveries: number;
    };
    top_customers: Array<{
        user_id: string;
        order_count: number;
        total_spent: number;
    }>;
    cancellation_rate: {
        period: string;
        cancellation_rate: number;
        total_orders: number;
        cancelled_orders: number;
    };
}