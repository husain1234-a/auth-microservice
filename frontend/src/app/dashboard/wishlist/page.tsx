'use client';

import { useCart } from '@/contexts/CartContext';
import R2Image from '@/components/ui/R2Image';
import { useRouter } from 'next/navigation';
import SkeletonLoader from '@/components/SkeletonLoader';

export default function WishlistPage() {
    const { state, removeFromWishlist, clearWishlist, moveToCart } = useCart();
    const router = useRouter();

    // Show skeleton loader while wishlist is loading
    if (!state.wishlist && state.loading) {
        return (
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between mb-8">
                        <SkeletonLoader type="text" className="h-8 w-64" />
                        <SkeletonLoader type="text" className="h-10 w-24" />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        <SkeletonLoader type="product" count={4} />
                    </div>
                </div>
            </div>
        );
    }

    // Show loading message if wishlist is null and not loading
    if (!state.wishlist) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-xl">Loading wishlist...</div>
            </div>
        );
    }

    const { items } = state.wishlist;

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Your Wishlist</h1>
                    {items.length > 0 && (
                        <button
                            onClick={clearWishlist}
                            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                        >
                            Clear Wishlist
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
                                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                            />
                        </svg>
                        <h3 className="text-xl font-medium text-gray-900 mb-2">Your wishlist is empty</h3>
                        <p className="text-gray-500 mb-6">Looks like you haven't added any items to your wishlist yet.</p>
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                        >
                            Continue Shopping
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {items.map((item) => (
                            <div key={item.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                                {item.product.image_url ? (
                                    <R2Image
                                        src={item.product.image_url}
                                        alt={item.product.name}
                                        className="w-full h-48 object-cover"
                                        fallbackText={item.product.name}
                                    />
                                ) : (
                                    <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
                                        <div className="text-center">
                                            <div className="text-4xl mb-2">📦</div>
                                            <div className="text-sm text-gray-500">{item.product.name}</div>
                                        </div>
                                    </div>
                                )}
                                <div className="p-4">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.product.name}</h3>
                                    {item.product.description && (
                                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{item.product.description}</p>
                                    )}
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-2">
                                            <span className="text-xl font-bold text-green-600">₹{item.product.price}</span>
                                            {item.product.mrp && item.product.mrp > item.product.price && (
                                                <span className="text-sm text-gray-500 line-through">₹{item.product.mrp}</span>
                                            )}
                                        </div>
                                        {item.product.unit && (
                                            <span className="text-sm text-gray-500">per {item.product.unit}</span>
                                        )}
                                    </div>
                                    <div className="mt-3 flex items-center justify-between">
                                        <span className={`text-sm ${item.product.stock_quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {item.product.stock_quantity > 0 ? `${item.product.stock_quantity} in stock` : 'Out of stock'}
                                        </span>
                                    </div>
                                    <div className="mt-4 flex space-x-2">
                                        <button
                                            onClick={() => moveToCart(item.product_id)}
                                            disabled={item.product.stock_quantity === 0}
                                            className={`flex-1 px-3 py-2 rounded text-sm font-medium ${item.product.stock_quantity > 0
                                                ? 'bg-blue-600 text-white hover:bg-blue-700'
                                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                }`}
                                        >
                                            Move to Cart
                                        </button>
                                        <button
                                            onClick={() => removeFromWishlist(item.product_id)}
                                            className="px-3 py-2 rounded text-sm font-medium text-red-600 hover:text-red-800"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}