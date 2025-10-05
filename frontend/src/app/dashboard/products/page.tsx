'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { productAPI, Product, Category } from '@/lib/productApi';
import { authAPI } from '@/lib/api';
import SkeletonLoader from '@/components/SkeletonLoader';
import R2Image from '@/components/ui/R2Image';

export default function ProductsPage() {
    const router = useRouter();
    const [user, setUser] = useState<any>(null);
    const [products, setProducts] = useState<Product[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [editingProduct, setEditingProduct] = useState<Product | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        price: '',
        mrp: '',
        category_id: '',
        stock_quantity: '',
        unit: '',
    });
    const [imageFile, setImageFile] = useState<File | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Get current user
                const userResponse = await authAPI.getCurrentUser();
                setUser(userResponse.data);

                // Fetch products and categories
                const [productsResponse, categoriesResponse] = await Promise.all([
                    productAPI.getProducts(),
                    productAPI.getCategories()
                ]);

                setProducts(productsResponse);
                setCategories(categoriesResponse);
                setLoading(false);
            } catch (err: any) {
                console.error('Error fetching data:', err);
                setError('Failed to load products data');
                setLoading(false);

                // If unauthorized, redirect to login
                if (err.response?.status === 401) {
                    router.push('/');
                }
            }
        };

        fetchData();
    }, [router]);

    const handleLogout = async () => {
        try {
            await authAPI.logout();
            router.push('/');
        } catch (err) {
            console.error('Logout error:', err);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setImageFile(e.target.files[0]);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            // Create FormData for file upload
            const formDataObj = new FormData();
            formDataObj.append('name', formData.name);
            formDataObj.append('description', formData.description);
            formDataObj.append('price', formData.price);

            if (formData.mrp) {
                formDataObj.append('mrp', formData.mrp);
            }

            formDataObj.append('category_id', formData.category_id);

            if (formData.stock_quantity) {
                formDataObj.append('stock_quantity', formData.stock_quantity);
            }

            if (formData.unit) {
                formDataObj.append('unit', formData.unit);
            }

            if (imageFile) {
                formDataObj.append('image', imageFile);
            }

            if (editingProduct) {
                // Update existing product
                const updatedProduct = await productAPI.updateProduct(editingProduct.id, formDataObj);
                // Update the product in the local state
                setProducts(products.map(p => p.id === updatedProduct.id ? updatedProduct : p));
            } else {
                // Create new product
                const newProduct = await productAPI.createProduct(formDataObj);
                // Add the new product to the local state
                setProducts([...products, newProduct]);
            }

            // Reset form
            setFormData({
                name: '',
                description: '',
                price: '',
                mrp: '',
                category_id: '',
                stock_quantity: '',
                unit: '',
            });
            setImageFile(null);
            setShowCreateForm(false);
            setEditingProduct(null);
        } catch (err: any) {
            console.error('Error saving product:', err);
            setError('Failed to save product: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleEdit = (product: Product) => {
        setEditingProduct(product);
        setFormData({
            name: product.name,
            description: product.description || '',
            price: product.price.toString(),
            mrp: product.mrp?.toString() || '',
            category_id: product.category_id.toString(),
            stock_quantity: product.stock_quantity.toString(),
            unit: product.unit || '',
        });
        setShowCreateForm(true);
    };

    const handleDelete = async (id: number) => {
        if (window.confirm('Are you sure you want to delete this product?')) {
            try {
                await productAPI.deleteProduct(id);
                // Remove the product from the local state
                setProducts(products.filter(p => p.id !== id));
            } catch (err: any) {
                console.error('Error deleting product:', err);
                setError('Failed to delete product: ' + (err.response?.data?.detail || err.message));
            }
        }
    };

    const cancelEdit = () => {
        setEditingProduct(null);
        setShowCreateForm(false);
        setFormData({
            name: '',
            description: '',
            price: '',
            mrp: '',
            category_id: '',
            stock_quantity: '',
            unit: '',
        });
        setImageFile(null);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50">
                {/* Header Skeleton */}
                <div className="bg-white shadow">
                    <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
                        <SkeletonLoader type="text" />
                        <div className="flex items-center space-x-4">
                            <SkeletonLoader type="text" />
                            <div className="w-24 h-10 skeleton-loader rounded"></div>
                        </div>
                    </div>
                </div>

                <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                    {/* Action buttons Skeleton */}
                    <div className="mb-6 flex justify-between items-center">
                        <SkeletonLoader type="text" />
                        <div className="w-32 h-10 skeleton-loader rounded"></div>
                    </div>

                    {/* Create/Edit Form Skeleton */}
                    {showCreateForm && (
                        <div className="bg-white shadow rounded-lg p-6 mb-8">
                            <div className="h-6 w-1/3 skeleton-loader rounded mb-4"></div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {[...Array(6)].map((_, i) => (
                                    <div key={i}>
                                        <div className="h-4 w-1/4 skeleton-loader rounded mb-2"></div>
                                        <div className="h-10 skeleton-loader rounded"></div>
                                    </div>
                                ))}
                                <div className="md:col-span-2">
                                    <div className="h-4 w-1/4 skeleton-loader rounded mb-2"></div>
                                    <div className="h-24 skeleton-loader rounded"></div>
                                </div>
                                <div className="md:col-span-2">
                                    <div className="h-4 w-1/4 skeleton-loader rounded mb-2"></div>
                                    <div className="h-10 skeleton-loader rounded"></div>
                                </div>
                            </div>
                            <div className="mt-6 flex space-x-3">
                                <div className="w-24 h-10 skeleton-loader rounded"></div>
                                <div className="w-24 h-10 skeleton-loader rounded"></div>
                            </div>
                        </div>
                    )}

                    {/* Products Table Skeleton */}
                    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                        <div className="bg-gray-50 h-12 skeleton-loader"></div>
                        <div className="divide-y divide-gray-200">
                            {[...Array(5)].map((_, i) => (
                                <div key={i} className="px-6 py-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center">
                                            <div className="h-10 w-10 rounded-full skeleton-loader"></div>
                                            <div className="ml-4">
                                                <div className="h-4 w-24 skeleton-loader rounded mb-2"></div>
                                                <div className="h-3 w-32 skeleton-loader rounded"></div>
                                            </div>
                                        </div>
                                        <div className="flex space-x-4">
                                            <div className="w-16 h-6 skeleton-loader rounded"></div>
                                            <div className="w-16 h-6 skeleton-loader rounded"></div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-red-500 text-xl">{error}</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-gray-900">Product Management</h1>
                    <div className="flex items-center space-x-4">
                        <span className="text-gray-700">Welcome, {user?.display_name || user?.email}</span>
                        <button
                            onClick={handleLogout}
                            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                {/* Action buttons */}
                <div className="mb-6 flex justify-between items-center">
                    <h2 className="text-2xl font-bold text-gray-800">Products</h2>
                    <button
                        onClick={() => setShowCreateForm(true)}
                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    >
                        Add New Product
                    </button>
                </div>

                {/* Create/Edit Form */}
                {showCreateForm && (
                    <div className="bg-white shadow rounded-lg p-6 mb-8">
                        <h3 className="text-xl font-bold mb-4">
                            {editingProduct ? 'Edit Product' : 'Create New Product'}
                        </h3>
                        <form onSubmit={handleSubmit}>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Name *
                                    </label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Category *
                                    </label>
                                    <select
                                        name="category_id"
                                        value={formData.category_id}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="">Select a category</option>
                                        {categories.map(category => (
                                            <option key={category.id} value={category.id}>
                                                {category.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Price *
                                    </label>
                                    <input
                                        type="number"
                                        name="price"
                                        value={formData.price}
                                        onChange={handleInputChange}
                                        step="0.01"
                                        min="0"
                                        required
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        MRP
                                    </label>
                                    <input
                                        type="number"
                                        name="mrp"
                                        value={formData.mrp}
                                        onChange={handleInputChange}
                                        step="0.01"
                                        min="0"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Stock Quantity
                                    </label>
                                    <input
                                        type="number"
                                        name="stock_quantity"
                                        value={formData.stock_quantity}
                                        onChange={handleInputChange}
                                        min="0"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Unit
                                    </label>
                                    <input
                                        type="text"
                                        name="unit"
                                        value={formData.unit}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Description
                                    </label>
                                    <textarea
                                        name="description"
                                        value={formData.description}
                                        onChange={handleInputChange}
                                        rows={3}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Product Image
                                    </label>
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleImageChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                            </div>

                            <div className="mt-6 flex space-x-3">
                                <button
                                    type="submit"
                                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                                >
                                    {editingProduct ? 'Update Product' : 'Create Product'}
                                </button>
                                <button
                                    type="button"
                                    onClick={cancelEdit}
                                    className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                )}

                {/* Products Table */}
                <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Product
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Category
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Price
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Stock
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {products.map((product) => (
                                <tr key={product.id}>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            {product.image_url ? (
                                                <R2Image className="h-10 w-10 rounded-full" src={product.image_url} alt={product.name} />
                                            ) : (
                                                <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                                                    <span className="text-gray-500">No Image</span>
                                                </div>
                                            )}
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-gray-900">{product.name}</div>
                                                <div className="text-sm text-gray-500">{product.description}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">
                                            {categories.find(c => c.id === product.category_id)?.name || 'N/A'}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">₹{product.price.toFixed(2)}</div>
                                        {product.mrp && product.mrp > product.price && (
                                            <div className="text-sm text-gray-500 line-through">₹{product.mrp.toFixed(2)}</div>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">{product.stock_quantity}</div>
                                        {product.unit && (
                                            <div className="text-sm text-gray-500">{product.unit}</div>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {product.is_active ? (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                Active
                                            </span>
                                        ) : (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                                                Inactive
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button
                                            onClick={() => handleEdit(product)}
                                            className="text-blue-600 hover:text-blue-900 mr-3"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleDelete(product.id)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {products.length === 0 && (
                        <div className="text-center py-8">
                            <p className="text-gray-500">No products found</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}