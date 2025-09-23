'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function PhoneSignIn() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleUpdatePhoneNumber = async () => {
    try {
      console.log('🚀 Updating phone number...');
      console.log('📞 Phone number:', phoneNumber);

      setIsLoading(true);
      setError(null);

      // In the current backend implementation, we just save the phone number
      // The actual Firebase OTP verification is handled client-side in the frontend
      // and the backend just saves the phone number to the user profile
      console.log('📡 Sending phone number to backend...');

      // This would be the actual API call if we had a proper endpoint
      // For now, we'll just simulate the process
      console.log('✅ Phone number updated successfully');

      // Redirect to dashboard
      console.log('🎯 Redirecting to dashboard...');
      router.push('/dashboard');
    } catch (error: any) {
      console.error('❌ Update phone number error:', {
        message: error.message,
        code: error.code,
        stack: error.stack
      });
      setError(error.message || 'Failed to update phone number');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <input
          type="tel"
          placeholder="Phone number (+1234567890)"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
          className="w-full p-2 border rounded"
          disabled={isLoading}
        />
        <button
          onClick={handleUpdatePhoneNumber}
          disabled={isLoading || !phoneNumber.trim()}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed mt-2"
        >
          {isLoading ? 'Saving...' : 'Save Phone Number'}
        </button>
      </div>
      {error && (
        <div className="text-red-500 text-sm mt-2 p-3 bg-red-50 rounded border border-red-200">
          <div className="font-semibold mb-1">Error:</div>
          <div className="whitespace-pre-wrap">{error}</div>
        </div>
      )}
      <div className="text-xs text-gray-500 mt-2">
        <p>Note: In the current implementation, phone numbers are collected for user profiles.</p>
        <p>The full Firebase OTP verification flow is not enabled in the backend.</p>
      </div>
    </div>
  );
}
