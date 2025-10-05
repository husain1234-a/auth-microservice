'use client';

import { useEffect, useState } from 'react';
import { productAPI, Product, Category } from '@/lib/productApi';
import SkeletonLoader from '@/components/SkeletonLoader';
import R2Image from '@/components/ui/R2Image';

interface User {
    uid: string;
    email?: string;
    phone_number?: string;
    display_name?: string;
    photo_url?: string;
    role: string;
}

interface OwnerDashboardProps {
    user: User;
    onLogout: () => void;
}

export default function OwnerDashboard({ user, onLogout }: OwnerDashboardProps) {
    const [products, setProducts] = useState<Product[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'products' | 'categories'>('overview');

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Updated to properly handle the direct array responses from the API
                const productsResponse = await productAPI.getProducts({ limit: 100 });
                const categoriesResponse = await productAPI.getCategories({ limit: 50 });

                setProducts(productsResponse);
                setCategories(categoriesResponse);
            } catch (error) {
                console.error('Failed to fetch data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleDeleteProduct = async (productId: number) => {
        if (confirm('Are you sure you want to delete this product?')) {
            try {
                await productAPI.deleteProduct(productId);
                setProducts(products.filter(p => p.id !== productId));
            } catch (error) {
                console.error('Failed to delete product:', error);
                alert('Failed to delete product');
            }
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50">
                {/* Header Skeleton */}
                <div className="bg-white shadow sticky top-0 z-50">
                    <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
                        <div className="flex items-center space-x-4">
                            <SkeletonLoader type="text" className="h-6 w-48" />
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <div className="w-8 h-8 rounded-full skeleton-loader"></div>
                                <SkeletonLoader type="text" className="h-4 w-32" />
                            </div>
                            <div className="w-20 h-10 skeleton-loader rounded-lg"></div>
                        </div>
                    </div>

                    {/* Navigation Tabs Skeleton */}
                    <div className="border-t border-gray-200">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex space-x-8 py-4">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className="py-4">
                                        <SkeletonLoader type="text" className="h-4 w-24" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                    {/* Content Skeleton */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 rounded-full skeleton-loader"></div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <SkeletonLoader type="text" className="h-4 w-3/4 mb-2" />
                                            <SkeletonLoader type="text" className="h-6 w-1/2" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        {[...Array(2)].map((_, i) => (
                            <div key={i} className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="px-6 py-5">
                                    <SkeletonLoader type="text" className="h-5 w-32 mb-4" />
                                    <div className="space-y-3">
                                        {[...Array(2)].map((_, j) => (
                                            <div key={j} className="w-full h-16 skeleton-loader rounded-lg"></div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </main>
            </div>
        );
    }

    const totalProducts = products.length;
    const activeProducts = products.filter(p => p.is_active).length;
    const lowStockProducts = products.filter(p => p.stock_quantity < 10).length;
    const totalCategories = categories.length;

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    <div className="flex items-center space-x-4">
                        <h1 className="text-2xl font-bold text-gray-900">🏪 Owner Dashboard</h1>
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            {user.photo_url && (
                                <R2Image
                                    src={user.photo_url}
                                    alt="Profile"
                                    className="w-8 h-8 rounded-full"
                                />
                            )}
                            <span className="text-gray-700">Welcome, {user.display_name || user.email}</span>
                        </div>
                        <button
                            onClick={onLogout}
                            className="bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                </div>

                {/* Navigation Tabs */}
                <div className="border-t border-gray-200">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <nav className="flex space-x-8">
                            <button
                                onClick={() => setActiveTab('overview')}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'overview'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                Overview
                            </button>
                            <button
                                onClick={() => setActiveTab('products')}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'products'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                Products ({totalProducts})
                            </button>
                            <button
                                onClick={() => setActiveTab('categories')}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'categories'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                Categories ({totalCategories})
                            </button>
                        </nav>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div>
                        {/* Stats Overview */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">📦</span>
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Total Products</dt>
                                                <dd className="text-2xl font-bold text-gray-900">{totalProducts}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">✓</span>
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Active Products</dt>
                                                <dd className="text-2xl font-bold text-gray-900">{activeProducts}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">⚠</span>
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Low Stock</dt>
                                                <dd className="text-2xl font-bold text-gray-900">{lowStockProducts}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                                                <span className="text-white font-bold">📂</span>
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Categories</dt>
                                                <dd className="text-2xl font-bold text-gray-900">{totalCategories}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="px-6 py-5">
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">Quick Actions</h3>
                                    <div className="space-y-3">
                                        <button
                                            onClick={() => setActiveTab('products')}
                                            className="w-full text-left px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                                        >
                                            <div className="font-medium text-blue-900">Manage Products</div>
                                            <div className="text-sm text-blue-700">Add, edit, or remove products</div>
                                        </button>
                                        <button
                                            onClick={() => setActiveTab('categories')}
                                            className="w-full text-left px-4 py-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
                                        >
                                            <div className="font-medium text-green-900">Manage Categories</div>
                                            <div className="text-sm text-green-700">Organize your product categories</div>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200">
                                <div className="px-6 py-5">
                                    <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Products</h3>
                                    <div className="space-y-3">
                                        {products.slice(0, 3).map((product) => (
                                            <div key={product.id} className="flex items-center space-x-3">
                                                {product.image_url ? (
                                                    <R2Image
                                                        src={product.image_url}
                                                        alt={product.name}
                                                        className="h-10 w-10 rounded-lg object-cover"
                                                    />
                                                ) : (
                                                    <div className="h-10 w-10 bg-gray-100 rounded-lg flex items-center justify-center">
                                                        <span className="text-gray-500 text-xs">📦</span>
                                                    </div>
                                                )}
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-medium text-gray-900 truncate">{product.name}</p>
                                                    <p className="text-sm text-gray-500">₹{product.price}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Products Tab */}
                {activeTab === 'products' && (
                    <div>
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold text-gray-900">Products Management</h2>
                            <button
                                onClick={() => window.location.href = '/dashboard/products'}
                                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                            >
                                + Add Product
                            </button>
                        </div>

                        <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Product
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Category
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Price
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Stock
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Status
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Actions
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {products.map((product) => {
                                            const category = categories.find(c => c.id === product.category_id);
                                            return (
                                                <tr key={product.id} className="hover:bg-gray-50">
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center">
                                                            {product.image_url ? (
                                                                <img
                                                                    className="h-12 w-12 rounded-lg object-cover mr-4"
                                                                    src={product.image_url}
                                                                    alt={product.name}
                                                                    onError={(e) => {
                                                                        const target = e.target as HTMLImageElement;
                                                                        target.src = `https://via.placeholder.com/48x48/f3f4f6/9ca3af?text=${encodeURIComponent(product.name.charAt(0))}`;
                                                                    }}
                                                                />
                                                            ) : (
                                                                <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center mr-4">
                                                                    <span className="text-gray-500">📦</span>
                                                                </div>
                                                            )}
                                                            <div>
                                                                <div className="text-sm font-medium text-gray-900">{product.name}</div>
                                                                <div className="text-sm text-gray-500">{product.description?.substring(0, 50)}...</div>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                                            {category?.name || 'No Category'}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="text-sm text-gray-900">₹{product.price}</div>
                                                        {product.mrp && product.mrp > product.price && (
                                                            <div className="text-sm text-gray-500 line-through">₹{product.mrp}</div>
                                                        )}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className={`text-sm ${product.stock_quantity < 10 ? 'text-red-600 font-medium' : 'text-gray-900'}`}>
                                                            {product.stock_quantity} {product.unit}
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${product.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                            }`}>
                                                            {product.is_active ? 'Active' : 'Inactive'}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                        <div className="flex space-x-2">
                                                            <button className="text-blue-600 hover:text-blue-900">Edit</button>
                                                            <button
                                                                onClick={() => handleDeleteProduct(product.id)}
                                                                className="text-red-600 hover:text-red-900"
                                                            >
                                                                Delete
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}

                {/* Categories Tab */}
                {activeTab === 'categories' && (
                    <div>
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold text-gray-900">Categories Management</h2>
                            <button
                                onClick={() => window.location.href = '/dashboard/categories'}
                                className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                            >
                                + Add Category
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {categories.map((category) => {
                                const categoryProductCount = products.filter(p => p.category_id === category.id).length;
                                return (
                                    <div key={category.id} className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
                                        {category.image_url ? (
                                            <img
                                                src={category.image_url}
                                                alt={category.name}
                                                className="w-full h-32 object-cover"
                                                onError={(e) => {
                                                    const target = e.target as HTMLImageElement;
                                                    target.src = `https://via.placeholder.com/400x128/f3f4f6/9ca3af?text=${encodeURIComponent(category.name)}`;
                                                }}
                                            />
                                        ) : (
                                            <div className="w-full h-32 bg-gray-100 flex items-center justify-center">
                                                <span className="text-4xl">📂</span>
                                            </div>
                                        )}
                                        <div className="p-4">
                                            <h3 className="text-lg font-medium text-gray-900 mb-2">{category.name}</h3>
                                            <p className="text-sm text-gray-500 mb-3">{categoryProductCount} products</p>
                                            <div className="flex items-center justify-between">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${category.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                    }`}>
                                                    {category.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                                <div className="flex space-x-2">
                                                    <button className="text-blue-600 hover:text-blue-900 text-sm">Edit</button>
                                                    <button className="text-red-600 hover:text-red-900 text-sm">Delete</button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}