'use client';

import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { orderAPI } from '@/lib/orderApi';
import {
    Order,
    OrderCreate,
    OrderStatus,
    OrderTemplate,
    OrderTemplateCreate,
    OrderFeedbackCreate,
    OrderAnalytics
} from '@/types/order';

interface OrderState {
    orders: Order[];
    currentOrder: Order | null;
    templates: OrderTemplate[];
    analytics: OrderAnalytics | null;
    loading: boolean;
    error: string | null;
}

type OrderAction =
    | { type: 'SET_ORDERS'; payload: Order[] }
    | { type: 'SET_CURRENT_ORDER'; payload: Order | null }
    | { type: 'SET_TEMPLATES'; payload: OrderTemplate[] }
    | { type: 'SET_ANALYTICS'; payload: OrderAnalytics }
    | { type: 'SET_LOADING'; payload: boolean }
    | { type: 'SET_ERROR'; payload: string }
    | { type: 'ADD_ORDER'; payload: Order }
    | { type: 'UPDATE_ORDER'; payload: Order }
    | { type: 'REMOVE_ORDER'; payload: number }
    | { type: 'ADD_TEMPLATE'; payload: OrderTemplate }
    | { type: 'REMOVE_TEMPLATE'; payload: number }
    | { type: 'CLEAR_ERROR' };

const initialState: OrderState = {
    orders: [],
    currentOrder: null,
    templates: [],
    analytics: null,
    loading: false,
    error: null
};

function orderReducer(state: OrderState, action: OrderAction): OrderState {
    switch (action.type) {
        case 'SET_ORDERS':
            return { ...state, orders: action.payload, loading: false };
        case 'SET_CURRENT_ORDER':
            return { ...state, currentOrder: action.payload, loading: false };
        case 'SET_TEMPLATES':
            return { ...state, templates: action.payload, loading: false };
        case 'SET_ANALYTICS':
            return { ...state, analytics: action.payload, loading: false };
        case 'SET_LOADING':
            return { ...state, loading: action.payload };
        case 'SET_ERROR':
            return { ...state, error: action.payload, loading: false };
        case 'ADD_ORDER':
            return { ...state, orders: [action.payload, ...state.orders], loading: false };
        case 'UPDATE_ORDER':
            return {
                ...state,
                orders: state.orders.map(order =>
                    order.id === action.payload.id ? action.payload : order
                ),
                currentOrder: state.currentOrder?.id === action.payload.id ? action.payload : state.currentOrder,
                loading: false
            };
        case 'REMOVE_ORDER':
            return {
                ...state,
                orders: state.orders.filter(order => order.id !== action.payload),
                currentOrder: state.currentOrder?.id === action.payload ? null : state.currentOrder,
                loading: false
            };
        case 'ADD_TEMPLATE':
            return { ...state, templates: [action.payload, ...state.templates], loading: false };
        case 'REMOVE_TEMPLATE':
            return {
                ...state,
                templates: state.templates.filter(template => template.id !== action.payload),
                loading: false
            };
        case 'CLEAR_ERROR':
            return { ...state, error: null };
        default:
            return state;
    }
}

const OrderContext = createContext<{
    state: OrderState;
    // Order operations
    createOrder: (orderData: OrderCreate) => Promise<Order>;
    createScheduledOrder: (orderData: OrderCreate) => Promise<Order>;
    fetchMyOrders: (params?: { limit?: number; offset?: number }) => Promise<void>;
    fetchOrder: (orderId: number) => Promise<void>;
    fetchAllOrders: (params?: { user_id?: string; status?: string; limit?: number; offset?: number }) => Promise<void>;
    updateOrderStatus: (orderId: number, status: OrderStatus) => Promise<void>;
    assignDeliveryPartner: (orderId: number, partnerId: string) => Promise<void>;
    cancelOrder: (orderId: number) => Promise<void>;
    requestReturn: (orderId: number) => Promise<void>;
    // Template operations
    createTemplate: (templateData: OrderTemplateCreate) => Promise<void>;
    fetchTemplates: () => Promise<void>;
    deleteTemplate: (templateId: number) => Promise<void>;
    createOrderFromTemplate: (templateId: number, orderData: OrderCreate) => Promise<Order>;
    // Feedback operations
    submitFeedback: (orderId: number, feedbackData: OrderFeedbackCreate) => Promise<void>;
    // Analytics operations
    fetchAnalytics: (startDate: string, endDate: string) => Promise<void>;
    // Utility functions
    clearError: () => void;
} | undefined>(undefined);

// Helper function to extract error message from API response
const extractErrorMessage = (error: any, defaultMessage: string): string => {
    if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
            return error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
            return error.response.data.detail.map((err: any) => err.msg || err.message || 'Validation error').join(', ');
        } else if (typeof error.response.data.detail === 'object') {
            return error.response.data.detail.msg || error.response.data.detail.message || 'Validation error';
        }
    } else if (error.message) {
        return error.message;
    }
    return defaultMessage;
};

