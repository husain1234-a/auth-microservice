'use client';

import React from 'react';

interface SkeletonLoaderProps {
    type?: 'product' | 'category' | 'cartItem' | 'profile' | 'text' | 'tableRow' | 'form';
    count?: number;
    className?: string;
}

export default function SkeletonLoader({ type = 'product', count = 1, className = '' }: SkeletonLoaderProps) {
    const renderSkeleton = () => {
        switch (type) {
            case 'product':
                return (
                    <div className={`bg-white rounded-lg shadow-md overflow-hidden ${className}`}>
                        <div className="w-full h-48 skeleton-loader"></div>
                        <div className="p-4">
                            <div className="h-6 skeleton-loader rounded mb-2"></div>
                            <div className="h-4 skeleton-loader rounded mb-3"></div>
                            <div className="h-4 skeleton-loader rounded w-1/2 mb-3"></div>
                            <div className="h-4 skeleton-loader rounded w-1/3 mb-4"></div>
                            <div className="flex space-x-2">
                                <div className="h-8 flex-1 skeleton-loader rounded"></div>
                                <div className="h-8 w-10 skeleton-loader rounded"></div>
                            </div>
                        </div>
                    </div>
                );

            case 'category':
                return (
                    <div className={`px-4 py-2 rounded-full skeleton-loader ${className}`}></div>
                );

            case 'cartItem':
                return (
                    <div className={`p-6 ${className}`}>
                        <div className="flex items-center">
                            <div className="flex-shrink-0 w-24 h-24 skeleton-loader rounded-md"></div>
                            <div className="ml-4 flex-1">
                                <div className="h-6 skeleton-loader rounded mb-2"></div>
                                <div className="h-4 skeleton-loader rounded w-1/2 mb-4"></div>
                                <div className="flex items-center justify-between">
                                    <div className="h-4 skeleton-loader rounded w-16"></div>
                                    <div className="h-4 skeleton-loader rounded w-16"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                );

            case 'profile':
                return (
                    <div className={className}>
                        <div className="h-6 skeleton-loader rounded mb-4"></div>
                        <div className="space-y-4">
                            {[...Array(4)].map((_, i) => (
                                <div key={i} className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4">
                                    <div className="h-4 skeleton-loader rounded sm:col-span-1"></div>
                                    <div className="h-4 skeleton-loader rounded sm:col-span-2 mt-1 sm:mt-0"></div>
                                </div>
                            ))}
                        </div>
                    </div>
                );

            case 'text':
                return (
                    <div className={`h-4 skeleton-loader rounded ${className}`}></div>
                );

            case 'tableRow':
                return (
                    <div className={`px-6 py-4 ${className}`}>
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
                );

            case 'form':
                return (
                    <div className={className}>
                        <div className="h-6 w-1/3 skeleton-loader rounded mb-4"></div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {[...Array(4)].map((_, i) => (
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
                );

            default:
                return null;
        }
    };

    return (
        <>
            {[...Array(count)].map((_, index) => (
                <div key={index} className="skeleton-loader">
                    {renderSkeleton()}
                </div>
            ))}
        </>
    );
}