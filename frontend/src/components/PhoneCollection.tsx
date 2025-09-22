'use client';

import { useState } from 'react';
import { authAPI } from '@/lib/api';

interface PhoneCollectionProps {
    user: any;
    onComplete: (phoneNumber: string) => void;
    onSkip: () => void;
}

export default function PhoneCollection({ user, onComplete, onSkip }: PhoneCollectionProps) {
    const [phoneNumber, setPhoneNumber] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showConfirmation, setShowConfirmation] = useState(false);

    const handleSubmit = async () => {
        try {
            console.log('🚀 Saving phone number for first-time user...');
            console.log('📞 Phone number:', phoneNumber);

            setIsLoading(true);
            setError(null);

            // Validate phone number format
            const phoneRegex = /^\+[1-9]\d{1,14}$/;
            if (!phoneRegex.test(phoneNumber)) {
                throw new Error('Please enter a valid phone number in international format (e.g., +1234567890)');
            }

            // Show confirmation popup
            setShowConfirmation(true);
        } catch (error: any) {
            console.error('❌ Phone number validation error:', {
                message: error.message,
                code: error.code,
                stack: error.stack
            });
            setError(error.message || 'Please enter a valid phone number');
        } finally {
            setIsLoading(false);
        }
    };

    const handleConfirm = async () => {
        try {
            console.log('📡 User confirmed phone number, saving to backend...');

            setIsLoading(true);
            setError(null);

            const updateResponse = await authAPI.updatePhoneNumber(phoneNumber);
            console.log('✅ Phone number saved to backend:', updateResponse.data);

            console.log('🎯 Phone number collection completed, redirecting to dashboard...');
            onComplete(phoneNumber);
        } catch (error: any) {
            console.error('❌ Save phone number error:', {
                message: error.message,
                code: error.code,
                stack: error.stack
            });
            setError(error.message || 'Failed to save phone number');
            setShowConfirmation(false);
        } finally {
            setIsLoading(false);
        }
    };

    const handleEdit = () => {
        setShowConfirmation(false);
        setError(null);
    };

    if (showConfirmation) {
        return (
            <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
                <div className="text-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">
                        Confirm Your Phone Number
                    </h2>
                    <p className="text-sm text-gray-600 mt-2">
                        Please confirm your phone number is correct
                    </p>
                </div>

                {/* Confirmation Display */}
                <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-6 text-center">
                    <div className="text-blue-800 font-semibold mb-2">📱 Your Phone Number:</div>
                    <div className="text-blue-900 text-lg font-mono bg-white p-2 rounded border">
                        {phoneNumber}
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex space-x-3">
                        <button
                            onClick={handleConfirm}
                            disabled={isLoading}
                            className="flex-1 bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                        >
                            {isLoading ? 'Saving...' : '✅ Confirm & Save'}
                        </button>

                        <button
                            onClick={handleEdit}
                            disabled={isLoading}
                            className="flex-1 bg-gray-500 text-white py-3 px-4 rounded-lg hover:bg-gray-600 disabled:opacity-50 font-semibold"
                        >
                            ✏️ Edit Number
                        </button>
                    </div>

                    <div className="text-center">
                        <button
                            onClick={onSkip}
                            disabled={isLoading}
                            className="text-gray-600 hover:text-gray-700 text-sm underline"
                        >
                            Skip for now
                        </button>
                    </div>

                    {error && (
                        <div className="text-red-500 text-sm p-3 bg-red-50 rounded border border-red-200">
                            <div className="font-semibold mb-1">Error:</div>
                            <div className="whitespace-pre-wrap">{error}</div>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
            <div className="text-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                    Add Your Phone Number
                </h2>
                <p className="text-sm text-gray-600 mt-2">
                    Welcome {user.display_name}! Please provide your phone number for your account.
                </p>
            </div>

            {/* Info Notice */}
            <div className="bg-blue-50 border border-blue-200 p-3 rounded mb-4 text-xs">
                <div className="text-blue-800 font-semibold mb-1">📱 One-time Setup:</div>
                <div className="text-blue-700">
                    This is a one-time setup. Once saved, you won't be asked for your phone number again on future logins.
                </div>
            </div>

            <div className="space-y-4">
                <input
                    type="tel"
                    placeholder="Phone number (+1234567890)"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={isLoading}
                />

                <div className="text-xs text-gray-500">
                    Please enter your phone number in international format starting with +
                </div>

                <div className="flex space-x-3">
                    <button
                        onClick={handleSubmit}
                        disabled={isLoading || !phoneNumber.trim()}
                        className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? 'Validating...' : 'Continue'}
                    </button>

                    <button
                        onClick={onSkip}
                        disabled={isLoading}
                        className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 disabled:opacity-50"
                    >
                        Skip for Now
                    </button>
                </div>

                {error && (
                    <div className="text-red-500 text-sm p-3 bg-red-50 rounded border border-red-200">
                        <div className="font-semibold mb-1">Error:</div>
                        <div className="whitespace-pre-wrap">{error}</div>
                    </div>
                )}
            </div>
        </div>
    );
}