export function OrderProvider({ children }: { children: React.ReactNode }) {
    const [state, dispatch] = useReducer(orderReducer, initialState);

    const clearError = useCallback(() => {
        dispatch({ type: 'CLEAR_ERROR' });
    }, []);

    const createOrder = useCallback(async (orderData: OrderCreate): Promise<Order> => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const order = await orderAPI.createOrder(orderData);
            dispatch({ type: 'ADD_ORDER', payload: order });
            return order;
        } catch (error: any) {
            const errorMessage = extractErrorMessage(error, 'Failed to create order');
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
            throw error;
        }
    }, []);

    const createScheduledOrder = useCallback(async (orderData: OrderCreate): Promise<Order> => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const order = await orderAPI.createScheduledOrder(orderData);
            dispatch({ type: 'ADD_ORDER', payload: order });
            return order;
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to create scheduled order';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
            throw error;
        }
    }, []);

    const fetchMyOrders = useCallback(async (params?: { limit?: number; offset?: number }) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const orders = await orderAPI.getMyOrders(params);
            dispatch({ type: 'SET_ORDERS', payload: orders });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch orders';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const fetchOrder = useCallback(async (orderId: number) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const order = await orderAPI.getOrder(orderId);
            dispatch({ type: 'SET_CURRENT_ORDER', payload: order });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch order';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const fetchAllOrders = useCallback(async (params?: { user_id?: string; status?: string; limit?: number; offset?: number }) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const orders = await orderAPI.getAllOrders(params);
            dispatch({ type: 'SET_ORDERS', payload: orders });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch all orders';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const updateOrderStatus = useCallback(async (orderId: number, status: OrderStatus) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const updatedOrder = await orderAPI.updateOrderStatus(orderId, { status });
            dispatch({ type: 'UPDATE_ORDER', payload: updatedOrder });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to update order status';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const assignDeliveryPartner = useCallback(async (orderId: number, partnerId: string) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const updatedOrder = await orderAPI.assignDeliveryPartner(orderId, { delivery_partner_id: partnerId });
            dispatch({ type: 'UPDATE_ORDER', payload: updatedOrder });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to assign delivery partner';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const cancelOrder = useCallback(async (orderId: number) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            await orderAPI.cancelOrder(orderId);
            // Refresh the order to get updated status
            const updatedOrder = await orderAPI.getOrder(orderId);
            dispatch({ type: 'UPDATE_ORDER', payload: updatedOrder });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to cancel order';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const requestReturn = useCallback(async (orderId: number) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const updatedOrder = await orderAPI.requestReturn(orderId);
            dispatch({ type: 'UPDATE_ORDER', payload: updatedOrder });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to request return';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const createTemplate = useCallback(async (templateData: OrderTemplateCreate) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const template = await orderAPI.createTemplate(templateData);
            dispatch({ type: 'ADD_TEMPLATE', payload: template });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to create template';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const fetchTemplates = useCallback(async () => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const templates = await orderAPI.getMyTemplates();
            dispatch({ type: 'SET_TEMPLATES', payload: templates });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch templates';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const deleteTemplate = useCallback(async (templateId: number) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            await orderAPI.deleteTemplate(templateId);
            dispatch({ type: 'REMOVE_TEMPLATE', payload: templateId });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete template';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const createOrderFromTemplate = useCallback(async (templateId: number, orderData: OrderCreate): Promise<Order> => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const order = await orderAPI.createOrderFromTemplate(templateId, orderData);
            dispatch({ type: 'ADD_ORDER', payload: order });
            return order;
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to create order from template';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
            throw error;
        }
    }, []);

    const submitFeedback = useCallback(async (orderId: number, feedbackData: OrderFeedbackCreate) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            await orderAPI.submitOrderFeedback(orderId, feedbackData);
            // Optionally refresh the order to show feedback was submitted
            const updatedOrder = await orderAPI.getOrder(orderId);
            dispatch({ type: 'UPDATE_ORDER', payload: updatedOrder });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to submit feedback';
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    const fetchAnalytics = useCallback(async (startDate: string, endDate: string) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            console.log('Fetching analytics for:', { startDate, endDate });

            const [revenue, deliveryPerformance, topCustomers, cancellationRate] = await Promise.all([
                orderAPI.getRevenueAnalytics({ start_date: startDate, end_date: endDate }),
                orderAPI.getDeliveryPerformance(),
                orderAPI.getTopCustomers(10),
                orderAPI.getCancellationRate(30)
            ]);

            console.log('Analytics API responses:', {
                revenue,
                deliveryPerformance,
                topCustomers,
                cancellationRate
            });

            const analytics: OrderAnalytics = {
                revenue,
                delivery_performance: deliveryPerformance,
                top_customers: topCustomers,
                cancellation_rate: cancellationRate
            };

            console.log('Final analytics object:', analytics);
            dispatch({ type: 'SET_ANALYTICS', payload: analytics });
        } catch (error: any) {
            const errorMessage = extractErrorMessage(error, 'Failed to fetch analytics');
            dispatch({ type: 'SET_ERROR', payload: errorMessage });
        }
    }, []);

    return (
        <OrderContext.Provider
            value={{
                state,
                createOrder,
                createScheduledOrder,
                fetchMyOrders,
                fetchOrder,
                fetchAllOrders,
                updateOrderStatus,
                assignDeliveryPartner,
                cancelOrder,
                requestReturn,
                createTemplate,
                fetchTemplates,
                deleteTemplate,
                createOrderFromTemplate,
                submitFeedback,
                fetchAnalytics,
                clearError
            }}
        >
            {children}
        </OrderContext.Provider>
    );
}

export function useOrder() {
    const context = useContext(OrderContext);
    if (context === undefined) {
        throw new Error('useOrder must be used within an OrderProvider');
    }
    return context;
}