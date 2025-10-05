'use client';

import { useState } from 'react';
import { signInWithPopup, signInWithRedirect, getRedirectResult } from 'firebase/auth';
import { auth, googleProvider } from '@/lib/firebase';
import { authAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';

export default function GoogleSignIn() {
  const router = useRouter();
  const { login } = useUser();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [usePopup, setUsePopup] = useState(true);

  const handleGoogleSignIn = async () => {
    try {
      console.log('🚀 Starting Google sign-in process...');
      console.log('📱 Using popup method:', usePopup);

      setIsLoading(true);
      setError(null);

      let result;

      if (usePopup) {
        console.log('🔄 Attempting popup sign-in...');
        try {
          result = await signInWithPopup(auth, googleProvider);
          console.log('✅ Popup sign-in successful:', result.user.uid);
        } catch (popupError: any) {
          console.warn('⚠️ Popup sign-in failed, falling back to redirect:', popupError.message);

          // Fall back to redirect if popup fails
          console.log('🔄 Switching to redirect method...');
          await signInWithRedirect(auth, googleProvider);
          // The redirect will handle the rest
          return;
        }
      } else {
        console.log('🔄 Using redirect sign-in...');
        await signInWithRedirect(auth, googleProvider);
        // The redirect will handle the rest
        return;
      }

      if (result?.user) {
        const idToken = await result.user.getIdToken();
        const response = await authAPI.googleLogin(idToken);

        // Update UserContext with the logged-in user data
        login(response.data.user);

        // Check if user has phone number, if not redirect to phone collection
        if (!response.data.user.phone_number) {
          router.push('/collect-phone');
        } else {
          router.push('/dashboard');
        }
      }
    } catch (error: any) {
      console.error('❌ Google sign-in error:', {
        message: error.message,
        code: error.code,
        stack: error.stack
      });
      setError(error.message || 'Failed to sign in with Google');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>Authentication method:</span>
        <button
          onClick={() => setUsePopup(!usePopup)}
          className="text-blue-600 hover:text-blue-700 underline"
          type="button"
        >
          {usePopup ? 'Switch to Redirect' : 'Switch to Popup'}
        </button>
      </div>

      <button
        onClick={handleGoogleSignIn}
        disabled={isLoading}
        className="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          usePopup ? 'Opening Google Popup...' : 'Redirecting to Google...'
        ) : (
          `Sign in with Google (${usePopup ? 'Popup' : 'Redirect'})`
        )}
      </button>

      {error && (
        <div className="text-red-500 text-sm mt-2 p-2 bg-red-50 rounded">
          <div className="font-semibold">Error:</div>
          <div>{error}</div>
        </div>
      )}
    </div>
  );
}