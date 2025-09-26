'use client';

import { useState } from 'react';
import { useCart } from '@/contexts/CartContext';
import R2Image from '@/components/ui/R2Image';
import { useRouter } from 'next/navigation';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function CartPage() {
    const { state, removeFromCart, clearCart, applyPromoCode, removePromoCode } = useCart();
    const [promoCode, setPromoCode] = useState('');
    const [isApplying, setIsApplying] = useState(false);
    const router = useRouter();

    const handleApplyPromoCode = async () => {
        if (!promoCode.trim()) return;

        setIsApplying(true);
        try {
            await applyPromoCode(promoCode);
            setPromoCode('');
        } catch (error) {
            console.error('Failed to apply promo code:', error);
        } finally {
            setIsApplying(false);
        }
    };

    const handleRemovePromoCode = async () => {
        try {
            await removePromoCode();
        } catch (error) {
            console.error('Failed to remove promo code:', error);
        }
    };

    const handleCheckout = () => {
        // For now, just clear the cart and show a message
        alert('Checkout functionality would be implemented here!');
        clearCart();
        router.push('/dashboard');
    };

    // Show skeleton loader while cart is loading
    if (!state.cart && state.loading) {
        return (
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between mb-8">
                        <SkeletonLoader type="text" className="h-8 w-64" />
                        <SkeletonLoader type="text" className="h-10 w-24" />
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2">
                            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                                <SkeletonLoader type="cartItem" count={3} />
                            </div>
                        </div>
                        <div className="lg:col-span-1">
                            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
                                <SkeletonLoader type="text" className="h-6 w-32 mb-4" />
                                <div className="space-y-4 mt-4">
                                    <SkeletonLoader type="text" className="h-4 w-full" />
                                    <SkeletonLoader type="text" className="h-4 w-3/4" />
                                    <SkeletonLoader type="text" className="h-4 w-1/2" />
                                    <div className="pt-4">
                                        <SkeletonLoader type="text" className="h-10 w-full" />
                                    </div>
                                    <div className="flex space-x-3">
                                        <SkeletonLoader type="text" className="h-12 flex-1" />
                                        <SkeletonLoader type="text" className="h-12 flex-1" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Show loading message if cart is null and not loading
    if (!state.cart) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-xl">Loading cart...</div>
            </div>
        );
    }

    const { items, subtotal, discount_amount, total_amount, total_items } = state.cart;

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Your Shopping Cart</h1>
                    {items.length > 0 && (
                        <button
                            onClick={clearCart}
                            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                        >
                            Clear Cart
                        </button>
                    )}
                </div>

                {items.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-md p-8 text-center">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-16 w-16 mx-auto text-gray-400 mb-4"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                            />
                        </svg>
                        <h3 className="text-xl font-medium text-gray-900 mb-2">Your cart is empty</h3>
                        <p className="text-gray-500 mb-6">Looks like you haven't added any items to your cart yet.</p>
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                        >
                            Continue Shopping
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Cart Items */}
                        <div className="lg:col-span-2">
                            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                                <ul className="divide-y divide-gray-200">
                                    {items.map((item) => (
                                        <li key={item.id} className="p-6">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0 w-24 h-24 bg-gray-200 rounded-md overflow-hidden">
                                                    {item.product.image_url ? (
                                                        <R2Image
                                                            src={item.product.image_url}
                                                            alt={item.product.name}
                                                            className="w-full h-full object-cover"
                                                            fallbackText={item.product.name.charAt(0)}
                                                        />
                                                    ) : (
                                                        <div className="w-full h-full flex items-center justify-center bg-gray-100">
                                                            <span className="text-2xl font-bold text-gray-400">
                                                                {item.product.name.charAt(0)}
                                                            </span>
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="ml-4 flex-1">
                                                    <div className="flex justify-between">
                                                        <div>
                                                            <h3 className="text-lg font-medium text-gray-900">
                                                                {item.product.name}
                                                            </h3>
                                                            <p className="text-gray-500 text-sm">
                                                                {item.product.unit ? `per ${item.product.unit}` : ''}
                                                            </p>
                                                        </div>
                                                        <div className="text-right">
                                                            <p className="text-lg font-medium text-gray-900">
                                                                ₹{(item.product.price * item.quantity).toFixed(2)}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="mt-2 flex items-center justify-between">
                                                        <div className="flex items-center">
                                                            <span className="text-gray-500 mr-2">Qty:</span>
                                                            <span className="font-medium">{item.quantity}</span>
                                                        </div>
                                                        <button
                                                            onClick={() => removeFromCart(item.product_id)}
                                                            className="text-red-600 hover:text-red-800 text-sm font-medium"
                                                        >
                                                            Remove
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        {/* Order Summary */}
                        <div className="lg:col-span-1">
                            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
                                <h2 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h2>

                                <div className="space-y-4">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Subtotal</span>
                                        <span className="font-medium">₹{subtotal.toFixed(2)}</span>
                                    </div>

                                    {state.cart.promo_code && (
                                        <div className="flex justify-between">
                                            <div>
                                                <span className="text-gray-600">Discount </span>
                                                <span className="text-green-600 font-medium">
                                                    ({state.cart.promo_code.code})
                                                </span>
                                                <button
                                                    onClick={handleRemovePromoCode}
                                                    className="ml-2 text-xs text-red-600 hover:text-red-800"
                                                >
                                                    Remove
                                                </button>
                                            </div>
                                            <span className="font-medium text-green-600">
                                                -₹{discount_amount.toFixed(2)}
                                            </span>
                                        </div>
                                    )}

                                    <div className="border-t border-gray-200 pt-4 flex justify-between">
                                        <span className="text-base font-medium text-gray-900">Total</span>
                                        <span className="text-base font-medium text-gray-900">
                                            ₹{total_amount.toFixed(2)}
                                        </span>
                                    </div>

                                    <div className="border-t border-gray-200 pt-4">
                                        <div className="flex">
                                            <input
                                                type="text"
                                                value={promoCode}
                                                onChange={(e) => setPromoCode(e.target.value)}
                                                placeholder="Promo code"
                                                className="flex-1 border border-gray-300 rounded-l-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            />
                                            <button
                                                onClick={handleApplyPromoCode}
                                                disabled={isApplying || !promoCode.trim()}
                                                className={`px-4 py-2 rounded-r-md font-medium ${isApplying || !promoCode.trim()
                                                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                    : 'bg-blue-600 text-white hover:bg-blue-700'
                                                    }`}
                                            >
                                                {isApplying ? 'Applying...' : 'Apply'}
                                            </button>
                                        </div>
                                    </div>

                                    <button
                                        onClick={handleCheckout}
                                        className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-md"
                                    >
                                        Proceed to Checkout
                                    </button>

                                    <button
                                        onClick={() => router.push('/dashboard')}
                                        className="w-full border border-gray-300 text-gray-700 font-medium py-3 px-4 rounded-md hover:bg-gray-50"
                                    >
                                        Continue Shopping
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}