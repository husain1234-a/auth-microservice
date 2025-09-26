'use client';

import { createContext, useContext, useReducer, useEffect } from 'react';
import { cartAPI, Cart, Wishlist } from '@/lib/cartApi';

// Define types
interface CartState {
    cart: Cart | null;
    wishlist: Wishlist | null;
    loading: boolean;
    error: string | null;
}

type CartAction =
    | { type: 'SET_CART'; payload: Cart }
    | { type: 'SET_WISHLIST'; payload: Wishlist }
    | { type: 'SET_LOADING'; payload: boolean }
    | { type: 'SET_ERROR'; payload: string }
    | { type: 'CLEAR_CART' }
    | { type: 'CLEAR_WISHLIST' };

// Initial state
const initialState: CartState = {
    cart: null,
    wishlist: null,
    loading: false,
    error: null
};

// Reducer
function cartReducer(state: CartState, action: CartAction): CartState {
    switch (action.type) {
        case 'SET_CART':
            return { ...state, cart: action.payload, loading: false };
        case 'SET_WISHLIST':
            return { ...state, wishlist: action.payload, loading: false };
        case 'SET_LOADING':
            return { ...state, loading: action.payload };
        case 'SET_ERROR':
            return { ...state, error: action.payload, loading: false };
        case 'CLEAR_CART':
            return { ...state, cart: null };
        case 'CLEAR_WISHLIST':
            return { ...state, wishlist: null };
        default:
            return state;
    }
}

// Create context
const CartContext = createContext<{
    state: CartState;
    fetchCart: () => Promise<void>;
    fetchWishlist: () => Promise<void>;
    addToCart: (productId: number, quantity?: number) => Promise<void>;
    removeFromCart: (productId: number) => Promise<void>;
    clearCart: () => Promise<void>;
    applyPromoCode: (code: string) => Promise<void>;
    removePromoCode: () => Promise<void>;
    addToWishlist: (productId: number) => Promise<void>;
    removeFromWishlist: (productId: number) => Promise<void>;
    moveToCart: (productId: number, quantity?: number) => Promise<void>;
    clearWishlist: () => Promise<void>;
} | undefined>(undefined);

// Provider component
export function CartProvider({ children }: { children: React.ReactNode }) {
    const [state, dispatch] = useReducer(cartReducer, initialState);

    const fetchCart = async () => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const cart = await cartAPI.getCart();
            dispatch({ type: 'SET_CART', payload: cart });
        } catch (error: any) {
            console.error('Failed to fetch cart:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to fetch cart' });
        }
    };

    const fetchWishlist = async () => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const wishlist = await cartAPI.getWishlist();
            dispatch({ type: 'SET_WISHLIST', payload: wishlist });
        } catch (error: any) {
            console.error('Failed to fetch wishlist:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to fetch wishlist' });
        }
    };

    const addToCart = async (productId: number, quantity: number = 1) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const cart = await cartAPI.addToCart(productId, quantity);
            dispatch({ type: 'SET_CART', payload: cart });
        } catch (error: any) {
            console.error('Failed to add to cart:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to add to cart' });
        }
    };

    const removeFromCart = async (productId: number) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const cart = await cartAPI.removeFromCart(productId);
            dispatch({ type: 'SET_CART', payload: cart });
        } catch (error: any) {
            console.error('Failed to remove from cart:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to remove from cart' });
        }
    };

    const clearCart = async () => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const cart = await cartAPI.clearCart();
            dispatch({ type: 'SET_CART', payload: cart });
        } catch (error: any) {
            console.error('Failed to clear cart:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to clear cart' });
        }
    };

    const applyPromoCode = async (code: string) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const cart = await cartAPI.applyPromoCode(code);
            dispatch({ type: 'SET_CART', payload: cart });
        } catch (error: any) {
            console.error('Failed to apply promo code:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to apply promo code' });
        }
    };

    const removePromoCode = async () => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const cart = await cartAPI.removePromoCode();
            dispatch({ type: 'SET_CART', payload: cart });
        } catch (error: any) {
            console.error('Failed to remove promo code:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to remove promo code' });
        }
    };

    const addToWishlist = async (productId: number) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const wishlist = await cartAPI.addToWishlist(productId);
            dispatch({ type: 'SET_WISHLIST', payload: wishlist });
        } catch (error: any) {
            console.error('Failed to add to wishlist:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to add to wishlist' });
        }
    };

    const removeFromWishlist = async (productId: number) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            const wishlist = await cartAPI.removeFromWishlist(productId);
            dispatch({ type: 'SET_WISHLIST', payload: wishlist });
        } catch (error: any) {
            console.error('Failed to remove from wishlist:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to remove from wishlist' });
        }
    };

    const moveToCart = async (productId: number, quantity: number = 1) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            await cartAPI.moveToCart(productId, quantity);
            // Refresh both cart and wishlist
            await fetchCart();
            await fetchWishlist();
        } catch (error: any) {
            console.error('Failed to move to cart:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to move to cart' });
        }
    };

    const clearWishlist = async () => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            await cartAPI.clearWishlist();
            dispatch({ type: 'CLEAR_WISHLIST' });
        } catch (error: any) {
            console.error('Failed to clear wishlist:', error);
            dispatch({ type: 'SET_ERROR', payload: error.message || 'Failed to clear wishlist' });
        }
    };

    // Load cart and wishlist on initial render
    useEffect(() => {
        fetchCart();
        fetchWishlist();
    }, []);

    return (
        <CartContext.Provider
            value={{
                state,
                fetchCart,
                fetchWishlist,
                addToCart,
                removeFromCart,
                clearCart,
                applyPromoCode,
                removePromoCode,
                addToWishlist,
                removeFromWishlist,
                moveToCart,
                clearWishlist
            }}
        >
            {children}
        </CartContext.Provider>
    );
}

// Hook to use cart context
export function useCart() {
    const context = useContext(CartContext);
    if (context === undefined) {
        throw new Error('useCart must be used within a CartProvider');
    }
    return context;
}