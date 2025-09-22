'use client';

import { useState } from 'react';
import { signInWithPhoneNumber, ConfirmationResult } from 'firebase/auth';
import { auth, setupRecaptcha } from '@/lib/firebase';
import { authAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function PhoneSignIn() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [confirmationResult, setConfirmationResult] = useState<ConfirmationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSendOTP = async () => {
    try {
      console.log('🚀 Starting phone OTP process...');
      console.log('📞 Phone number:', phoneNumber);

      setIsLoading(true);
      setError(null);

      console.log('📡 Validating with backend first...');
      const backendResponse = await authAPI.sendOTP(phoneNumber);
      console.log('✅ Backend validation successful:', backendResponse.data);

      console.log('🔒 Setting up reCAPTCHA...');
      const recaptchaVerifier = setupRecaptcha('recaptcha-container');

      if (!recaptchaVerifier) {
        throw new Error('Failed to initialize reCAPTCHA');
      }
      console.log('✅ reCAPTCHA setup successful');

      console.log('📤 Sending OTP via Firebase...');
      const confirmation = await signInWithPhoneNumber(auth, phoneNumber, recaptchaVerifier);
      console.log('✅ OTP sent successfully, confirmation ID:', confirmation.verificationId);

      setConfirmationResult(confirmation);
      setStep('otp');
      console.log('🎯 Moved to OTP verification step');
    } catch (error: any) {
      console.error('❌ Send OTP error:', {
        message: error.message,
        code: error.code,
        stack: error.stack
      });
      setError(error.message || 'Failed to send OTP');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!confirmationResult) {
      console.error('❌ No confirmation result available');
      return;
    }

    try {
      console.log('🚀 Starting OTP verification...');
      console.log('🔢 OTP entered:', otp);

      setIsLoading(true);
      setError(null);

      console.log('✅ Confirming OTP with Firebase...');
      const result = await confirmationResult.confirm(otp);
      console.log('✅ OTP confirmed successfully:', {
        uid: result.user.uid,
        phoneNumber: result.user.phoneNumber
      });

      console.log('🔑 Getting ID token from phone auth...');
      const idToken = await result.user.getIdToken();
      console.log('✅ ID token obtained, length:', idToken.length);

      console.log('📡 Sending verification to backend...');
      const response = await authAPI.verifyOTP(phoneNumber, otp, idToken);
      console.log('✅ Backend verification successful:', response.data);

      console.log('🎯 Redirecting to dashboard...');
      router.push('/dashboard');
    } catch (error: any) {
      console.error('❌ Verify OTP error:', {
        message: error.message,
        code: error.code,
        stack: error.stack
      });
      setError(error.message || 'Failed to verify OTP');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {step === 'phone' ? (
        <>
          <input
            type="tel"
            placeholder="Phone number (+1234567890)"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            className="w-full p-2 border rounded"
            disabled={isLoading}
          />
          <button
            onClick={handleSendOTP}
            disabled={isLoading || !phoneNumber.trim()}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Sending OTP...' : 'Send OTP'}
          </button>
        </>
      ) : (
        <>
          <input
            type="text"
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            className="w-full p-2 border rounded"
            disabled={isLoading}
          />
          <button
            onClick={handleVerifyOTP}
            disabled={isLoading || !otp.trim()}
            className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Verifying...' : 'Verify OTP'}
          </button>
          <button
            onClick={() => setStep('phone')}
            disabled={isLoading}
            className="w-full bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 disabled:opacity-50"
          >
            Back to Phone Number
          </button>
        </>
      )}
      {error && (
        <div className="text-red-500 text-sm mt-2 p-3 bg-red-50 rounded border border-red-200">
          <div className="font-semibold mb-1">Error:</div>
          <div className="whitespace-pre-wrap">{error}</div>
        </div>
      )}
      <div id="recaptcha-container"></div>
    </div>
  );
}