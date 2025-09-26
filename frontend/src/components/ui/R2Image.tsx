'use client';

import { useState } from 'react';

interface R2ImageProps {
    src: string;
    alt: string;
    className?: string;
    fallbackText?: string;
    onLoad?: () => void;
    onError?: () => void;
}

export default function R2Image({
    src,
    alt,
    className = "",
    fallbackText,
    onLoad,
    onError
}: R2ImageProps) {
    const [imageError, setImageError] = useState(false);
    const [imageLoading, setImageLoading] = useState(true);

    const handleImageLoad = () => {
        setImageLoading(false);
        setImageError(false);
        onLoad?.();
    };

    const handleImageError = () => {
        setImageLoading(false);
        setImageError(true);
        onError?.();
        console.warn(`Failed to load image: ${src}`);
    };

    // If image failed to load, show fallback
    if (imageError) {
        return (
            <div className={`bg-gray-100 flex items-center justify-center ${className}`}>
                <div className="text-center p-4">
                    <div className="text-4xl mb-2">📦</div>
                    <div className="text-sm text-gray-500">
                        {fallbackText || alt || 'Image not available'}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`relative ${className}`}>
            {imageLoading && (
                <div className="absolute inset-0 skeleton-loader skeleton-image rounded"></div>
            )}
            <img
                src={src}
                alt={alt}
                className={`${className} ${imageLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
                onLoad={handleImageLoad}
                onError={handleImageError}
                crossOrigin="anonymous"
                referrerPolicy="no-referrer"
            />
        </div>
    );
}