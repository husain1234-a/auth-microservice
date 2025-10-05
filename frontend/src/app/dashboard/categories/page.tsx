'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { productAPI, Category } from '@/lib/productApi';
import { authAPI } from '@/lib/api';
import SkeletonLoader from '@/components/SkeletonLoader';
import R2Image from '@/components/ui/R2Image';

export default function CategoriesPage() {
    const router = useRouter();
    const [user, setUser] = useState<any>(null);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [editingCategory, setEditingCategory] = useState<Category | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        name: '',
        description: '',
    });
    const [imageFile, setImageFile] = useState<File | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Get current user
                const userResponse = await authAPI.getCurrentUser();
                setUser(userResponse.data);

                // Fetch categories
                const categoriesResponse = await productAPI.getCategories();
                setCategories(categoriesResponse);
                setLoading(false);
            } catch (err: any) {
                console.error('Error fetching data:', err);
                setError('Failed to load categories data');
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

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
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

            if (imageFile) {
                formDataObj.append('image', imageFile);
            }

            if (editingCategory) {
                // Update existing category
                const updatedCategory = await productAPI.updateCategory(editingCategory.id, formDataObj);
                // Update the category in the local state
                setCategories(categories.map(c => c.id === updatedCategory.id ? updatedCategory : c));
            } else {
                // Create new category
                const newCategory = await productAPI.createCategory(formDataObj);
                // Add the new category to the local state
                setCategories([...categories, newCategory]);
            }

            // Reset form
            setFormData({ name: '', description: '' });
            setImageFile(null);
            setShowCreateForm(false);
            setEditingCategory(null);
        } catch (err: any) {
            console.error('Error saving category:', err);
            setError('Failed to save category: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleEdit = (category: Category) => {
        setEditingCategory(category);
        setFormData({
            name: category.name,
            description: category.description || '',
        });
        setShowCreateForm(true);
    };

    const handleDelete = async (id: number) => {
        if (window.confirm('Are you sure you want to delete this category? This will affect all products in this category.')) {
            try {
                // We'll implement soft delete by setting is_active to false
                const formDataObj = new FormData();
                formDataObj.append('is_active', 'false');
                const updatedCategory = await productAPI.updateCategory(id, formDataObj);
                // Update the category in the local state
                setCategories(categories.map(c => c.id === updatedCategory.id ? updatedCategory : c));
            } catch (err: any) {
                console.error('Error deleting category:', err);
                setError('Failed to delete category: ' + (err.response?.data?.detail || err.message));
            }
        }
    };

    const handleToggleActive = async (id: number) => {
        try {
            const category = categories.find(c => c.id === id);
            if (!category) return;

            const formDataObj = new FormData();
            formDataObj.append('is_active', (!category.is_active).toString());
            const updatedCategory = await productAPI.updateCategory(id, formDataObj);
            // Update the category in the local state
            setCategories(categories.map(c => c.id === updatedCategory.id ? updatedCategory : c));
        } catch (err: any) {
            console.error('Error toggling category status:', err);
            setError('Failed to update category: ' + (err.response?.data?.detail || err.message));
        }
    };

    const cancelEdit = () => {
        setEditingCategory(null);
        setShowCreateForm(false);
        setFormData({ name: '', description: '' });
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
                                <div>
                                    <div className="h-4 w-1/4 skeleton-loader rounded mb-2"></div>
                                    <div className="h-10 skeleton-loader rounded"></div>
                                </div>
                                <div>
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

                    {/* Categories Table Skeleton */}
                    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                        <div className="bg-gray-50 h-12 skeleton-loader"></div>
                        <div className="divide-y divide-gray-200">
                            {[...Array(5)].map((_, i) => (
                                <div key={i} className="px-6 py-4">
                                    <div className="flex items-center justify-between">
                                        <div className="h-4 w-1/4 skeleton-loader rounded"></div>
                                        <div className="h-10 w-10 rounded skeleton-loader"></div>
                                        <div className="w-16 h-6 skeleton-loader rounded"></div>
                                        <div className="flex space-x-2">
                                            <div className="w-12 h-6 skeleton-loader rounded"></div>
                                            <div className="w-12 h-6 skeleton-loader rounded"></div>
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
                    <h1 className="text-3xl font-bold text-gray-900">Category Management</h1>
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
                    <h2 className="text-2xl font-bold text-gray-800">Categories</h2>
                    <button
                        onClick={() => setShowCreateForm(true)}
                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    >
                        Add New Category
                    </button>
                </div>

                {/* Create/Edit Form */}
                {showCreateForm && (
                    <div className="bg-white shadow rounded-lg p-6 mb-8">
                        <h3 className="text-xl font-bold mb-4">
                            {editingCategory ? 'Edit Category' : 'Create New Category'}
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
                                        Category Image
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
                                    {editingCategory ? 'Update Category' : 'Create Category'}
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

                {/* Categories Table */}
                <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Category
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Image
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
                            {categories.map((category) => (
                                <tr key={category.id}>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">{category.name}</div>
                                        {category.description && (
                                            <div className="text-sm text-gray-500">{category.description}</div>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {category.image_url ? (
                                            <R2Image className="h-10 w-10 rounded" src={category.image_url} alt={category.name} />
                                        ) : (
                                            <div className="h-10 w-10 rounded bg-gray-200 flex items-center justify-center">
                                                <span className="text-gray-500 text-xs">No Image</span>
                                            </div>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {category.is_active ? (
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
                                            onClick={() => handleEdit(category)}
                                            className="text-blue-600 hover:text-blue-900 mr-3"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleToggleActive(category.id)}
                                            className={category.is_active
                                                ? "text-red-600 hover:text-red-900"
                                                : "text-green-600 hover:text-green-900"}
                                        >
                                            {category.is_active ? 'Deactivate' : 'Activate'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {categories.length === 0 && (
                        <div className="text-center py-8">
                            <p className="text-gray-500">No categories found</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}