'use client';

import { useEffect, useState } from 'react';
import { productAPI, Product, Category } from '@/lib/productApi';

interface User {
    uid: string;
    email?: string;
    phone_number?: string;
    display_name?: string;
    photo_url?: string;
    role: string;
}

interface CustomerDashboardProps {
    user: User;
    onLogout: () => void;
}

export default function CustomerDashboard({ user, onLogout }: CustomerDashboardProps) {
    const [products, setProducts] = useState<Product[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [productsResponse, categoriesResponse] = await Promise.all([
                    productAPI.getProducts({ limit: 12 }),
                    productAPI.getCategories({ limit: 20 })
                ]);

                setProducts(productsResponse.products || productsResponse);
                setCategories(categoriesResponse.categories || categoriesResponse);
            } catch (error) {
                console.error('Failed to fetch data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const filteredProducts = selectedCategory
        ? products.filter(product => product.category_id === selectedCategory)
        : products;

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-xl">Loading products...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-gray-900">Welcome to GroFast</h1>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            {user.photo_url && (
                                <img
                                    src={user.photo_url}
                                    alt="Profile"
                                    className="w-8 h-8 rounded-full"
                                />
                            )}
                            <span className="text-gray-700">Hi, {user.display_name || user.email}</span>
                        </div>
                        <button
                            onClick={onLogout}
                            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                {/* Categories Filter */}
                <div className="mb-6">
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Shop by Category</h2>
                    <div className="flex flex-wrap gap-2">
                        <button
                            onClick={() => setSelectedCategory(null)}
                            className={`px-4 py-2 rounded-full text-sm font-medium ${selectedCategory === null
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                        >
                            All Products
                        </button>
                        {categories.map((category) => (
                            <button
                                key={category.id}
                                onClick={() => setSelectedCategory(category.id)}
                                className={`px-4 py-2 rounded-full text-sm font-medium ${selectedCategory === category.id
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                    }`}
                            >
                                {category.name}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Products Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    {filteredProducts.map((product) => (
                        <div key={product.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                            {product.image_url ? (
                                <img
                                    src={product.image_url}
                                    alt={product.name}
                                    className="w-full h-48 object-cover"
                                    onError={(e) => {
                                        const target = e.target as HTMLImageElement;
                                        target.src = `https://via.placeholder.com/400x300/f3f4f6/9ca3af?text=${encodeURIComponent(product.name)}`;
                                    }}
                                />
                            ) : (
                                <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
                                    <div className="text-center">
                                        <div className="text-4xl mb-2">📦</div>
                                        <div className="text-sm text-gray-500">{product.name}</div>
                                    </div>
                                </div>
                            )}
                            <div className="p-4">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">{product.name}</h3>
                                {product.description && (
                                    <p className="text-gray-600 text-sm mb-3 line-clamp-2">{product.description}</p>
                                )}
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-xl font-bold text-green-600">₹{product.price}</span>
                                        {product.mrp && product.mrp > product.price && (
                                            <span className="text-sm text-gray-500 line-through">₹{product.mrp}</span>
                                        )}
                                    </div>
                                    {product.unit && (
                                        <span className="text-sm text-gray-500">per {product.unit}</span>
                                    )}
                                </div>
                                <div className="mt-3 flex items-center justify-between">
                                    <span className={`text-sm ${product.stock_quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'Out of stock'}
                                    </span>
                                    <button
                                        disabled={product.stock_quantity === 0}
                                        className={`px-4 py-2 rounded text-sm font-medium ${product.stock_quantity > 0
                                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                            }`}
                                    >
                                        Add to Cart
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {filteredProducts.length === 0 && (
                    <div className="text-center py-12">
                        <p className="text-gray-500 text-lg">No products found in this category.</p>
                    </div>
                )}

                {/* User Profile Section */}
                <div className="mt-12 bg-white shadow overflow-hidden sm:rounded-lg">
                    <div className="px-4 py-5 sm:px-6">
                        <h3 className="text-lg leading-6 font-medium text-gray-900">My Profile</h3>
                        <p className="mt-1 max-w-2xl text-sm text-gray-500">Your account information.</p>
                    </div>
                    <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                        <dl className="sm:divide-y sm:divide-gray-200">
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Name</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    {user.display_name || 'N/A'}
                                </dd>
                            </div>
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Email</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    {user.email || 'N/A'}
                                </dd>
                            </div>
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Phone</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    {user.phone_number || 'Not provided'}
                                </dd>
                            </div>
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Account Type</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                        Customer
                                    </span>
                                </dd>
                            </div>
                        </dl>
                    </div>
                </div>
            </main>
        </div>
    );
}