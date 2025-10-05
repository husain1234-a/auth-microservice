'use client';

import { useEffect, useState } from 'react';
import { productAPI, Product, Category } from '@/lib/productApi';
import Link from 'next/link';
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

interface AdminDashboardProps {
    user: User;
    onLogout: () => void;
}

export default function AdminDashboard({ user, onLogout }: AdminDashboardProps) {
    const [products, setProducts] = useState<Product[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Updated to properly handle the direct array responses from the API
                const productsResponse = await productAPI.getProducts({ limit: 10 });
                const categoriesResponse = await productAPI.getCategories({ limit: 10 });

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

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50">
                {/* Header Skeleton */}
                <div className="bg-white shadow">
                    <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
                        <SkeletonLoader type="text" className="h-8 w-64" />
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <div className="w-8 h-8 rounded-full skeleton-loader"></div>
                                <SkeletonLoader type="text" className="h-4 w-32" />
                            </div>
                            <div className="w-24 h-10 skeleton-loader rounded"></div>
                        </div>
                    </div>
                </div>

                <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                    {/* Stats Overview Skeleton */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
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

                    {/* Management Cards Skeleton */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="px-4 py-5 sm:p-6">
                                    <SkeletonLoader type="text" className="h-5 w-3/4 mb-4" />
                                    <SkeletonLoader type="text" className="h-4 w-full mb-6" />
                                    <div className="w-32 h-10 skeleton-loader rounded"></div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* System Overview Skeleton */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        {[...Array(2)].map((_, i) => (
                            <div key={i} className="bg-white shadow overflow-hidden sm:rounded-lg">
                                <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                                    <div>
                                        <SkeletonLoader type="text" className="h-5 w-40 mb-2" />
                                        <SkeletonLoader type="text" className="h-4 w-64" />
                                    </div>
                                    <div className="w-16 h-6 skeleton-loader rounded"></div>
                                </div>
                                <div className="border-t border-gray-200">
                                    <div className="divide-y divide-gray-200">
                                        {[...Array(3)].map((_, j) => (
                                            <div key={j} className="px-4 py-4">
                                                <div className="flex items-center space-x-4">
                                                    <div className="h-10 w-10 rounded-full skeleton-loader"></div>
                                                    <div className="flex-1 min-w-0">
                                                        <SkeletonLoader type="text" className="h-4 w-32 mb-2" />
                                                        <SkeletonLoader type="text" className="h-4 w-16" />
                                                    </div>
                                                    <div className="text-right">
                                                        <SkeletonLoader type="text" className="h-4 w-24 mb-2" />
                                                        <div className="w-16 h-6 skeleton-loader rounded-full"></div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Admin Profile Section Skeleton */}
                    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                        <div className="px-4 py-5 sm:px-6">
                            <SkeletonLoader type="text" className="h-5 w-48 mb-2" />
                            <SkeletonLoader type="text" className="h-4 w-64" />
                        </div>
                        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                            <div className="sm:divide-y sm:divide-gray-200">
                                {[...Array(5)].map((_, i) => (
                                    <div key={i} className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                        <SkeletonLoader type="text" className="h-4 w-32" />
                                        <div className="mt-1 sm:mt-0 sm:col-span-2">
                                            <SkeletonLoader type="text" className="h-4 w-48" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
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
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
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
                            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                {/* Stats Overview */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white overflow-hidden shadow rounded-lg">
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
                                        <dd className="text-lg font-medium text-gray-900">{totalProducts}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow rounded-lg">
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
                                        <dd className="text-lg font-medium text-gray-900">{activeProducts}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow rounded-lg">
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
                                        <dd className="text-lg font-medium text-gray-900">{lowStockProducts}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                                        <span className="text-white font-bold">👥</span>
                                    </div>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                                        <dd className="text-lg font-medium text-gray-900">--</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Management Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {/* Products Card */}
                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-2">Product Management</h3>
                            <p className="text-gray-500 mb-4">
                                Full control over all products in the system.
                            </p>
                            <Link
                                href="/dashboard/products"
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Manage Products
                            </Link>
                        </div>
                    </div>

                    {/* Categories Card */}
                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-2">Category Management</h3>
                            <p className="text-gray-500 mb-4">
                                Organize and manage product categories.
                            </p>
                            <Link
                                href="/dashboard/categories"
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                            >
                                Manage Categories
                            </Link>
                        </div>
                    </div>

                    {/* User Management Card */}
                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-2">User Management</h3>
                            <p className="text-gray-500 mb-4">
                                Manage user accounts and roles.
                            </p>
                            <button
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                                onClick={() => alert('User management coming soon!')}
                            >
                                Manage Users
                            </button>
                        </div>
                    </div>
                </div>

                {/* System Overview */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    {/* Recent Products */}
                    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                            <div>
                                <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Products</h3>
                                <p className="mt-1 max-w-2xl text-sm text-gray-500">Latest products in the system.</p>
                            </div>
                            <Link
                                href="/dashboard/products"
                                className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                            >
                                View All
                            </Link>
                        </div>
                        <div className="border-t border-gray-200">
                            <ul className="divide-y divide-gray-200">
                                {products.slice(0, 5).map((product) => (
                                    <li key={product.id} className="px-4 py-4">
                                        <div className="flex items-center space-x-4">
                                            {product.image_url && (
                                                <R2Image className="h-10 w-10 rounded-full object-cover" src={product.image_url} alt={product.name} />
                                            )}
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium text-gray-900 truncate">{product.name}</p>
                                                <p className="text-sm text-gray-500">₹{product.price}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm text-gray-900">{product.stock_quantity} in stock</p>
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${product.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                    }`}>
                                                    {product.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Categories Overview */}
                    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                            <div>
                                <h3 className="text-lg leading-6 font-medium text-gray-900">Categories</h3>
                                <p className="mt-1 max-w-2xl text-sm text-gray-500">Product categories overview.</p>
                            </div>
                            <Link
                                href="/dashboard/categories"
                                className="text-green-600 hover:text-green-900 text-sm font-medium"
                            >
                                View All
                            </Link>
                        </div>
                        <div className="border-t border-gray-200">
                            <ul className="divide-y divide-gray-200">
                                {categories.slice(0, 5).map((category) => (
                                    <li key={category.id} className="px-4 py-4">
                                        <div className="flex items-center space-x-4">
                                            {category.image_url && (
                                                <R2Image className="h-10 w-10 rounded-full object-cover" src={category.image_url} alt={category.name} />
                                            )}
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium text-gray-900 truncate">{category.name}</p>
                                                <p className="text-sm text-gray-500">
                                                    {products.filter(p => p.category_id === category.id).length} products
                                                </p>
                                            </div>
                                            <div>
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${category.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                    }`}>
                                                    {category.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Admin Profile Section */}
                <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                    <div className="px-4 py-5 sm:px-6">
                        <h3 className="text-lg leading-6 font-medium text-gray-900">Administrator Profile</h3>
                        <p className="mt-1 max-w-2xl text-sm text-gray-500">System administrator account information.</p>
                    </div>
                    <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                        <dl className="sm:divide-y sm:divide-gray-200">
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Full name</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    {user.display_name || 'N/A'}
                                </dd>
                            </div>
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Email address</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    {user.email || 'N/A'}
                                </dd>
                            </div>
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Phone number</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    {user.phone_number || 'Not provided'}
                                </dd>
                            </div>
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Role</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                        System Administrator
                                    </span>
                                </dd>
                            </div>
                            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt className="text-sm font-medium text-gray-500">Permissions</dt>
                                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    Full system access, user management, product management, category management
                                </dd>
                            </div>
                        </dl>
                    </div>
                </div>
            </main>
        </div>
    );
}